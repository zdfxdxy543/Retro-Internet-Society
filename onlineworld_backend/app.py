# 添加项目根目录到sys.path，确保模块导入正确
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from config import config
# 从forum.models导入数据库和模型类
from forum.models import db, Board, Post, Reply, PlayerStatus, CompanyInfo, ProductCategory, Product
from datetime import datetime
import os
from flask.views import MethodView  # 导入Flask类视图基类
from forum.ai_page_generator import AIPageGenerator
from sqlalchemy.exc import SQLAlchemyError
import functools

# 创建Flask应用实例
app = Flask(__name__)
app.config.from_object(config)

# 配置应用
app.config["ALLOWED_HTML_TAGS"] = ["div", "p", "h2", "h3", "h4", "ul", "li", "a", "strong", "em", "code", "pre"]
app.config["ALLOWED_HTML_ATTRS"] = {"a": ["href", "target", "rel"], "code": ["class"]}
app.config["API_KEY"] = "your-secret-key-123456"  # 请替换为你的实际密钥（重要！）

# 启用CORS，增加对/email路径的明确支持
CORS(app, origins=['http://localhost:8080'], supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])

# 初始化数据库
import os
app_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(app_root, 'instance', 'forum.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path.replace(chr(92), "/")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
db.init_app(app)

# 确保邮箱系统数据表被创建
with app.app_context():
    db.create_all()

# -------------------------- 导入并注册所有蓝图 --------------------------
# 导入蓝图
from forum.blueprints.forum_pages import forum_bp
from forum.blueprints.api import api_bp
from forum.blueprints.user import user_bp
# 导入company_pages模块，执行其中的路由注册代码
from forum.blueprints.company_pages import api_bp  # 注意：这里不需要导入company_bp，因为路由已经注册到api_bp中
# 导入AI地图模块
from forum.blueprints.ai_map import api_bp  # AI地图路由也注册到api_bp中
# 导入商城模块
from forum.blueprints.shop import shop_bp  # 商城路由注册到shop_bp中
# 导入邮箱模块
from forum.blueprints.email import email_bp  # 邮箱路由注册到email_bp中

# 注册蓝图
app.register_blueprint(forum_bp)  # 论坛页面路由，前缀 /forum
app.register_blueprint(api_bp)     # API路由，前缀 /api
app.register_blueprint(user_bp)    # 用户相关路由，前缀 /user
app.register_blueprint(shop_bp)    # 商城路由，前缀 /shop
app.register_blueprint(email_bp)    # 邮箱路由，前缀 /email
# 移除对company_bp的注册，因为公司网站路由现在已经注册到api_bp中了
# app.register_blueprint(company_bp)  # 公司网站路由，前缀 /company

# 为根路径添加重定向到论坛首页
@app.route('/')
def root():
    from flask import redirect, url_for
    return redirect(url_for('forum.indexview'))  # 重定向到论坛首页，注意端点名称是indexview而不是index

# -------------------------- 数据库初始化（保持不变）--------------------------
@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    # 插入测试数据（和之前完全一致，无修改）
    board1 = Board(name="技术讨论区", description="聊聊编程、网络、硬件相关")
    board2 = Board(name="生活闲聊区", description="分享日常、八卦、求助")
    db.session.add_all([board1, board2])
    db.session.commit()

    post1 = Post(
        title="求助！老旧服务器登录密码忘了",
        content="公司有台2018年的服务器，登录密码找不到了，系统是CentOS7。试了admin、root123都不行，有没有大佬知道默认密码或者重置方法？\n（附：服务器机房在XX大厦B1层，门禁牌上的编号是8A3F）",
        author="IT小菜鸟",
        board_id=board1.id
    )
    post2 = Post(
        title="XX大厦附近有什么好吃的？",
        content="刚来这边上班，想问下XX大厦周边有没有性价比高的午饭？不要太贵，人均20左右～",
        author="打工人小李",
        board_id=board2.id
    )
    post3 = Post(
        title="分享一个简单的Python脚本",
        content="写了个自动备份SQLite数据库的脚本，贴出来给需要的人：\n```python\nimport shutil\nshutil.copy('data.db', 'data_backup.db')\n```",
        author="代码爱好者",
        board_id=board1.id
    )
    db.session.add_all([post1, post2, post3])
    db.session.commit()

    reply1 = Reply(
        content="CentOS7默认没有root密码，可能是之前管理员设的。试试重置：重启按e，修改kernel参数加rd.break，然后mount /sysroot rw，chroot /sysroot，passwd root改密码～",
        author="运维老司机",
        post_id=post1.id,
        signature="专注运维10年 | 常用命令：ssh root@xxx.xxx.xxx.xxx -p 22"
    )
    reply2 = Reply(
        content="我知道！大厦对面的巷子里有家兰州拉面，18元一碗，分量超足～",
        author="吃货小张",
        post_id=post2.id,
        signature="唯有美食不可辜负"
    )
    reply3 = Reply(
        content="谢谢分享！我之前用shell写过类似的，Python版本更简洁～",
        author="脚本达人",
        post_id=post3.id,
        signature="密钥：L2FkbWluL2RhdGEv"
    )
    reply4 = Reply(
        content="楼主的服务器是戴尔的吗？戴尔服务器默认用户名可能是dell，密码Dell123！",
        author="硬件爱好者",
        post_id=post1.id,
        signature="硬件问题欢迎咨询"
    )
    reply5 = Reply(
        content="马克一下，下次备份数据库能用～",
        author="小白白",
        post_id=post3.id,
        signature=""
    )
    db.session.add_all([reply1, reply2, reply3, reply4, reply5])
    db.session.commit()
    
    # 插入公司网站测试数据
    import json
    # 公司信息
    company = CompanyInfo(
        name="未来科技有限公司",
        description="未来科技有限公司成立于2015年，是一家专注于软件开发、硬件设计和人工智能技术的高科技企业。我们致力于为客户提供最先进的技术解决方案，帮助客户在数字化时代取得成功。",
        founded_year=2015,
        address="北京市海淀区中关村科技园区",
        phone="010-12345678",
        email="contact@futuretech.com",
        website="www.futuretech.com",
        slogan="科技创造未来，创新引领时代",
        logo_url="/static/images/logo.png"
    )
    db.session.add(company)
    
    # 产品分类
    category1 = ProductCategory(
        name="软件开发",
        description="各种软件开发工具和平台",
        order_num=1
    )
    category2 = ProductCategory(
        name="硬件设备",
        description="高性能硬件设备和解决方案",
        order_num=2
    )
    category3 = ProductCategory(
        name="人工智能",
        description="AI技术和解决方案",
        order_num=3
    )
    db.session.add_all([category1, category2, category3])
    db.session.commit()
    
    # 产品数据
    product1 = Product(
        name="HX-400型处理器",
        model="HX-400",
        description="HX-400型处理器是本公司自主研发的高性能多核处理器，采用7nm工艺制程，专为服务器和高性能计算领域设计。该处理器具有出色的计算能力和能效比，可满足各种高负载应用场景的需求。",
        features=json.dumps([
            "8核心16线程设计，基础频率3.2GHz，最大睿频4.5GHz",
            "7nm工艺制程，功耗仅为95W",
            "支持DDR4-3600内存，最大内存容量可达512GB",
            "集成PCIe 4.0控制器，支持64条PCIe通道",
            "支持硬件级虚拟化和安全加密功能"
        ]),
        specifications=json.dumps({
            "核心数": "8核心16线程",
            "基础频率": "3.2GHz",
            "最大睿频": "4.5GHz",
            "工艺制程": "7nm",
            "功耗": "95W TDP",
            "内存支持": "DDR4-3600，最大512GB",
            "PCIe版本": "PCIe 4.0 x64",
            "封装": "LGA 4189"
        }),
        category_id=category2.id,
        datasheet_url="/static/files/hx-400-datasheet.pdf",
        image_url="/static/images/products/hx-400.jpg",
        price=12999.00,
        stock=30
    )
    
    product2 = Product(
        name="GS-2000系列服务器",
        model="GS-2000",
        description="GS-2000系列服务器是基于HX-400处理器开发的高性能服务器，采用2U机架式设计，支持双路处理器配置，适用于数据中心、云计算和高性能计算等场景。",
        features=json.dumps([
            "支持双路HX-400处理器，最大16核心32线程",
            "24个DDR4内存插槽，最大内存容量可达1.5TB",
            "支持8个NVMe SSD和12个SATA HDD",
            "4个10Gbps以太网接口，支持链路聚合",
            "冗余电源和风扇设计，提高系统可靠性"
        ]),
        specifications=json.dumps({
            "处理器": "2×HX-400 8核心16线程",
            "内存": "64GB DDR4-3600 (最高1.5TB)",
            "存储": "2×1TB NVMe SSD + 4×4TB SATA HDD",
            "网络": "4个10Gbps以太网接口",
            "电源": "2×1200W冗余电源",
            "尺寸": "2U机架式",
            "重量": "25kg"
        }),
        category_id=category2.id,
        datasheet_url="/static/files/gs-2000-datasheet.pdf",
        image_url="/static/images/products/gs-2000.jpg",
        price=39999.00,
        stock=15
    )
    
    product3 = Product(
        name="GX-1000图形工作站",
        model="GX-1000",
        description="GX-1000图形工作站是专为设计师、工程师和内容创作者打造的高性能工作站，采用HX-400处理器和专业图形显卡，提供卓越的图形处理能力和计算性能。",
        features=json.dumps([
            "HX-400处理器，8核心16线程",
            "NVIDIA RTX A6000专业图形显卡，48GB GDDR6显存",
            "64GB DDR4-3600内存，支持扩展到256GB",
            "2TB NVMe SSD + 4TB HDD存储组合",
            "专业散热设计，确保长时间稳定运行"
        ]),
        specifications=json.dumps({
            "处理器": "HX-400 8核心16线程",
            "显卡": "NVIDIA RTX A6000 (48GB GDDR6)",
            "内存": "64GB DDR4-3600",
            "存储": "2TB NVMe SSD + 4TB HDD",
            "接口": "USB 3.2 Gen2 ×6, Thunderbolt 4 ×2, DisplayPort 1.4 ×4",
            "电源": "1500W 80+ Titanium",
            "尺寸": "塔式，450×180×420mm"
        }),
        category_id=category2.id,
        datasheet_url="/static/files/gx-1000-datasheet.pdf",
        image_url="/static/images/products/gx-1000.jpg",
        price=24999.00,
        stock=20
    )
    
    db.session.add_all([product1, product2, product3])
    db.session.commit()
    
    print("数据库初始化成功！测试数据已插入")

# -------------------------- 404页面（保持不变）--------------------------
@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({
        "status": "error",
        "msg": "404 Not Found - 页面不存在或已被删除",
        "html": "<h1>404 页面不存在</h1><p>你访问的页面可能已经被删除，或者URL输入错误，请返回首页重试。</p>"
    }), 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)