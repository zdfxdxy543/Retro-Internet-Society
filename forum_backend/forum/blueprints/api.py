from flask import Blueprint, request, jsonify, make_response
from .base import BasePageView, register_page_route, require_api_key
from ..models import Post, Reply, db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 搜索接口视图类
class SearchView(BasePageView):
    def get_data(self):
        # 获取前端传递的搜索参数
        keyword = request.args.get('keyword', '').strip()
        search_type = request.args.get('type', 'post')  # 默认搜索帖子

        if not keyword:
            return {
                "results": [],
                "keyword": keyword,
                "type": search_type
            }

        # 1. 搜索帖子：模糊匹配标题或内容，关联板块信息
        if search_type == 'post':
            # 使用 LIKE 模糊查询（不区分大小写，适配不同数据库）
            posts = Post.query.filter(
                db.or_(
                    Post.title.ilike(f'%{keyword}%'),
                    Post.content.ilike(f'%{keyword}%')
                )
            ).order_by(Post.create_time.desc()).all()

            results = [{
                "id": post.id,
                "title": post.title,
                "content": post.content[:150] + "..." if len(post.content) > 150 else post.content,  # 截取前150字预览
                "author": post.author,
                "board_id": post.board.id,
                "board_name": post.board.name,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": len(post.replies)
            } for post in posts]

        # 2. 搜索用户：模糊匹配作者名，去重并统计发帖/回帖数
        elif search_type == 'user':
            # 从帖子表和回帖表中查询匹配的作者名（去重）
            post_authors = Post.query.filter(Post.author.ilike(f'%{keyword}%')).with_entities(Post.author).distinct()
            reply_authors = Reply.query.filter(Reply.author.ilike(f'%{keyword}%')).with_entities(Reply.author).distinct()
            
            # 合并去重所有匹配的用户名
            all_authors = set()
            for author in post_authors:
                all_authors.add(author[0])
            for author in reply_authors:
                all_authors.add(author[0])
            all_authors = list(all_authors)

            # 统计每个用户的发帖数和回帖数
            results = []
            for author in all_authors:
                post_count = Post.query.filter_by(author=author).count()
                reply_count = Reply.query.filter_by(author=author).count()
                results.append({
                    "author": author,
                    "post_count": post_count,
                    "reply_count": reply_count
                })

        # 其他类型默认返回空结果
        else:
            results = []

        return {
            "results": results,
            "keyword": keyword,
            "type": search_type
        }

# 注册搜索接口路由
register_page_route(api_bp, "/search", SearchView)

# 大模型生成页面接口（带鉴权）
@api_bp.route("/ai/generate-page", methods=["POST"])
@require_api_key  # 保留原有鉴权装饰器
def ai_generate_page():
    """
    大模型生成动态页面的接口（仅内部/管理员调用）
    请求体：{"title": "页面标题", "content": "HTML/Markdown内容", "content_type": "html", "category": "tech"}
    """
    try:
        # 延迟导入，避免循环依赖
        from ai_page_generator import AIPageGenerator
        
        data = request.get_json()
        # 创建AI页面生成器实例
        ai_generator = AIPageGenerator(db=db, app_config=current_app.config)
        
        # 调用工具类的核心方法，创建动态页面
        page_info = ai_generator.create_dynamic_page(
            title=data.get("title"),
            content=data.get("content"),
            content_type=data.get("content_type", "html"),
            category=data.get("category", "general"),
            is_public=data.get("is_public", True)
        )
        return jsonify({
            "status": "success",
            "data": page_info
        }), 201
    except ValueError as e:
        # 参数校验失败
        return jsonify({"status": "error", "msg": str(e)}), 400
    except SQLAlchemyError as e:
        # 数据库存储失败
        return jsonify({"status": "error", "msg": f"页面生成失败：{str(e)}"}), 500
    except Exception as e:
        # 其他未知异常
        return jsonify({"status": "error", "msg": f"服务器错误：{str(e)}"}), 500

# 为未来API预留扩展空间
# 可以在这里添加更多API路由，或者创建专门的API模块
# 例如：
# @api_bp.route("/other/endpoint", methods=["GET", "POST"])
# def other_endpoint():
#     pass

# 首页数据接口（兼容前端请求）
@api_bp.route("/", methods=["GET"])
def api_index():
    """
    首页数据接口，返回论坛板块信息
    """
    try:
        # 从models导入Board模型
        from ..models import Board, db
        
        # 查询所有板块，按创建时间排序
        boards = Board.query.order_by(Board.create_time.desc()).all()
        
        # 格式化板块数据
        boards_data = []
        for board in boards:
            boards_data.append({
                "id": board.id,
                "name": board.name,
                "description": board.description,
                "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": "GreatGame论坛",
                "boards": boards_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取数据失败：{str(e)}"
        }), 500

# 板块详情接口
@api_bp.route("/board/<int:board_id>", methods=["GET"])
def api_board(board_id):
    """
    板块详情接口，返回板块信息和帖子列表
    """
    try:
        # 从models导入Board和Post模型
        from ..models import Board, Post, Reply, db
        
        # 查询板块信息
        board = Board.query.get_or_404(board_id)
        
        # 查询该板块下的所有帖子
        posts = Post.query.filter_by(board_id=board_id).order_by(Post.create_time.desc()).all()
        
        # 格式化帖子数据
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "author": post.author,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": Reply.query.filter_by(post_id=post.id).count()
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": f"论坛 - {board.name}",
                "board": {
                    "id": board.id,
                    "name": board.name,
                    "description": board.description,
                    "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "posts": posts_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取板块数据失败：{str(e)}"
        }), 500

# 帖子详情接口
@api_bp.route("/post/<int:post_id>", methods=["GET"])
def api_post(post_id):
    """
    帖子详情接口，返回帖子信息和回帖列表
    """
    try:
        # 从models导入Post、Reply和Board模型
        from ..models import Post, Reply, Board, db
        
        # 查询帖子信息
        post = Post.query.get_or_404(post_id)
        
        # 查询该帖子的所有回帖
        replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.create_time.asc()).all()
        
        # 格式化回帖数据
        replies_data = []
        for reply in replies:
            replies_data.append({
                "id": reply.id,
                "author": reply.author,
                "content": reply.content,
                "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "signature": reply.signature
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": post.title,
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "author": post.author,
                    "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "view_count": post.view_count,
                    "board_id": post.board_id,
                    "board_name": post.board.name
                },
                "replies": replies_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取帖子数据失败：{str(e)}"
        }), 500

# 个人页面接口
@api_bp.route("/user/<string:author>", methods=["GET"])
def api_user(author):
    """
    个人页面接口，返回用户信息、发布的帖子和回复的帖子
    """
    try:
        # 从models导入Post、Reply和Board模型
        from ..models import Post, Reply, Board, db
        
        # 查询用户发布的帖子
        posts = Post.query.filter_by(author=author).order_by(Post.create_time.desc()).all()
        
        # 格式化发布的帖子数据
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "author": post.author,
                "board_id": post.board_id,
                "board_name": post.board.name,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": Reply.query.filter_by(post_id=post.id).count()
            })
        
        # 查询用户回复的帖子
        replies = Reply.query.filter_by(author=author).order_by(Reply.create_time.desc()).all()
        
        # 格式化回复的帖子数据
        replies_data = []
        for reply in replies:
            # 获取回复对应的帖子信息
            post = Post.query.get(reply.post_id)
            if post:
                replies_data.append({
                    "id": reply.id,
                    "post_id": reply.post_id,
                    "post_title": post.title,
                    "author": reply.author,
                    "content": reply.content,
                    "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "signature": reply.signature
                })
        
        # 计算用户的发帖数和回帖数
        post_count = len(posts_data)
        reply_count = len(replies_data)
        
        return jsonify({
            "status": "success",
            "data": {
                "title": f"个人主页 - {author}",
                "user_info": {
                    "author": author,
                    "post_count": post_count,
                    "reply_count": reply_count
                },
                "posts": posts_data,
                "replies": replies_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取个人页面数据失败：{str(e)}"
        }), 500



