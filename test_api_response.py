import json
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def call_siliconflow_api_test(messages, temperature=0.7):
    """测试调用SiliconFlow API"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    api_key = os.getenv("SILICONFLOW_API_KEY")
    
    if not api_key:
        print("❌ 未设置SILICONFLOW_API_KEY环境变量")
        return None
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "Pro/deepseek-ai/DeepSeek-V3.2-Exp",
        "messages": messages,
        "temperature": temperature
    }
    
    try:
        print("📤 发送请求到SiliconFlow API...")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        print("📥 API响应：")
        print(json.dumps(response_data, ensure_ascii=False, indent=2))
        
        # 检查响应结构
        if "choices" in response_data and response_data["choices"]:
            message = response_data["choices"][0]["message"]
            print("\n📋 消息结构：")
            print(f"   - content字段存在: {'content' in message}")
            print(f"   - reasoning_content字段存在: {'reasoning_content' in message}")
            
            if "content" in message:
                print(f"   - content内容: {message['content'][:100]}..." if len(message['content']) > 100 else f"   - content内容: {message['content']}")
            
            if "reasoning_content" in message:
                print(f"   - reasoning_content内容: {message['reasoning_content'][:100]}..." if len(message['reasoning_content']) > 100 else f"   - reasoning_content内容: {message['reasoning_content']}")
        
        return response_data
    except Exception as e:
        print(f"❌ API调用出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# 测试用例1：简单对话
print("\n=== 测试用例1：简单对话 ===")
messages1 = [
    {"role": "system", "content": "你是一个友好的助手。"},
    {"role": "user", "content": "你好，今天天气怎么样？"}
]
call_siliconflow_api_test(messages1)

# 测试用例2：复杂思考任务
print("\n=== 测试用例2：复杂思考任务 ===")
messages2 = [
    {"role": "system", "content": "你是一个数学老师。"},
    {"role": "user", "content": "解释一下微积分中的导数概念，并给出一个例子。"}
]
call_siliconflow_api_test(messages2)