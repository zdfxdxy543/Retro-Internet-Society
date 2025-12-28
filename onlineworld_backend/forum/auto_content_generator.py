import requests
import time
import random
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
# 直接导入模型和原生SQLAlchemy的Base（无需Flask）
from .models import Board, Post, Reply

# -------------------------- 基础配置（必须手动填写，与项目一致）--------------------------
# 数据库配置（关键！必须和项目config.py中的数据库地址完全一致）
# 获取项目根目录
app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(app_root, 'instance', 'forum.db')
DATABASE_URL = f"sqlite:///{db_path.replace(chr(92), '/')}"
# 若用MySQL，需先安装依赖：pip install pymysql

# 硅基流动API配置
SILICONFLOW_API_KEY = "sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv"  # 替换为你的API密钥
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = "Pro/deepseek-ai/DeepSeek-V3.2-Exp"  # 硅基流动支持的模型（如glm-4、llama3-8b）

# 发帖/回复配置
NEW_POSTS_PER_RUN = 2
REPLIES_PER_RUN = 3
REPLY_TIME_WINDOW = 24  # 仅回复24小时内帖子
PROB_REUSE_USER = 0.7   # 70%复用现有用户，30%生成新用户
BASE_AUTHOR_POOL = [
    "路人甲", "技术爱好者", "打工人小李", "吃货小张", "运维老司机",
    "编程菜鸟", "生活观察员", "数码发烧友", "职场新人", "闲聊达人"
]
BOARD_THEME_MAP = {
    "技术讨论区": ["编程问题求助", "技术工具分享", "服务器运维经验", "编程语言对比", "软件使用技巧"],
    "生活闲聊区": ["日常美食分享", "通勤路线推荐", "租房经验交流", "兴趣爱好讨论", "职场吐槽"],
    "游戏娱乐区": ["复古游戏推荐", "游戏攻略分享", "电竞赛事讨论", "游戏手柄测评"]
}

# -------------------------- 原生SQLAlchemy初始化（无Flask依赖！）--------------------------
# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite需加此参数
# 创建会话工厂（替代Flask-SQLAlchemy的db.session）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 验证数据库连接
def test_db_connection():
    try:
        db = SessionLocal()
        # 执行简单查询，验证连接
        db.query(Board).first()
        db.close()
        print("✅ 数据库连接成功（原生SQLAlchemy，无Flask依赖）")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败：{str(e)}")
        print(f"⚠️  请检查 DATABASE_URL 是否与项目config.py一致！")
        return False

# -------------------------- 工具函数：获取数据库会话 --------------------------
def get_db():
    """获取数据库会话（用完自动关闭）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------- 工具函数：获取现有用户列表（去重）--------------------------
def get_existing_users():
    db = next(get_db())
    try:
        post_authors = db.query(Post.author).distinct().all()
        reply_authors = db.query(Reply.author).distinct().all()
        existing_users = set()
        for author in post_authors:
            existing_users.add(author[0].strip())
        for author in reply_authors:
            existing_users.add(author[0].strip())
        return [user for user in existing_users if user]
    finally:
        db.close()

# -------------------------- 工具函数：生成新用户（不重复）--------------------------
def generate_new_user(existing_users):
    user_prompt = f"""
    生成一个复古论坛的用户名，要求：
    1. 风格：接地气、生活化，符合2000-2010年论坛风格（如"打工仔小李"、"编程老陈"）；
    2. 格式：2-4字，可带职业、身份或昵称（如"运维达人"、"校园吃货"）；
    3. 唯一性：不要和以下现有用户名重复：{','.join(existing_users[:10]) if existing_users else '无'}；
    4. 输出：仅返回用户名，不要任何多余字符。
    """
    new_username = call_siliconflow_api(user_prompt, temperature=0.9)
    
    # API失败时降级到基础池
    if not new_username:
        available_users = [u for u in BASE_AUTHOR_POOL if u not in existing_users]
        return random.choice(available_users) if available_users else f"用户{random.randint(1000,9999)}"
    
    # 重试3次避免重复
    retry_count = 0
    while new_username in existing_users and retry_count < 3:
        new_username = call_siliconflow_api(user_prompt, temperature=0.9)
        retry_count += 1
    return new_username.strip() if new_username else f"用户{random.randint(1000,9999)}"

# -------------------------- 工具函数：选择作者（复用/新增）--------------------------
def select_author(exclude_author=None):
    existing_users = get_existing_users()
    random_prob = random.random()
    
    # 70%复用现有用户
    if random_prob < PROB_REUSE_USER and existing_users:
        candidates = existing_users if not exclude_author else [u for u in existing_users if u != exclude_author]
        return random.choice(candidates) if candidates else generate_new_user(existing_users)
    # 30%生成新用户
    else:
        new_user = generate_new_user(existing_users)
        print(f"🆕 生成新用户：{new_user}")
        return new_user

# -------------------------- 硅基流动API调用 --------------------------
def call_siliconflow_api(prompt, temperature=0.7):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 500
    }
    try:
        response = requests.post(SILICONFLOW_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"❌ API调用失败：{str(e)}")
        return None

# -------------------------- 自动发帖 --------------------------
def generate_new_posts():
    db = next(get_db())
    try:
        # 查询所有板块
        boards = db.query(Board).all()
        if not boards:
            print("⚠️  无可用板块，跳过发帖")
            return
        
        generated_count = 0
        while generated_count < NEW_POSTS_PER_RUN:
            board = random.choice(boards)
            board_name = board.name
            theme = random.choice(BOARD_THEME_MAP.get(board_name, ["日常讨论"]))
            author = select_author()
            
            # 生成帖子内容
            post_prompt = f"""
            你是复古论坛的用户「{author}」，在「{board_name}」板块发一个帖子，要求：
            1. 标题：简洁明了，含「{theme}」关键词，不超过20字；
            2. 内容：口语化，3-5句话，像真实用户提问/分享，贴合「{author}」昵称风格；
            3. 风格：接地气、有生活气息，不官方；
            4. 输出格式：先标题（换行）再内容，无多余字符。
            """
            content = call_siliconflow_api(post_prompt)
            if not content:
                continue
            
            # 拆分标题和内容
            parts = [p.strip() for p in content.split("\n") if p.strip()]
            if len(parts) < 2:
                print(f"⚠️  帖子格式错误（{author}）：{content}")
                continue
            title, post_content = parts[0], "\n".join(parts[1:])
            
            # 新增帖子到数据库
            new_post = Post(
                title=title,
                content=post_content,
                author=author,
                board_id=board.id,
                create_time=datetime.utcnow()
            )
            db.add(new_post)
            db.commit()
            print(f"✅ 新增帖子：[{board_name}] {title}（{author}）")
            generated_count += 1
            time.sleep(1)
    except Exception as e:
        db.rollback()
        print(f"❌ 发帖失败：{str(e)}")
    finally:
        db.close()

# -------------------------- 自动回复 --------------------------
def generate_replies():
    db = next(get_db())
    try:
        # 查询24小时内的帖子
        recent_time = datetime.utcnow() - timedelta(hours=REPLY_TIME_WINDOW)
        recent_posts = db.query(Post).filter(
            Post.create_time >= recent_time
        ).order_by(Post.create_time.desc()).all()
        
        if not recent_posts:
            print("⚠️  无近期帖子，跳过回复")
            return
        
        replied_count = 0
        random.shuffle(recent_posts)
        for post in recent_posts:
            if replied_count >= REPLIES_PER_RUN:
                break
            
            author = select_author(exclude_author=post.author)
            signatures = ["", "专注此事10年", "纯属个人经验", "欢迎交流～", "亲测有效！", "踩过坑分享"]
            signature = random.choice(signatures)
            
            # 生成回复内容
            reply_prompt = f"""
            你是复古论坛的用户「{author}」，回复以下帖子：
            标题：{post.title}
            内容：{post.content}
            发帖人：{post.author}
            要求：1. 强相关；2. 口语化1-3句话；3. 贴合「{author}」风格；4. 仅返回回复内容。
            """
            reply_content = call_siliconflow_api(reply_prompt, temperature=0.8)
            if not reply_content:
                continue
            
            # 新增回复到数据库
            new_reply = Reply(
                content=reply_content,
                author=author,
                signature=signature,
                post_id=post.id,
                create_time=datetime.utcnow()
            )
            db.add(new_reply)
            db.commit()
            print(f"💬 新增回复：《{post.title}》（{author}）")
            replied_count += 1
            time.sleep(1)
    except Exception as e:
        db.rollback()
        print(f"❌ 回复失败：{str(e)}")
    finally:
        db.close()

# -------------------------- 定时任务 --------------------------
# def main():
#     # 先验证数据库连接
#     if not test_db_connection():
#         return
    
#     # 初始化定时任务（每个半点执行）
#     scheduler = BlockingScheduler(timezone="Asia/Shanghai")
#     scheduler.add_job(
#         func=lambda: [generate_new_posts(), generate_replies()],
#         trigger="cron",
#         minute="0,30",
#         id="auto_content_job",
#         name="半点自动发帖回复"
#     )
    
#     # 启动日志
#     print("=" * 60)
#     print("🚀 自动内容生成服务启动成功（无Flask依赖）")
#     print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"配置：{NEW_POSTS_PER_RUN}帖/{REPLIES_PER_RUN}回复/次 | 24小时内回复 | 70%复用用户")
#     print(f"数据库：{DATABASE_URL}")
#     print("=" * 60)
    
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         print("⚠️  服务已停止")

# if __name__ == "__main__":
#     main()

# -------------------------- 主程序入口 --------------------------
def main():
    # 先验证数据库连接
    if not test_db_connection():
        return
    
    # 只执行一次发帖和回帖
    generate_new_posts()  # 生成新帖子
    generate_replies()    # 生成回复
    print("✅ 已完成一次发帖和回帖，程序结束")

# 直接执行主函数（不再启动定时任务）
if __name__ == "__main__":
    main()