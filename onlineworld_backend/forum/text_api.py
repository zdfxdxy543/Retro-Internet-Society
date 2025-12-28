import requests

# 替换为你的配置
API_KEY = "sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv"
MODEL_NAME = "Pro/deepseek-ai/DeepSeek-V3.2-Exp"  # 替换为你开通的模型名
API_URL = "https://api.siliconflow.cn/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
data = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": "简洁回复"},
        {"role": "user", "content": "生成一个2字复古论坛用户名"}
    ],
    "temperature": 0.7,
    "max_tokens": 10
}

try:
    response = requests.post(API_URL, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    print("✅ API测试成功：", response.json())
except Exception as e:
    print("❌ API测试失败：", str(e))
    print("响应内容：", response.text if 'response' in locals() else '无')