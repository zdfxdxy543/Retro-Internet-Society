from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()
# 板块表（如：技术讨论、生活闲聊）
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 板块名称
    description = db.Column(db.String(200))  # 板块描述
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 关联帖子（一对多）
    posts = db.relationship("Post", backref="board", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Board {self.name}>"

# 帖子表（核心内容，含关键线索）
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # 帖子标题
    content = db.Column(db.Text, nullable=False)  # 帖子正文（可藏线索）
    author = db.Column(db.String(50), default="匿名用户")  # 发帖人
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)  # 浏览量（拟真用）
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"), nullable=False)
    # 关联回帖
    replies = db.relationship("Reply", backref="post", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post {self.title}>"

# 回帖表（含核心回帖线索，无大模型凑数）
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 回帖内容（可藏线索）
    author = db.Column(db.String(50), default="匿名用户")  # 回帖人
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    signature = db.Column(db.String(200))  # 签名档（可藏线索）

    def __repr__(self):
        return f"<Reply {self.id}>"

# 玩家状态表（记录已访问页面、收集线索，匿名）
class PlayerStatus(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # 匿名ID
    visited_boards = db.Column(db.JSON, default=[])  # 已访问板块ID列表
    visited_posts = db.Column(db.JSON, default=[])  # 已访问帖子ID列表
    collected_clues = db.Column(db.JSON, default=[])  # 已收集线索ID（后续扩展用）
    last_visit = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PlayerStatus {self.id}>"

# -------------------------- 新增：大模型动态页面模型 --------------------------
class DynamicPage(db.Model):
    """大模型自动生成的动态网页模型"""
    __tablename__ = "dynamic_page"  # 显式指定表名（可选，默认是类名小写）
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # URL唯一标识（如 "ai-tech-2025"）
    title = db.Column(db.String(200), nullable=False)  # 页面标题
    content = db.Column(db.Text, nullable=False)  # 大模型生成的内容（HTML/Markdown）
    content_type = db.Column(db.String(20), default="html")  # 内容格式（html/markdown）
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 生成时间
    is_active = db.Column(db.Boolean, default=True)  # 是否启用（可下架）

    def __repr__(self):
        return f"<DynamicPage {self.slug}>"
    
    def to_dict(self):
        """可选：新增序列化方法，方便返回给前端（无需手动构造字典）"""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_active": self.is_active,
            "category": self.category,
            "is_public": self.is_public
        }