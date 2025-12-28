import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录
app_root = os.path.dirname(os.path.abspath(__file__))

class Config:
    # 数据库配置（SQLite3本地文件）
    # 直接使用instance/forum.db路径，符合项目结构
    app_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_root, 'instance', 'forum.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.replace(chr(92), '/')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cookie配置（匿名玩家ID，有效期30天）
    SESSION_COOKIE_NAME = "forum_anon_id"  # 隐藏游戏痕迹，用普通Cookie名
    PERMANENT_SESSION_LIFETIME = 30 * 24 * 3600  # 30天
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_123")  # 本地开发用，上线替换
    
    # AI相关配置
    # 硅基流动API配置
    SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY", "sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv")
    SILICON_FLOW_API_URL = os.getenv("SILICON_FLOW_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
    # 兼容旧版变量名
    SILICONFLOW_API_KEY = SILICON_FLOW_API_KEY  # 兼容ai_content_generator.py中的命名
    SILICONFLOW_API_URL = SILICON_FLOW_API_URL  # 兼容ai_content_generator.py中的命名
    AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "Pro/deepseek-ai/DeepSeek-V3.2-Exp")
    # 测试模式标志，用于控制是否使用真实API
    TEST_MODE = os.getenv("TEST_MODE", "False").lower() in ('true', '1', 't', 'yes')

config = Config()