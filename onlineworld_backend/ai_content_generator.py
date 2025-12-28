import requests
import time
import random
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# 直接导入模型和原生SQLAlchemy的Base（无需Flask）
from forum.models import Board, Post, Reply
# 导入工具系统
from ai_tools import tool_registry
# 导入配置
from config import Config

# -------------------------- 基础配置（从config.py获取）--------------------------
# 数据库配置（使用与项目config.py相同的配置）
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# 硅基流动API配置
SILICONFLOW_API_KEY = Config.SILICONFLOW_API_KEY
SILICONFLOW_API_URL = Config.SILICONFLOW_API_URL
MODEL_NAME = Config.AI_MODEL_NAME

# 发帖/回复配置
NEW_POSTS_PER_RUN = 1  # 增加到每次运行生成5个新帖子
REPLIES_PER_RUN = 4    # 增加到每次运行生成8个回复
REPLY_TIME_WINDOW = 24  # 仅回复24小时内帖子
PROB_REUSE_USER = 0.7   # 70%复用现有用户
USE_TOOL_PROB = 1.0     # 总是使用工具获取地点信息，确保与数据库一致
BASE_AUTHOR_POOL = [
    "路人甲", "技术爱好者", "打工人小李", "吃货小张", "运维老司机",
    "编程菜鸟", "生活观察员", "数码发烧友", "职场新人", "闲聊达人"
]
# 与地点相关的主题列表，确保这些主题使用工具获取地点信息
LOCATION_RELATED_THEMES = [
    "日常美食分享", "通勤路线推荐", "租房经验交流", "兴趣爱好讨论"
]
BOARD_THEME_MAP = {
    "技术讨论区": ["编程问题求助", "技术工具分享", "服务器运维经验", "编程语言对比", "软件使用技巧"],
    "生活闲聊区": ["日常美食分享", "通勤路线推荐", "租房经验交流", "兴趣爱好讨论", "职场吐槽"],
    "游戏娱乐区": ["复古游戏推荐", "游戏攻略分享", "电竞赛事讨论", "游戏手柄测评"]
}

# -------------------------- 导入Flask应用上下文
from app import app

# -------------------------- 原生SQLAlchemy初始化（无Flask依赖！）--------------------------
# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite需加此参数
# 创建会话工厂（替代Flask-SQLAlchemy的db.session）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 验证数据库连接
def test_db_connection():
    try:
        with app.app_context():
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
    with app.app_context():
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
    
    # 调用API生成用户名
    result = call_siliconflow_api(user_prompt, temperature=0.9)
    
    # 处理API响应
    new_username = None
    if result:
        try:
            # 如果result是字典，说明是完整的API响应
            if isinstance(result, dict) and "choices" in result:
                new_username = result["choices"][0]["message"]["content"].strip()
            # 如果是字符串，直接使用
            elif isinstance(result, str):
                new_username = result.strip()
        except Exception as e:
            print(f"❌ 解析用户名失败：{str(e)}")
    
    # API失败时降级到基础池
    if not new_username:
        available_users = [u for u in BASE_AUTHOR_POOL if u not in existing_users]
        return random.choice(available_users) if available_users else f"用户{random.randint(1000,9999)}"
    
    # 重试3次避免重复
    retry_count = 0
    while new_username in existing_users and retry_count < 3:
        result = call_siliconflow_api(user_prompt, temperature=0.9)
        if result:
            try:
                if isinstance(result, dict) and "choices" in result:
                    new_username = result["choices"][0]["message"]["content"].strip()
                elif isinstance(result, str):
                    new_username = result.strip()
            except Exception as e:
                print(f"❌ 重试解析用户名失败：{str(e)}")
        retry_count += 1
    
    return new_username if new_username and new_username not in existing_users else f"用户{random.randint(1000,9999)}"

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
def call_siliconflow_api(messages, temperature=0.7, tools=None, timeout=30):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
    }
    
    # 确保messages是列表格式
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000
    }
    
    # 如果提供了工具，添加工具配置
    if tools:
        # 转换工具格式以符合硅基流动API要求
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            formatted_tools.append(formatted_tool)
        
        data["tools"] = formatted_tools
        data["tool_choice"] = "auto"  # 允许模型自动选择是否使用工具
    
    print(f"📤 API请求数据：{data}")
    try:
        print(f"🔄 正在调用API...")
        response = requests.post(SILICONFLOW_API_URL, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        print(f"📥 API响应结构：")
        print(f"   - 有choices字段: {'choices' in result}")
        if 'choices' in result:
            print(f"   - choices数量: {len(result['choices'])}")
            if result['choices']:
                print(f"   - 第一个choice类型: {type(result['choices'][0])}")
                print(f"   - 第一个choice内容: {json.dumps(result['choices'][0], ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ API调用失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return None

# -------------------------- 处理工具调用 --------------------------
def handle_tool_call(tool_call):
    """处理大模型的工具调用请求"""
    tool_name = tool_call["function"]["name"]
    
    try:
        tool_args = json.loads(tool_call["function"]["arguments"])
        print(f"🔧 执行工具调用：{tool_name}，参数：{tool_args}")
    except json.JSONDecodeError as e:
        print(f"❌ 解析工具参数失败：{str(e)}")
        return {
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": f"错误：工具参数格式错误 - {str(e)}"
        }
    
    # 获取工具实例
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        print(f"❌ 找不到工具：{tool_name}")
        return {
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": f"错误：找不到工具 '{tool_name}'"
        }
    
    try:
        # 特殊处理MapLocationTool，因为模型可能传递错误的参数
        if tool_name == "get_map_location_info":
            # 检查是否有keyword参数，如果有，转换为合适的查询
            if "keyword" in tool_args:
                keyword = tool_args["keyword"]
                print(f"⚠️  MapLocationTool参数转换：将keyword '{keyword}'转换为地点查询")
                # 尝试直接通过名称获取地点信息
                # 如果是特定地点名称（如阳光小区），尝试获取详细信息
                if keyword in ["星云小区", "幻想公寓", "梦境城邦", "星湖别墅"]:
                    # 这里可以根据名称映射到对应的place_id
                    place_id_map = {
                        "星云小区": 1,
                        "幻想公寓": 2,
                        "梦境城邦": 3,
                        "星湖别墅": 4
                    }
                    if keyword in place_id_map:
                        tool_args = {"query_type": "places", "place_id": place_id_map[keyword]}
                        print(f"🔍 直接查询特定地点：{keyword} (place_id={place_id_map[keyword]})")
                    else:
                        tool_args = {"query_type": "places", "limit": 5}
            elif "query_type" not in tool_args:
                tool_args["query_type"] = "places"
            # 转换region_id为place_id
            if "region_id" in tool_args:
                tool_args["place_id"] = tool_args.pop("region_id")
            # 转换place_name为place_id
            elif "place_name" in tool_args:
                place_name = tool_args["place_name"]
                print(f"⚠️  MapLocationTool参数转换：将place_name '{place_name}'转换为place_id")
                place_id_map = {
                    "星云小区": 1,
                    "幻想公寓": 2,
                    "梦境城邦": 3,
                    "星湖别墅": 4
                }
                if place_name in place_id_map:
                    tool_args = {"query_type": "places", "place_id": place_id_map[place_name]}
                    print(f"🔍 直接查询特定地点：{place_name} (place_id={place_id_map[place_name]})")
                else:
                    tool_args = {"query_type": "places", "limit": 5}
        
        # 执行工具
        result = tool.execute(**tool_args)
        return {
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": result
        }
    except TypeError as e:
        print(f"❌ 工具参数错误：{str(e)}")
        # 如果是参数错误，提供友好的错误信息
        return {
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": f"错误：工具参数错误 - {str(e)}"
        }
    except Exception as e:
        print(f"❌ 工具执行失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": f"执行工具失败：{str(e)}"
        }

# -------------------------- 带工具调用的内容生成 --------------------------
def generate_content_with_tools(messages, temperature=0.7, use_tool_prob=USE_TOOL_PROB, max_tool_calls=2, current_tool_calls=0):
    """生成内容，支持工具调用（有概率使用工具）"""
    
    # 随机决定是否使用工具
    use_tools = random.random() < use_tool_prob
    
    if use_tools and current_tool_calls < max_tool_calls:
        print(f"🔧 本次生成将尝试使用工具获取额外信息（已调用{current_tool_calls}/{max_tool_calls}次）")
        # 获取所有工具的描述
        tools_description = tool_registry.get_tools_description()
        
        # 第一次调用大模型
        response = call_siliconflow_api(messages, temperature, tools_description, timeout=60)
        if not response:
            print("⚠️  使用工具失败，回退到普通生成模式")
            return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
        
        # 处理大模型的响应
        try:
            if "choices" not in response or not response["choices"]:
                print("⚠️  API响应格式错误，回退到普通生成模式")
                return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
                
            message = response["choices"][0]["message"]
            
            # 如果大模型想要调用工具
            if message.get("tool_calls"):
                tool_call_results = []
                
                # 处理每个工具调用
                for tool_call in message["tool_calls"]:
                    result = handle_tool_call(tool_call)
                    tool_call_results.append(result)
                
                # 将工具调用结果添加到对话历史
                for result in tool_call_results:
                    messages.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "id": result["tool_call_id"],
                            "type": "function",
                            "function": {
                                "name": result["name"],
                                "arguments": "{}"
                            }
                        }]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "name": result["name"],
                        "content": result["content"],
                        "tool_call_id": result["tool_call_id"]
                    })
                
                # 增加工具调用计数
                current_tool_calls += 1
                
                # 再次调用大模型，获取最终响应
                response = call_siliconflow_api(messages, temperature, timeout=60)
                if not response:
                    return None
                    
                print(f"📤 工具调用后API返回原始响应：{json.dumps(response, ensure_ascii=False, indent=2)}")
                
                if "choices" not in response or not response["choices"]:
                    print("⚠️  工具调用后API响应中没有choices字段或choices为空")
                    return None
                    
                message = response["choices"][0]["message"]
                # 详细记录content和reasoning_content的内容
                content_field = message.get("content", "").strip()
                reasoning_content_field = message.get("reasoning_content", "").strip()
                print(f"📋 工具调用后content字段内容: {'[空]' if not content_field else content_field[:100]}...")
                print(f"📋 工具调用后reasoning_content字段内容: {'[空]' if not reasoning_content_field else reasoning_content_field[:100]}...")
                # 优先使用content字段（最终输出结果），仅当content为空时才使用reasoning_content
                content = content_field or reasoning_content_field
                
                # 检查是否是DSML格式的工具调用
                if content and "<｜DSML｜function_calls>" in content:
                    print("⚠️  检测到DSML格式工具调用请求，当前版本暂不支持DSML格式，回退到普通生成模式")
                    return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
                
                print(f"📝 解析后的内容：{content}")
                return content
            
            # 如果大模型直接返回了内容
            print(f"📤 直接返回API响应：{json.dumps(response, ensure_ascii=False, indent=2)}")
            # 详细记录content和reasoning_content的内容
            content_field = message.get("content", "").strip()
            reasoning_content_field = message.get("reasoning_content", "").strip()
            print(f"📋 直接返回时content字段内容: {'[空]' if not content_field else content_field[:100]}...")
            print(f"📋 直接返回时reasoning_content字段内容: {'[空]' if not reasoning_content_field else reasoning_content_field[:100]}...")
            # 优先使用content字段（最终输出结果），仅当content为空时才使用reasoning_content
            content = content_field or reasoning_content_field
            
            # 检查是否是DSML格式的工具调用
            if content and "<｜DSML｜function_calls>" in content:
                print("⚠️  检测到DSML格式工具调用请求，当前版本暂不支持DSML格式，回退到普通生成模式")
                return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
            
            print(f"📝 直接解析的内容：{content}")
            return content
        except Exception as e:
            print(f"❌ 处理工具响应时出错：{str(e)}")
            return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
    else:
        print("📝 本次生成将直接使用AI模型生成内容")
        # 不使用工具，直接调用大模型
        response = call_siliconflow_api(messages, temperature, timeout=60)
        if not response:
            return None
        
        try:
            print(f"📤 API返回原始响应：{json.dumps(response, ensure_ascii=False, indent=2)}")
            if "choices" in response and response["choices"]:
                message = response["choices"][0]["message"]
                # 优先使用content字段（最终输出结果），仅当content为空时才使用reasoning_content
                content = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
                
                # 检查是否是DSML格式的工具调用
                if content and "<｜DSML｜function_calls>" in content:
                    print("⚠️  检测到DSML格式工具调用请求，当前版本暂不支持DSML格式，回退到普通生成模式")
                    return generate_content_with_tools(messages, temperature, use_tool_prob=0.0, max_tool_calls=max_tool_calls, current_tool_calls=current_tool_calls)
                
                print(f"📝 解析后的内容：{content}")
                return content
            else:
                print("⚠️  API响应中没有choices字段或choices为空")
                return None
        except Exception as e:
            print(f"❌ 解析普通生成响应时出错：{str(e)}")
            import traceback
            traceback.print_exc()
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
            
            # 生成帖子内容（支持工具调用）
            messages = [
                {
                    "role": "system",
                    "content": f"你是复古论坛的用户「{author}」，在「{board_name}」板块发帖。你可以使用提供的工具来获取虚构的地点信息。生成的内容应尽量与现实世界保持距离，避免提及真实的地点、人名、事件或品牌。"
                },
                {
                    "role": "user",
                    "content": f'''请发一个关于「{theme}」的帖子，要求：
1. 标题：简洁明了，含「{theme}」关键词，不超过20字；
2. 内容：口语化，3-5句话，像真实用户提问/分享，贴合「{author}」昵称风格；
3. 风格：接地气、有生活气息，但内容必须是虚构的，不与现实对应；
4. 如果主题与地点相关（如租房、通勤、美食），请使用工具获取虚构地点信息，使帖子内容更有想象力；
5. 输出格式：先标题（换行）再内容，无多余字符。'''
                }
            ]
            
            content = generate_content_with_tools(messages)
            if not content:
                print("⚠️  generate_content_with_tools返回None")
                continue
            
            print(f"📥 从API获取到的完整内容：{repr(content)}")
            
            # 拆分标题和内容
            parts = [p.strip() for p in content.split("\n") if p.strip()]
            print(f"✂️  内容拆分为：{parts}")
            
            if len(parts) < 2:
                print(f"⚠️  帖子格式错误（{author}）：内容行数不足2行")
                continue
            title, post_content = parts[0], "\n".join(parts[1:])
            
            print(f"📝 提取的标题：{repr(title)}")
            print(f"📝 提取的内容：{repr(post_content)}")
            
            # 新增帖子到数据库
            print(f"💾 准备保存到数据库：标题={title[:20]}..., 作者={author}, 板块ID={board.id}")
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
            
            # 生成回复内容（支持工具调用）
            messages = [
                {
                    "role": "system",
                    "content": f"你是复古论坛的用户「{author}」，正在回复一个帖子。你可以使用提供的工具来获取虚构的地点信息。生成的内容应尽量与现实世界保持距离，避免提及真实的地点、人名、事件或品牌。"
                },
                {
                    "role": "user",
                    "content": f'''请回复以下帖子：
标题：{post.title}
内容：{post.content}
发帖人：{post.author}
要求：
1. 回复内容必须与帖子主题强相关
2. 口语化表达，1-3句话即可
3. 贴合「{author}」的昵称风格
4. 如果合适，可以使用工具获取虚构信息使回复更丰富
5. 回复内容必须是虚构的，不与现实对应
6. 只返回回复内容，不要包含任何额外格式或说明'''}
            ]
            
            reply_content = generate_content_with_tools(messages)
            if not reply_content:
                print("⚠️  generate_content_with_tools返回None")
                continue
            
            print(f"📥 从API获取到的完整回复：{repr(reply_content)}")
            
            # 简单清理：去除首尾空白
            final_content = reply_content.strip()
            
            # 如果清理后内容为空，跳过
            if not final_content:
                print(f"⚠️  清理后回复内容为空，跳过")
                continue
            
            print(f"✨ 清理后的最终回复内容：{repr(final_content)}")
            
            signatures = ["", "专注此事10年", "纯属个人经验", "欢迎交流～", "亲测有效！", "踩过坑分享"]
            signature = random.choice(signatures)
            
            # 新增回复到数据库
            print(f"💾 准备保存回复到数据库：内容={final_content[:20]}..., 作者={author}, 帖子ID={post.id}")
            new_reply = Reply(
                content=final_content,
                author=author,
                signature=signature,
                post_id=post.id,
                create_time=datetime.utcnow()
            )
            db.add(new_reply)
            db.commit()
            print(f"✅ 新增回复：《{post.title}》（{author}）")
            replied_count += 1
            time.sleep(1)
    except Exception as e:
        db.rollback()
        print(f"❌ 回复失败：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

# -------------------------- 主程序入口 --------------------------
def main():
    # 导入Flask应用和数据库实例
    from app import app, db
    
    # 创建并推送Flask应用上下文
    with app.app_context():
        # 先验证数据库连接
        if not test_db_connection():
            return
        
        print("🚀 启动AI内容生成器（支持工具调用）")
        print("可用工具：")
        for tool in tool_registry.list_tools():
            print(f"  - {tool.name()}: {tool.description()}")
        
        # 执行发帖（暂时注释掉，只测试回帖）
        print("\n📝 开始生成新帖子...")
        # generate_new_posts()  # 生成新帖子
        
        # 执行回帖
        print("\n💬 开始生成回复...")
        generate_replies()    # 生成回复
        
        print("\n✅ 已完成回帖，程序结束")

# 直接执行主函数
if __name__ == "__main__":
    main()