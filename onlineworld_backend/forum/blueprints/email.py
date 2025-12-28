from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from ..models import db, MailUser, Mail
from datetime import datetime
import re

# 创建邮箱系统蓝图
email_bp = Blueprint('email', __name__, url_prefix='/email')

# ===================== 辅助函数 =====================

def login_required(f):
    """登录装饰器，验证用户是否已登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"success": False, "message": "请先登录"}), 401
        # 将用户信息注入到请求上下文
        user = MailUser.query.get(user_id)
        if user is None:
            session.pop('user_id', None)  # 清除无效的用户ID
            return jsonify({"success": False, "message": "用户不存在或已被删除"}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    """验证邮箱格式是否正确"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_username(username):
    """验证用户名格式是否正确（只允许字母、数字、下划线，长度3-20）"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

# ===================== 用户认证API =====================

@email_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # 参数验证
        if not username or not email or not password:
            return jsonify({"success": False, "message": "用户名、邮箱和密码不能为空"}), 400
            
        if not is_valid_username(username):
            return jsonify({"success": False, "message": "用户名格式不正确，只允许字母、数字、下划线，长度3-20"}), 400
            
        if not is_valid_email(email):
            return jsonify({"success": False, "message": "邮箱格式不正确"}), 400
            
        if len(password) < 6:
            return jsonify({"success": False, "message": "密码长度至少6位"}), 400
        
        # 检查用户名是否已存在
        if MailUser.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "用户名已被使用"}), 409
            
        # 检查邮箱是否已存在
        if MailUser.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "邮箱已被注册"}), 409
        
        # 创建新用户
        hashed_password = generate_password_hash(password)
        new_user = MailUser(
            username=username,
            email=email,
            password=hashed_password,
            display_name=username  # 默认为用户名
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"success": True, "message": "注册成功", "user": new_user.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"注册失败: {str(e)}"}), 500

@email_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # 参数验证
        if not username or not password:
            return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400
        
        # 查找用户
        user = MailUser.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "用户名或密码错误"}), 401
        
        if not user.is_active:
            return jsonify({"success": False, "message": "账户已被禁用"}), 403
        
        # 设置登录状态
        session['user_id'] = user.id
        session.permanent = True  # 设置会话为永久性（需要配置PERMANENT_SESSION_LIFETIME）
        
        return jsonify({"success": True, "message": "登录成功", "user": user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"登录失败: {str(e)}"}), 500

@email_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出接口"""
    try:
        session.pop('user_id', None)
        return jsonify({"success": True, "message": "登出成功"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"登出失败: {str(e)}"}), 500

@email_bp.route('/status', methods=['GET'])
@login_required
def status():
    """获取当前用户登录状态"""
    try:
        user = request.current_user
        return jsonify({"success": True, "message": "已登录", "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"获取状态失败: {str(e)}"}), 500

# ===================== 邮件操作API =====================

@email_bp.route('/send', methods=['POST'])
@login_required
def send_email():
    """发送邮件接口"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # 参数验证
        recipient_email = data.get('recipient_email', '').strip()
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        
        if not recipient_email or not subject or not content:
            return jsonify({"success": False, "message": "收件人邮箱、主题和内容不能为空"}), 400
            
        if not is_valid_email(recipient_email):
            return jsonify({"success": False, "message": "收件人邮箱格式不正确"}), 400
        
        # 查找收件人
        recipient = MailUser.query.filter_by(email=recipient_email).first()
        if not recipient:
            return jsonify({"success": False, "message": "收件人不存在"}), 404
            
        # 不允许给自己发送邮件
        if user.id == recipient.id:
            return jsonify({"success": False, "message": "不能给自己发送邮件"}), 400
            
        # 创建新邮件
        new_mail = Mail(
            sender_id=user.id,
            recipient_id=recipient.id,
            subject=subject,
            content=content
        )
        
        db.session.add(new_mail)
        db.session.commit()
        
        return jsonify({"success": True, "message": "邮件发送成功", "mail": new_mail.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"发送邮件失败: {str(e)}"}), 500

@email_bp.route('/inbox', methods=['GET'])
@login_required
def get_inbox():
    """获取收件箱邮件列表"""
    try:
        user = request.current_user
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_starred = request.args.get('is_starred', None, type=bool)
        is_read = request.args.get('is_read', None, type=bool)
        
        # 构建查询
        query = Mail.query.filter_by(
            recipient_id=user.id,
            is_deleted=False
        )
        
        # 应用过滤条件
        if is_starred is not None:
            query = query.filter_by(is_starred=is_starred)
            
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
            
        # 按时间降序排序并分页
        paginated = query.order_by(Mail.create_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 转换为字典列表
        mails = [mail.to_dict() for mail in paginated.items]
        
        # 统计未读邮件数量
        unread_count = Mail.query.filter_by(
            recipient_id=user.id,
            is_read=False,
            is_deleted=False
        ).count()
        
        return jsonify({
            "success": True,
            "message": "获取收件箱成功",
            "data": mails,
            "total": paginated.total,
            "pages": paginated.pages,
            "page": paginated.page,
            "per_page": paginated.per_page,
            "unread_count": unread_count
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取收件箱失败: {str(e)}"}), 500

@email_bp.route('/outbox', methods=['GET'])
@login_required
def get_outbox():
    """获取发件箱邮件列表"""
    try:
        user = request.current_user
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = Mail.query.filter_by(
            sender_id=user.id,
            is_deleted=False
        )
        
        # 按时间降序排序并分页
        paginated = query.order_by(Mail.create_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 转换为字典列表
        mails = [mail.to_dict() for mail in paginated.items]
        
        return jsonify({
            "success": True,
            "message": "获取发件箱成功",
            "data": mails,
            "total": paginated.total,
            "pages": paginated.pages,
            "page": paginated.page,
            "per_page": paginated.per_page
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取发件箱失败: {str(e)}"}), 500

@email_bp.route('/<int:mail_id>', methods=['GET'])
@login_required
def get_email_detail(mail_id):
    """获取邮件详情"""
    try:
        user = request.current_user
        
        # 查询邮件
        mail = Mail.query.get(mail_id)
        if not mail:
            return jsonify({"success": False, "message": "邮件不存在"}), 404
            
        # 检查权限（只能查看自己发送或接收的邮件）
        if mail.sender_id != user.id and mail.recipient_id != user.id:
            return jsonify({"success": False, "message": "没有权限查看此邮件"}), 403
            
        # 如果是收件人查看，标记为已读
        if mail.recipient_id == user.id and not mail.is_read:
            mail.is_read = True
            db.session.commit()
            
        return jsonify({"success": True, "message": "获取邮件详情成功", "data": mail.to_dict()}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"获取邮件详情失败: {str(e)}"}), 500

@email_bp.route('/<int:mail_id>/mark-read', methods=['PUT'])
@login_required
def mark_email_read(mail_id):
    """标记邮件为已读"""
    try:
        user = request.current_user
        
        # 查询邮件
        mail = Mail.query.get(mail_id)
        if not mail:
            return jsonify({"success": False, "message": "邮件不存在"}), 404
            
        # 只有收件人才能标记已读
        if mail.recipient_id != user.id:
            return jsonify({"success": False, "message": "只有收件人才能标记已读"}), 403
            
        # 标记为已读
        mail.is_read = True
        db.session.commit()
        
        return jsonify({"success": True, "message": "邮件已标记为已读", "data": mail.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"标记失败: {str(e)}"}), 500

@email_bp.route('/<int:mail_id>/mark-starred', methods=['PUT'])
@login_required
def mark_email_starred(mail_id):
    """标记/取消标记邮件星标"""
    try:
        user = request.current_user
        data = request.get_json()
        is_starred = data.get('is_starred', True)
        
        # 查询邮件
        mail = Mail.query.get(mail_id)
        if not mail:
            return jsonify({"success": False, "message": "邮件不存在"}), 404
            
        # 只有收件人才能标记星标
        if mail.recipient_id != user.id:
            return jsonify({"success": False, "message": "只有收件人才能标记星标"}), 403
            
        # 更新星标状态
        mail.is_starred = is_starred
        db.session.commit()
        
        return jsonify({"success": True, "message": f"邮件已{'标记星标' if is_starred else '取消星标'}", "data": mail.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"标记失败: {str(e)}"}), 500

@email_bp.route('/<int:mail_id>/delete', methods=['DELETE'])
@login_required
def delete_email(mail_id):
    """删除邮件（软删除）"""
    try:
        user = request.current_user
        
        # 查询邮件
        mail = Mail.query.get(mail_id)
        if not mail:
            return jsonify({"success": False, "message": "邮件不存在"}), 404
            
        # 检查权限
        is_sender = mail.sender_id == user.id
        is_recipient = mail.recipient_id == user.id
        
        if not is_sender and not is_recipient:
            return jsonify({"success": False, "message": "没有权限删除此邮件"}), 403
            
        # 处理软删除逻辑
        if not mail.is_deleted:
            mail.is_deleted = True
            mail.delete_by = 'sender' if is_sender else 'recipient'
        elif mail.is_deleted:
            # 如果邮件已经被对方删除，那么彻底从数据库中删除
            if ((mail.delete_by == 'sender' and is_recipient) or 
                (mail.delete_by == 'recipient' and is_sender)):
                db.session.delete(mail)
                return jsonify({"success": True, "message": "邮件已彻底删除"}), 200
            # 如果是同一个人再次删除，不做操作
            elif ((mail.delete_by == 'sender' and is_sender) or 
                  (mail.delete_by == 'recipient' and is_recipient)):
                return jsonify({"success": True, "message": "邮件已经在回收站中"}), 200
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "邮件已移至回收站"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"删除邮件失败: {str(e)}"}), 500

# ===================== 用户信息API =====================

@email_bp.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户个人资料"""
    try:
        user = request.current_user
        return jsonify({"success": True, "message": "获取个人资料成功", "data": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"获取个人资料失败: {str(e)}"}), 500

@email_bp.route('/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户个人资料"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # 更新资料（只更新提供的字段）
        if 'display_name' in data:
            user.display_name = data['display_name'].strip()
            
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url'].strip()
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "更新个人资料成功", "data": user.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"更新个人资料失败: {str(e)}"}), 500

@email_bp.route('/user/change-password', methods=['PUT'])
@login_required
def change_password():
    """修改密码"""
    try:
        user = request.current_user
        data = request.get_json()
        
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # 验证旧密码
        if not check_password_hash(user.password, old_password):
            return jsonify({"success": False, "message": "原密码错误"}), 400
            
        # 验证新密码
        if not new_password or len(new_password) < 6:
            return jsonify({"success": False, "message": "新密码不能为空且长度至少为6位"}), 400
            
        # 更新密码
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({"success": True, "message": "密码修改成功"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"修改密码失败: {str(e)}"}), 500

