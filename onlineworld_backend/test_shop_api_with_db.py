import os
import logging
import json
import requests
import time
from datetime import datetime
import sys

# 添加项目根目录到sys.path，确保模块导入正确
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ShopAIWithDBTest')

# 导入数据库和模型
from forum.models import db, ShopCategory, ShopMerchant, ShopProduct
from flask import Flask

class ShopAIWithDBTest:
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('SILICON_FLOW_API_KEY', 'sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv')
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.test_mode = False  # 明确设置为不使用测试模式
        
        # 初始化Flask应用和数据库
        self.app = Flask(__name__)
        
        # 数据库配置
        app_root = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(app_root, 'instance', 'forum.db')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or f'sqlite:///{db_path.replace(chr(92), "/")}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        
        # 初始化数据库
        db.init_app(self.app)
        
        # 在应用上下文中创建数据库表
        with self.app.app_context():
            db.create_all()
            
        # 如果没有配置API密钥，提示用户
        if not self.api_key:
            logger.warning("警告: 未设置SILICON_FLOW_API_KEY环境变量，API调用可能会失败")
    
    def generate_product_data(self, category_name="电子产品", merchant_name="测试商家"):
        """生成商品数据"""
        logger.info(f"生成商品数据: 分类={category_name}, 商家={merchant_name}")
        
        # 默认商品数据，当API调用失败时使用
        default_data = {
            "name": f"{category_name}二手商品",
            "description": "这是一个由系统自动生成的二手商品，成色良好，功能正常。",
            "price": 599,
            "image_count": 2,
            "tags": [category_name, "二手", "自动生成"]
        }
        
        if self.test_mode or not self.api_key:
            logger.info(f"[测试模式/无API密钥] 返回默认数据: {default_data}")
            return default_data
        
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
        logger.info(f"[失败回退] 使用默认商品数据: {default_data}")
        return default_data
    
    def save_product_to_db(self, product_data, merchant_name, category_name):
        """将商品数据保存到数据库"""
        with self.app.app_context():
            try:
                # 查找或创建商家 - 在同一个事务中处理
                merchant = ShopMerchant.query.filter_by(name=merchant_name).first()
                if not merchant:
                    merchant = ShopMerchant(
                        name=merchant_name,
                        description=f"商家{merchant_name}的店铺",
                        is_active=True
                    )
                    db.session.add(merchant)
                    logger.info(f"创建新商家: {merchant_name}")
                
                # 查找或创建分类 - 在同一个事务中处理
                category = ShopCategory.query.filter_by(name=category_name).first()
                if not category:
                    category = ShopCategory(
                        name=category_name,
                        description=f"{category_name}分类",
                        is_active=True
                    )
                    db.session.add(category)
                    logger.info(f"创建新分类: {category_name}")
                
                # 提交到这一步，确保商家和分类已持久化
                db.session.flush()
                
                # 创建商品
                product = ShopProduct(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data.get('price', 599),
                    merchant_id=merchant.id,
                    category_id=category.id,
                    is_active=True,
                    tags=product_data.get('tags', [])
                )
                
                # 添加到数据库并提交
                db.session.add(product)
                db.session.commit()
                
                logger.info(f"成功保存商品到数据库: {product_data['name']} (ID: {product.id})")
                return True
            except Exception as e:
                db.session.rollback()
                logger.error(f"保存商品到数据库时出错: {str(e)}")
                return False
    
    def count_products_in_db(self):
        """统计数据库中的商品数量"""
        with self.app.app_context():
            try:
                count = ShopProduct.query.count()
                logger.info(f"当前数据库中商品总数: {count}")
                return count
            except Exception as e:
                logger.error(f"统计商品数量时出错: {str(e)}")
                return 0
    
    def test_save_to_database(self, count=3):
        """测试保存商品数据到数据库"""
        logger.info(f"开始测试：生成并保存{count}个商品到数据库")
        
        # 记录开始前的商品数量
        before_count = self.count_products_in_db()
        
        # 测试类别和商家
        categories = ["家居生活", "数码配件", "服饰鞋包"]
        merchants = ["精品二手店", "诚信商家", "优品折扣"]
        
        success_count = 0
        
        for i in range(count):
            category = categories[i % len(categories)]
            merchant = merchants[i % len(merchants)]
            
            logger.info(f"\n===== 商品 {i+1}/{count} =====")
            logger.info(f"类别: {category}, 商家: {merchant}")
            
            # 生成商品数据
            product_data = self.generate_product_data(category, merchant)
            
            # 保存到数据库
            if self.save_product_to_db(product_data, merchant, category):
                success_count += 1
                logger.info("✓ 商品保存成功")
            else:
                logger.error("✗ 商品保存失败")
        
        # 记录结束后的商品数量
        after_count = self.count_products_in_db()
        
        logger.info(f"\n===== 测试结果 =====")
        logger.info(f"开始前商品数量: {before_count}")
        logger.info(f"结束后商品数量: {after_count}")
        logger.info(f"成功保存: {success_count}/{count} 个商品")
        logger.info(f"净新增商品: {after_count - before_count} 个")
        
        return {
            "total_attempts": count,
            "successful_saves": success_count,
            "before_count": before_count,
            "after_count": after_count,
            "net_additions": after_count - before_count
        }

if __name__ == "__main__":
    # 创建测试实例
    tester = ShopAIWithDBTest()
    
    print("\n===== ShopAI 真实API与数据库测试工具 =====")
    print(f"当前模式: {'测试模式' if tester.test_mode else '真实API调用模式'}")
    print(f"API URL: {tester.api_url}")
    print(f"API密钥状态: {'已设置' if tester.api_key else '未设置'}")
    print(f"数据库路径: {tester.app.config['SQLALCHEMY_DATABASE_URI']}")
    print("===========================================\n")
    
    # 测试保存商品到数据库
    print("1. 测试商品生成和数据库存储")
    print("-" * 50)
    result = tester.test_save_to_database(count=3)
    
    print("\n===== 总结 =====")
    print(f"测试完成！生成并尝试保存 {result['total_attempts']} 个商品")
    print(f"成功保存到数据库: {result['successful_saves']} 个商品")
    print(f"数据库中商品数量净增: {result['net_additions']} 个")
    
    if result['successful_saves'] > 0:
        print("\n✓ 测试成功: 商品数据已成功保存到数据库")
    else:
        print("\n✗ 测试失败: 未能将商品数据保存到数据库，请检查错误日志")
    
    print("\n提示: 如果API调用失败，可以通过设置SILICON_FLOW_API_KEY环境变量来配置正确的API密钥")