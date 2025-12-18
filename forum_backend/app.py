from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from flask.views import MethodView  # 导入Flask类视图基类
from config import config
from models import db, Board, Post, Reply, PlayerStatus
from datetime import datetime
from ai_page_generator import AIPageGenerator
from sqlalchemy.exc import SQLAlchemyError
import functools

app = Flask(__name__)
app.config.from_object(config)

app.config["ALLOWED_HTML_TAGS"] = ["div", "p", "h2", "h3", "h4", "ul", "li", "a", "strong", "em", "code", "pre"]
app.config["ALLOWED_HTML_ATTRS"] = {"a": ["href", "target", "rel"], "code": ["class"]}
app.config["API_KEY"] = "your-secret-key-123456"  # 请替换为你的实际密钥（重要！）

CORS(app, supports_credentials=True)
db.init_app(app)

ai_page_generator = AIPageGenerator(db=db,app_config=app.config)

# -------------------------- 1. 核心基类（所有网页路由继承此类）--------------------------
class BasePageView(MethodView):
    """网页路由基类：封装公共逻辑，子类只需实现 get_data()"""
    
    def dispatch_request(self, *args, **kwargs):
        """所有请求都会经过此方法（MethodView核心），封装公共逻辑"""
        try:
            # 第一步：生成/验证匿名玩家ID（公共逻辑）
            player_id = session.get("player_id")
            if not player_id or not PlayerStatus.query.get(player_id):
                # 新建匿名玩家
                player = PlayerStatus()
                db.session.add(player)
                db.session.commit()
                player_id = player.id
                session["player_id"] = player_id
            else:
                # 更新最后访问时间
                player = PlayerStatus.query.get(player_id)
                player.last_visit = datetime.utcnow()
                db.session.commit()

            # 第二步：调用子类实现的 get_data()，获取页面专属数据
            page_data = self.get_data(*args, **kwargs)  # 子类必须实现此方法

            # 第三步：返回统一格式的响应（公共响应格式）
            return jsonify({
                "status": "success",
                "data": {
                    "player_id": player_id,  # 所有页面都返回匿名ID（前端无需显示）
                    **page_data  # 合并子类返回的页面数据（如title、boards、posts等）
                }
            })
        except Exception as e:
            # 异常处理：返回404（拟真）
            return make_response(jsonify({
                "status": "error",
                "msg": "404 Not Found - 页面不存在或已被删除",
                "html": "<h1>404 页面不存在</h1><p>你访问的页面可能已经被删除，或者URL输入错误，请返回首页重试。</p>"
            }), 404)

    def get_data(self, *args, **kwargs):
        """子类必须实现的方法：返回页面专属数据（如 {"title": "首页", "boards": [...]}）"""
        raise NotImplementedError("子类必须实现 get_data() 方法")

# -------------------------- 2. 辅助函数：简化路由注册（可选，进一步简化开发）--------------------------
def register_page_route(url_rule, view_class, endpoint=None):
    """
    注册页面路由的辅助函数，避免重复写 add_url_rule
    :param url_rule: 路由路径（如 "/"、"/board/<int:board_id>"）
    :param view_class: 视图类（继承自 BasePageView）
    :param endpoint: 路由别名（默认用视图类名小写）
    """
    if not endpoint:
        endpoint = view_class.__name__.lower()
    app.add_url_rule(url_rule, view_func=view_class.as_view(endpoint))

# -------------------------- 3. 具体页面视图类（继承 BasePageView）--------------------------
# 首页视图类
class IndexView(BasePageView):
    def get_data(self):
        # 只关注首页专属逻辑：查询所有板块
        boards = Board.query.all()
        board_list = [{
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
        } for board in boards]
        return {
            "title": "复古论坛 - 首页",
            "boards": board_list
        }

# 板块页面视图类
class BoardView(BasePageView):
    def get_data(self, board_id):
        # 板块页专属逻辑：查询板块+帖子
        board = Board.query.get_or_404(board_id)  # 不存在直接404
        posts = Post.query.filter_by(board_id=board_id).order_by(Post.create_time.desc()).all()
        
        # 更新玩家已访问板块
        player_id = session["player_id"]
        player = PlayerStatus.query.get(player_id)
        if board_id not in player.visited_boards:
            player.visited_boards.append(board_id)
            db.session.commit()
        
        # 更新帖子浏览量
        for post in posts:
            post.view_count += 1
        db.session.commit()
        
        post_list = [{
            "id": post.id,
            "title": post.title,
            "author": post.author,
            "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "view_count": post.view_count,
            "reply_count": len(post.replies),
            "board_id": post.board.id,
            "board_name": post.board.name
        } for post in posts]
        
        return {
            "title": f"复古论坛 - {board.name}",
            "board": {
                "id": board.id,
                "name": board.name,
                "description": board.description
            },
            "posts": post_list
        }

# 帖子详情页视图类
class PostView(BasePageView):
    def get_data(self, post_id):
        # 帖子页专属逻辑：查询帖子+回帖
        post = Post.query.get_or_404(post_id)
        replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.create_time.asc()).all()
        
        # 更新玩家已访问帖子
        player_id = session["player_id"]
        player = PlayerStatus.query.get(player_id)
        if post_id not in player.visited_posts:
            player.visited_posts.append(post_id)
            db.session.commit()
        
        # 更新帖子浏览量
        post.view_count += 1
        db.session.commit()
        
        reply_list = [{
            "id": reply.id,
            "content": reply.content,
            "author": reply.author,
            "signature": reply.signature,
            "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S")
        } for reply in replies]
        
        return {
            "title": f"复古论坛 - {post.title}",
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "board_name": post.board.name,
                "board_id": post.board.id
            },
            "replies": reply_list
        }
    
# 个人页面（查看用户发帖、回帖）
class UserProfileView(BasePageView):
    def get_data(self, author):
        # 1. 查询该用户发布的帖子（按时间倒序）
        user_posts = Post.query.filter_by(author=author).order_by(Post.create_time.desc()).all()
        post_list = [{
            "id": post.id,
            "title": post.title,
            "board_name": post.board.name,
            "board_id": post.board.id,
            "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "view_count": post.view_count,
            "reply_count": len(post.replies)
        } for post in user_posts]

        # 2. 查询该用户发布的回帖（按时间倒序）
        user_replies = Reply.query.filter_by(author=author).order_by(Reply.create_time.desc()).all()
        reply_list = [{
            "id": reply.id,
            "content": reply.content[:100] + "..." if len(reply.content) > 100 else reply.content,  # 截取前100字
            "signature": reply.signature,
            "post_title": reply.post.title,  # 回帖对应的帖子标题
            "post_id": reply.post.id,  # 回帖对应的帖子ID（用于跳转）
            "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S")
        } for reply in user_replies]

        return {
            "title": f"复古论坛 - {author} 的个人主页",
            "user_info": {
                "author": author,
                "post_count": len(post_list),  # 发帖数
                "reply_count": len(reply_list)  # 回帖数
            },
            "posts": post_list,  # 发布的帖子
            "replies": reply_list  # 发布的回帖
        }
    
# 搜索接口视图类（返回JSON数据，供前端渲染）
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
    
class SearchResultView(BasePageView):
    def get_data(self):
        return {
            "title": "复古论坛 - 搜索结果"
        }

# 新人指南视图类
class NewbieGuideView(BasePageView):
    def get_data(self):
        # 静态页面：只需返回标题
        return {
            "title": "复古论坛 - 新人指南"
        }

# 版规说明视图类
class RulesView(BasePageView):
    def get_data(self):
        return {
            "title": "复古论坛 - 版规说明"
        }

# 联系我们视图类
class ContactView(BasePageView):
    def get_data(self):
        return {
            "title": "复古论坛 - 联系我们"
        }
    
# 动态页面类
class DynamicPageView(BasePageView):
    """通用动态页面视图类：匹配大模型生成的所有网页"""
    def get_data(self, slug):
        # 1. 查询动态页面（未启用或不存在则404）
        dynamic_page = DynamicPage.query.filter_by(
            slug=slug, 
            is_active=True
        ).first_or_404()  # 不存在直接返回404
        
        # 2. 返回页面数据（前端根据content_type渲染）
        return {
            "title": f"复古论坛 - {dynamic_page.title}",
            "dynamic_page": {
                "slug": dynamic_page.slug,
                "title": dynamic_page.title,
                "content": dynamic_page.content,
                "content_type": dynamic_page.content_type,
                "create_time": dynamic_page.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

# -------------------------- 4. 注册所有路由（用辅助函数简化）--------------------------
register_page_route("/", IndexView)  # 首页
register_page_route("/board/<int:board_id>", BoardView)  # 板块页
register_page_route("/post/<int:post_id>", PostView)  # 帖子页
register_page_route("/user/<author>", UserProfileView)  # 个人页面路由（放在动态页面之前）
register_page_route("/api/search", SearchView)  # 搜索接口路由（API风格）
register_page_route("/search", SearchResultView)  # 搜索结果页面路由（前端渲染用）
register_page_route("/newbie", NewbieGuideView)  # 新人指南
register_page_route("/rules", RulesView)  # 版规说明
register_page_route("/contact", ContactView)  # 联系我们
register_page_route("/page/<slug>", DynamicPageView)  # 路径格式：/page/xxx

# -------------------------- 大模型生成页面接口（带鉴权） --------------------------
# 接口鉴权装饰器
def require_api_key(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != app.config.get("API_KEY"):
            return jsonify({"status": "error", "msg": "无权限访问（无效API密钥）"}), 403
        return f(*args, **kwargs)
    return wrapper

# 大模型生成页面接口（简化后的逻辑，核心调用工具类）
@app.route("/api/ai/generate-page", methods=["POST"])
@require_api_key  # 保留原有鉴权装饰器
def ai_generate_page():
    """
    大模型生成动态页面的接口（仅内部/管理员调用）
    请求体：{"title": "页面标题", "content": "HTML/Markdown内容", "content_type": "html", "category": "tech"}
    """
    try:
        data = request.get_json()
        # 调用工具类的核心方法，创建动态页面
        page_info = ai_page_generator.create_dynamic_page(
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

# -------------------------- 5. 数据库初始化（保持不变）--------------------------
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
    print("数据库初始化成功！测试数据已插入")

# -------------------------- 6. 404页面（保持不变）--------------------------
@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({
        "status": "error",
        "msg": "404 Not Found - 页面不存在或已被删除",
        "html": "<h1>404 页面不存在</h1><p>你访问的页面可能已经被删除，或者URL输入错误，请返回首页重试。</p>"
    }), 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)