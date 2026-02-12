import json
import time
import random
import logging
from datetime import datetime
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入现有功能
from ai_content_generator import call_siliconflow_api, generate_content_with_tools, select_author
from forum.disk_file_generator import DiskFileGenerator
from forum.models import Post, Reply, Board, db
from app import app

class ResourcePool:
    """资源池，用于存储中间生成结果"""
    
    def __init__(self):
        self.resources = {}
    
    def add_resource(self, step_id, resource_data):
        """添加资源到资源池"""
        self.resources[step_id] = resource_data
        logger.info(f"资源添加成功：{step_id} - {resource_data}")
    
    def get_resource(self, step_id):
        """从资源池获取资源"""
        return self.resources.get(step_id)
    
    def get_all_resources(self):
        """获取所有资源"""
        return self.resources
    
    def clear(self):
        """清空资源池"""
        self.resources.clear()

class StepExecutor(ABC):
    """步骤执行器抽象类"""
    
    @abstractmethod
    def execute(self, step, resource_pool):
        """执行步骤"""
        pass

class DiskFileExecutor(StepExecutor):
    """网盘文件执行器"""
    
    def execute(self, step, resource_pool):
        """执行网盘文件生成"""
        try:
            params = step.get('params', {})
            content = params.get('content', '')
            file_name = params.get('file_name', f"ai-generated-{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            file_extension = params.get('file_extension', 'txt')
            
            # 使用现有 DiskFileGenerator
            with app.app_context():
                disk_generator = DiskFileGenerator(db, app.config)
                result = disk_generator.generate_disk_file(
                    content=content,
                    file_name=file_name,
                    file_extension=file_extension
                )
            
            logger.info(f"网盘文件生成成功：{result['file_name']}")
            return result
        except Exception as e:
            logger.error(f"网盘文件生成失败：{str(e)}")
            raise

class PostExecutor(StepExecutor):
    """帖子执行器"""
    
    def execute(self, step, resource_pool):
        """执行帖子生成"""
        try:
            params = step.get('params', {})
            board_id = params.get('board_id', 1)
            title = params.get('title', '未命名帖子')
            use_resources = params.get('use_resources', [])
            
            # 获取资源
            resources = {}
            for resource_id in use_resources:
                resource = resource_pool.get_resource(resource_id)
                if resource:
                    resources[resource_id] = resource
            
            # 生成帖子内容
            author = select_author()
            
            # 获取板块信息
            with app.app_context():
                board = Board.query.get(board_id)
                board_name = board.name if board else "技术讨论区"
            
            # 构建提示词
            resource_info = ""
            if resources:
                for resource_id, resource_data in resources.items():
                    if resource_data.get('share_id'):
                        resource_info += f"\n资源链接：分享号 {resource_data['share_id']}，密码 {resource_data['password']}，文件名 {resource_data['file_name']}"
            
            messages = [
                {
                    "role": "system",
                    "content": f"你是复古论坛的用户「{author}」，在「{board_name}」板块发帖。生成的内容应尽量与现实世界保持距离，避免提及真实的地点、人名、事件或品牌。"
                },
                {
                    "role": "user",
                    "content": f"请发一个关于「{title}」的帖子，要求：\n1. 标题：{title}\n2. 内容：口语化，3-5句话，像真实用户提问/分享，贴合「{author}」昵称风格；\n3. 风格：接地气、有生活气息，符合现实，但内容中提到的地名与现实无关；\n4. 如果有以下资源，请在帖子中合理使用：{resource_info}\n5. 输出格式：先标题（换行）再内容，无多余字符。"
                }
            ]
            
            # 使用现有 generate_content_with_tools 函数
            content = generate_content_with_tools(messages)
            
            # 拆分标题和内容
            parts = [p.strip() for p in content.split('\n') if p.strip()]
            if len(parts) < 2:
                raise ValueError("帖子格式错误")
            post_title, post_content = parts[0], '\n'.join(parts[1:])
            
            # 保存到数据库
            with app.app_context():
                new_post = Post(
                    title=post_title,
                    content=post_content,
                    author=author,
                    board_id=board_id,
                    create_time=datetime.utcnow()
                )
                db.session.add(new_post)
                db.session.commit()
            
            result = {
                "id": new_post.id,
                "title": new_post.title,
                "content": new_post.content,
                "author": new_post.author,
                "board_id": new_post.board_id,
                "create_time": new_post.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"帖子生成成功：{result['title']}")
            return result
        except Exception as e:
            logger.error(f"帖子生成失败：{str(e)}")
            raise

class ReplyExecutor(StepExecutor):
    """回复执行器"""
    
    def execute(self, step, resource_pool):
        """执行回复生成"""
        try:
            params = step.get('params', {})
            post_id = params.get('post_id')
            content = params.get('content', '')
            use_resources = params.get('use_resources', [])
            
            # 处理依赖步骤
            if isinstance(post_id, str) and post_id.startswith('step_'):
                post_resource = resource_pool.get_resource(post_id)
                if post_resource:
                    post_id = post_resource.get('id')
                else:
                    raise ValueError(f"依赖的帖子资源不存在：{post_id}")
            
            # 获取资源
            resources = {}
            for resource_id in use_resources:
                resource = resource_pool.get_resource(resource_id)
                if resource:
                    resources[resource_id] = resource
            
            # 获取帖子信息
            with app.app_context():
                post = Post.query.get(post_id)
                if not post:
                    raise ValueError(f"帖子不存在：{post_id}")
            
            # 生成回复
            author = select_author(exclude_author=post.author)
            
            # 构建提示词
            messages = [
                {
                    "role": "system",
                    "content": f"你是复古论坛的用户「{author}」，正在回复一个帖子。生成的内容应尽量与现实世界保持距离，避免提及真实的地点、人名、事件或品牌。"
                },
                {
                    "role": "user",
                    "content": f"请回复以下帖子：\n标题：{post.title}\n内容：{post.content}\n发帖人：{post.author}\n要求：\n1. 回复内容必须与帖子主题强相关\n2. 口语化表达，1-3句话即可\n3. 贴合「{author}」的昵称风格\n4. 回复内容必须是虚构的，不与现实对应\n5. 只返回回复内容，不要包含任何额外格式或说明"
                }
            ]
            
            # 使用现有 generate_content_with_tools 函数
            reply_content = generate_content_with_tools(messages)
            final_content = reply_content.strip()
            
            if not final_content:
                raise ValueError("回复内容为空")
            
            # 保存到数据库
            with app.app_context():
                new_reply = Reply(
                    content=final_content,
                    author=author,
                    signature="",
                    post_id=post_id,
                    create_time=datetime.utcnow()
                )
                db.session.add(new_reply)
                db.session.commit()
            
            result = {
                "id": new_reply.id,
                "content": new_reply.content,
                "author": new_reply.author,
                "post_id": new_reply.post_id,
                "create_time": new_reply.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"回复生成成功")
            return result
        except Exception as e:
            logger.error(f"回复生成失败：{str(e)}")
            raise

class AIScheduler:
    """AI调度器"""
    
    def __init__(self):
        self.resource_pool = ResourcePool()
        self.executors = {
            'disk_file': DiskFileExecutor(),
            'post': PostExecutor(),
            'reply': ReplyExecutor()
        }
    
    def register_executor(self, step_type, executor):
        """注册新的执行器"""
        self.executors[step_type] = executor
        logger.info(f"执行器注册成功：{step_type}")
    
    def generate_execution_plan(self, task_description):
        """生成执行计划"""
        try:
            # 调用API生成执行步骤
            # 构建示例JSON字符串
            example_json = '''
{
  "steps": [
    {
      "id": "step_1",
      "type": "disk_file",
      "params": {
        "content": "文件内容",
        "file_name": "文件名"
      }
    },
    {
      "id": "step_2",
      "type": "post",
      "params": {
        "board_id": 1,
        "title": "帖子标题",
        "use_resources": ["step_1"]
      }
    }
  ]
}
'''
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个AI任务调度器，负责将用户的任务分解为可执行的步骤序列。每个步骤应该是独立的，可以是以下类型之一：disk_file（生成网盘文件）、post（生成帖子）、reply（生成回复）。步骤之间可以有依赖关系，通过use_resources字段指定。"
                },
                {
                    "role": "user",
                    "content": f"请为以下任务生成执行步骤序列：{task_description}\n\n输出格式必须是JSON，包含steps数组，每个步骤包含id、type和params字段。例如：{example_json}"
                }
            ]
            
            response = call_siliconflow_api(messages, temperature=0.7)
            
            if response and "choices" in response:
                content = response["choices"][0]["message"].get("content", "")
                # 提取JSON部分
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    plan = json.loads(json_match.group(0))
                    logger.info(f"执行计划生成成功：{plan}")
                    return plan
            
            # 默认计划
            default_plan = {
                "steps": [
                    {
                        "id": "step_1",
                        "type": "post",
                        "params": {
                            "board_id": 1,
                            "title": task_description[:50]
                        }
                    }
                ]
            }
            logger.warning(f"使用默认执行计划：{default_plan}")
            return default_plan
        except Exception as e:
            logger.error(f"执行计划生成失败：{str(e)}")
            # 返回默认计划
            return {
                "steps": [
                    {
                        "id": "step_1",
                        "type": "post",
                        "params": {
                            "board_id": 1,
                            "title": task_description[:50]
                        }
                    }
                ]
            }
    
    def execute_plan(self, plan):
        """执行计划"""
        try:
            results = {}
            steps = plan.get('steps', [])
            
            for step in steps:
                step_id = step.get('id')
                step_type = step.get('type')
                
                logger.info(f"执行步骤：{step_id} ({step_type})")
                
                # 获取执行器
                executor = self.executors.get(step_type)
                if not executor:
                    logger.error(f"未知的步骤类型：{step_type}")
                    continue
                
                # 执行步骤
                result = executor.execute(step, self.resource_pool)
                
                # 保存结果到资源池
                if result:
                    self.resource_pool.add_resource(step_id, result)
                    results[step_id] = result
                
                # 避免API调用过于频繁
                time.sleep(1)
            
            logger.info(f"执行计划完成，共执行 {len(results)} 个步骤")
            return results
        except Exception as e:
            logger.error(f"执行计划失败：{str(e)}")
            raise
    
    def run_task(self, task_description, parameters=None):
        """运行任务"""
        try:
            # 生成执行计划
            plan = self.generate_execution_plan(task_description)
            
            # 合并参数
            if parameters:
                for step in plan.get('steps', []):
                    step['params'].update(parameters)
            
            # 执行计划
            results = self.execute_plan(plan)
            
            # 清空资源池
            self.resource_pool.clear()
            
            return {
                "status": "success",
                "result": results
            }
        except Exception as e:
            logger.error(f"任务运行失败：{str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

# 创建全局调度器实例
aI_scheduler = AIScheduler()
