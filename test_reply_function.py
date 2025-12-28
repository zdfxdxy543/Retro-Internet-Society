import json
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 模拟API响应
mock_responses = {
    "case1": {
        "choices": [
            {
                "message": {
                    "content": "这是最终的回复内容",
                    "reasoning_content": "我正在思考如何回答这个问题..."
                }
            }
        ]
    },
    "case2": {
        "choices": [
            {
                "message": {
                    "content": "",
                    "reasoning_content": "这是最终的回复内容"
                }
            }
        ]
    },
    "case3": {
        "choices": [
            {
                "message": {
                    "reasoning_content": "这是最终的回复内容"
                }
            }
        ]
    },
    "case4": {
        "choices": [
            {
                "message": {
                    "content": "这是最终的回复内容"
                }
            }
        ]
    }
}

def test_content_extraction():
    """测试内容提取逻辑"""
    print("=== 测试内容提取逻辑 ===")
    
    for case_name, response in mock_responses.items():
        print(f"\n📋 测试用例: {case_name}")
        print(f"   API响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        message = response["choices"][0]["message"]
        
        # 当前代码的提取逻辑
        content = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
        
        print(f"   提取的内容: {content}")
        print(f"   是否正确: {'是' if content == '这是最终的回复内容' else '否'}")

# 测试generate_content_with_tools函数的逻辑
def test_generate_content_logic():
    """测试generate_content_with_tools函数的逻辑"""
    print("\n=== 测试generate_content_with_tools逻辑 ===")
    
    # 模拟工具调用后的响应处理
    mock_response = mock_responses["case1"]
    message = mock_response["choices"][0]["message"]
    
    # 第379行的处理逻辑
    content1 = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
    print(f"📝 第379行处理结果: {content1}")
    
    # 第392行的处理逻辑
    content2 = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
    print(f"📝 第392行处理结果: {content2}")
    
    # 第416行的处理逻辑
    content3 = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
    print(f"📝 第416行处理结果: {content3}")

if __name__ == "__main__":
    test_content_extraction()
    test_generate_content_logic()