from flask import Blueprint
from .base import BasePageView, register_page_route
from ..models import Post, Reply, PlayerStatus
from datetime import datetime

# 创建用户相关蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')

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

# 注册用户相关路由
register_page_route(user_bp, "/<author>", UserProfileView)  # 个人页面路由

# 为未来用户系统预留扩展空间
# 例如：登录、注册、个人设置等
# @user_bp.route("/login", methods=["GET", "POST"])
# def login():
#     pass

# @user_bp.route("/register", methods=["GET", "POST"])
# def register():
#     pass

# @user_bp.route("/settings")
# def settings():
#     pass
