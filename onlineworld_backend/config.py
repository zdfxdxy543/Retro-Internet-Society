import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录
app_root = os.path.dirname(os.path.abspath(__file__))

class Config:
    # 数据库配置（SQLite3本地文件）
    db_path = os.path.join(app_root, 'instance', 'forum.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{db_path.replace(chr(92), '/')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cookie配置（匿名玩家ID，有效期30天）
    SESSION_COOKIE_NAME = "forum_anon_id"  # 隐藏游戏痕迹，用普通Cookie名
    PERMANENT_SESSION_LIFETIME = 30 * 24 * 3600  # 30天
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123")  # 本地开发用，上线替换

config = Config()
