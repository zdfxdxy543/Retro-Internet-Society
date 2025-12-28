import json
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入需要测试的函数
from onlineworld_backend.ai_content_generator import generate_reply

# 模拟数据库会话和模型
class MockSession:
    def query(self, *args):
        return self
    
    def filter(self, *args):
        return self
    
    def first(self):
        return None
    
    def all(self):
        return []
    
    def get(self, *args):
        return None

class MockPost:
    def __init__(self, id, title, content, board_id):
        self.id = id
        self.title = title
        self.content = content
        self.board_id = board_id
        self.author_id = 1
        self.created_at = "2023-01-01 00:00:00"
        self.updated_at = "2023-01-01 00:00:00"
        self.is_active = True
        self.likes = []
        self.comments = []

# 模拟Flask应用上下文
class MockApp:
    def __init__(self):
        self.config = {
            "SILICONFLOW_API_KEY": "mock_key"
        }
        self.extensions = {
            "sqlalchemy": {
                "db": MockSession()
            }
        }

class MockFlaskContext:
    def __init__(self):
        self.app = MockApp()
    
    def __enter__(self):
        return self.app
    
    def __exit__(self, *args):
        pass

# 替换掉实际的API调用
def mock_call_siliconflow_api(messages, temperature=0.7, tools=None):
    """模拟API调用"""
    print(f"📤 模拟API调用，消息: {json.dumps(messages[-1], ensure_ascii=False)}")
    print(f"   使用工具: {tools is not None}")
    
    # 根据不同情况返回不同的响应
    if tools:
        # 模拟工具调用后的响应
        return {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "reasoning_content": "根据查询结果，我来回答这个问题。这是关于产品A的详细信息..."
                    }
                }
            ]
        }
    else:
        # 模拟普通响应
        return {
            "choices": [
                {
                    "message": {
                        "content": "这是最终的回复内容，使用了工具查询的信息。"
                    }
                }
            ]
        }

# 测试回复生成函数
def test_reply_generation():
    """测试回复生成函数"""
    print("=== 测试回复生成函数 ===")
    
    # 创建测试帖子
    test_post = MockPost(
        id=1,
        title="测试帖子",
        content="这是一个测试帖子，讨论产品A。",
        board_id=1
    )
    
    try:
        # 替换实际的API调用
        import onlineworld_backend.ai_content_generator as acg
        original_api_call = acg.call_siliconflow_api
        acg.call_siliconflow_api = mock_call_siliconflow_api
        
        # 调用生成回复函数
        reply_content = generate_reply(test_post, temperature=0.7)
        
        print(f"📝 生成的回复内容: {reply_content}")
        
        # 恢复原函数
        acg.call_siliconflow_api = original_api_call
        
        return reply_content
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_reply_generation()