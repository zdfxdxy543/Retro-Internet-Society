import os
import logging
import json
import requests
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ShopAIAPITest')

class ShopAIAPITest:
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('SILICON_FLOW_API_KEY', 'sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv')
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.test_mode = False  # 明确设置为不使用测试模式
        
        # 如果没有配置API密钥，提示用户
        if not self.api_key:
            logger.warning("警告: 未设置SILICON_FLOW_API_KEY环境变量，API调用可能会失败")
    
    def test_api_connection(self):
        """测试API连接"""
        logger.info("测试API连接...")
        
        if self.test_mode:
            logger.info("当前在测试模式下，不会发送真实API请求")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送一个简单的请求测试API连接
            test_prompt = "你是谁？请用一句话简单介绍自己。"
            data = {
                "model": "Pro/deepseek-ai/DeepSeek-V3.2-Exp",
                "messages": [{"role": "user", "content": test_prompt}],
                "temperature": 0.7,
                "max_tokens": 50  # 限制响应长度
            }
            
            logger.info(f"[API调用] 发送测试请求到 {self.api_url}")
            logger.info(f"[请求参数] model: {data['model']}, 提示词长度: {len(test_prompt)} 字符")
            
            start_time = time.time()
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            end_time = time.time()
            
            logger.info(f"[API响应] 状态码: {response.status_code}, 响应时间: {end_time - start_time:.2f}秒")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.info(f"[响应内容] 成功获取JSON响应，格式正确")
                    if 'choices' in response_data and response_data['choices']:
                        message = response_data['choices'][0]['message'].get('content', '')
                        logger.info(f"[生成内容] {message.strip()}")
                    else:
                        logger.warning("[响应内容] 响应中没有找到choices字段")
                        logger.info(f"[完整响应] {json.dumps(response_data, ensure_ascii=False)}")
                except json.JSONDecodeError as e:
                    logger.error(f"[JSON解析错误] 无法解析响应: {str(e)}")
                    logger.info(f"[原始响应] {response.text}")
            else:
                logger.error(f"[API错误] 请求失败，状态码: {response.status_code}")
                logger.info(f"[错误详情] {response.text}")
                
            return response.status_code == 200
        except Exception as e:
            logger.error(f"[请求异常] 发送请求时发生错误: {str(e)}")
            return False
    
    def generate_product_data(self, category_name="电子产品", merchant_name="测试商家"):
        """生成商品数据"""
        logger.info(f"生成商品数据: 分类={category_name}, 商家={merchant_name}")
        
        if self.test_mode:
            # 测试模式下返回模拟数据
            mock_data = {
                "name": f"{category_name}二手商品",
                "description": "这是一个由系统自动生成的二手商品，成色良好，功能正常。",
                "price": 599,
                "image_count": 2,
                "tags": [category_name, "二手", "自动生成"]
            }
            logger.info(f"[测试模式] 返回模拟数据: {mock_data}")
            return mock_data
        
        # 真实API调用逻辑
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建详细的商品生成提示词
        prompt = f"""请生成一个{category_name}类别的二手商品数据，商家名称是{merchant_name}。
        返回格式必须是JSON，包含：name（商品名称）、description（商品描述）、price（价格，100-1000之间）、
        image_count（图片数量，1-3张）、tags（标签数组，3-5个）。
        请确保JSON格式正确，不要包含任何其他文本。"""
        
        data = {
            "model": "Pro/deepseek-ai/DeepSeek-V3.2-Exp",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            logger.info(f"[API调用] 发送商品生成请求...")
            start_time = time.time()
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            end_time = time.time()
            
            logger.info(f"[API响应] 状态码: {response.status_code}, 响应时间: {end_time - start_time:.2f}秒")
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and response_data['choices']:
                    product_content = response_data['choices'][0]['message'].get('content', '')
                    logger.info(f"[响应内容] 获取到生成内容: {product_content.strip()}")
                    
                    # 尝试解析JSON
                    try:
                        product_data = json.loads(product_content)
                        logger.info(f"[JSON解析] 成功解析商品数据: {product_data}")
                        return product_data
                    except json.JSONDecodeError as e:
                        logger.error(f"[JSON解析错误] 无法解析生成的内容为JSON: {str(e)}")
                        logger.info(f"[原始内容] {product_content}")
                else:
                    logger.warning("[响应内容] 响应中没有找到choices字段")
            else:
                logger.error(f"[API错误] 请求失败: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"[请求异常] 调用商品生成API时发生错误: {str(e)}")
        
        # API调用失败时返回默认数据
        default_data = {
            "name": f"{category_name}二手商品",
            "description": "这是一个二手商品，功能完好，品质保证。",
            "price": 699,
            "image_count": 2,
            "tags": [category_name, "二手", "推荐"]
        }
        logger.info(f"[失败回退] 使用默认商品数据: {default_data}")
        return default_data

if __name__ == "__main__":
    # 创建测试实例
    tester = ShopAIAPITest()
    
    print("\n===== ShopAI 真实API测试工具 =====")
    print(f"当前模式: {'测试模式' if tester.test_mode else '真实API调用模式'}")
    print(f"API URL: {tester.api_url}")
    # 添加硬编码的API密钥 - 根据用户要求设置
    # 用户表示已提供API，这里使用一个示例密钥，实际使用时请替换
    # 如果运行时设置了环境变量，会覆盖这个值
    # tester.set_api_key("your_api_key_here")  # 用户需要替换为实际的API密钥
    print(f"API密钥状态: {'已设置' if tester.api_key else '未设置'}")
    print("====================================\n")
    
    # 1. 测试API连接
    print("1. 测试API连接")
    print("-" * 30)
    tester.test_api_connection()
    print()
    
    # 2. 测试商品数据生成
    print("2. 测试商品数据生成")
    print("-" * 30)
    product_data = tester.generate_product_data()
    print(f"生成的商品数据: {json.dumps(product_data, ensure_ascii=False, indent=2)}")
    print()
    
    # 3. 测试不同类别商品生成
    print("3. 测试不同类别商品生成")
    print("-" * 30)
    categories = ["家居生活", "数码配件", "服饰鞋包"]
    
    for category in categories:
        print(f"\n测试生成 {category} 类商品...")
        cat_product = tester.generate_product_data(category_name=category)
        print(f"结果: {cat_product['name']}")
    
    print("\n====================================")
    print("测试完成！如果API调用失败，请检查您的API密钥是否正确配置。")
    print(f"提示: 您可以通过设置环境变量 'SILICON_FLOW_API_KEY' 来配置API密钥")


