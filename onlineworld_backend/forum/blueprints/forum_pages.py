from flask import Blueprint
from .base import BasePageView, register_page_route
from ..models import Board, Post, Reply, PlayerStatus, DynamicPage, db
from flask import session
from datetime import datetime

# 创建论坛页面蓝图
forum_bp = Blueprint('forum', __name__, url_prefix='/forum')

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

# 搜索结果页面视图类
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

# 注册所有论坛页面路由
register_page_route(forum_bp, "/", IndexView)  # 论坛首页
register_page_route(forum_bp, "/board/<int:board_id>", BoardView)  # 板块页
register_page_route(forum_bp, "/post/<int:post_id>", PostView)  # 帖子页
register_page_route(forum_bp, "/search", SearchResultView)  # 搜索结果页面
register_page_route(forum_bp, "/newbie", NewbieGuideView)  # 新人指南
register_page_route(forum_bp, "/rules", RulesView)  # 版规说明
register_page_route(forum_bp, "/contact", ContactView)  # 联系我们
register_page_route(forum_bp, "/page/<slug>", DynamicPageView)  # 动态页面

# 为未来公司网站预留蓝图结构
# company_bp = Blueprint('company', __name__, url_prefix='/company')
# 可以在这里提前定义公司网站的路由结构，或者在需要时创建单独的文件

# 为其他可能的网页预留蓝图结构
# other_bp = Blueprint('other', __name__, url_prefix='/other')
