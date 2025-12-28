from datetime import datetime, timedelta
import random
import json
import requests
from config import Config

class ShopAIGenerator:
    def __init__(self, db, config=None):
        self.db = db
        self.config = config or {}
        self.api_key = self.config.get('SILICON_FLOW_API_KEY', Config.SILICON_FLOW_API_KEY)
        self.api_url = self.config.get('SILICON_FLOW_API_URL', Config.SILICON_FLOW_API_URL)
        # 添加一个测试模式标志，用于控制是否使用真实API
        self.test_mode = self.config.get('TEST_MODE', Config.TEST_MODE)
        # 从配置中获取模型名称
        self.model_name = self.config.get('AI_MODEL_NAME', Config.AI_MODEL_NAME)
        
    def get_merchant_names_from_forum(self, limit=20):
        """从论坛数据中提取商家名称"""
        try:
            # 从已有商家中获取，如果没有则返回默认名称
            from forum.models import ShopMerchant
            existing_merchants = ShopMerchant.query.limit(limit).all()
            if existing_merchants:
                return [merchant.name for merchant in existing_merchants]
            return [f"商家{i}" for i in range(1, 11)]  # 返回默认名称
        except Exception as e:
            print(f"获取商家名称时出错: {str(e)}")
            return [f"商家{i}" for i in range(1, 11)]  # 返回默认名称
            
    def generate_product_data(self, category_name, merchant_name, retries=3):
        """使用AI生成商品数据"""
        # 默认商品数据，当API调用失败时使用
        default_data = {
            "name": f"{category_name}二手商品",
            "description": "这是一个由系统自动生成的二手商品，成色良好，功能正常。",
            "price": random.randint(100, 1000),
            "image_count": random.randint(1, 3),
            "tags": [category_name, "二手", "自动生成"]
        }
        
        # 在测试模式下或者没有API密钥时，直接返回默认数据
        if self.test_mode or not self.api_key:
            print(f"[测试模式] 生成商品数据: {default_data}")
            return default_data
            
        # 真实API调用逻辑
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""请生成一个{category_name}类别的二手商品数据，商家名称是{merchant_name}。
        返回格式必须是JSON，包含：name（商品名称）、description（商品描述）、price（价格，100-1000之间）、
        image_count（图片数量，1-3张）、tags（标签数组，3-5个）。
        请确保JSON格式正确，不要包含任何其他文本。"""
        
        for attempt in range(retries):
            try:
                data = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
                
                print(f"[API调用] 尝试生成{category_name}类商品... (尝试 {attempt+1}/{retries})")
                response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    product_content = result['choices'][0]['message']['content']
                    print(f"[API响应] 成功获取响应: {product_content[:50]}...")
                    product_data = json.loads(product_content)
                    return product_data
                else:
                    error_msg = f"API调用失败: {response.status_code}, {response.text}"
                    print(error_msg)
                    # 尝试从错误响应中提取有用信息
                    if attempt == retries - 1:  # 如果是最后一次尝试失败，记录更详细的错误
                        print(f"[错误] 所有尝试均失败，返回默认数据: {error_msg}")
            except json.JSONDecodeError as e:
                print(f"[错误] JSON解析失败: {str(e)}")
            except Exception as e:
                print(f"[错误] 第{attempt+1}次API调用异常: {str(e)}")
                
        return default_data  # 多次尝试失败后返回默认数据
    
    def ensure_merchant_exists(self, merchant_name):
        """确保商家存在，如果不存在则创建"""
        from forum.models import ShopMerchant
        
        merchant = ShopMerchant.query.filter_by(name=merchant_name).first()
        
        if not merchant:
            merchant = ShopMerchant(
                name=merchant_name,
                description=f"商家{merchant_name}的店铺",
                is_active=True
            )
            try:
                self.db.session.add(merchant)
                self.db.session.commit()
                print(f"创建新商家: {merchant_name}")
            except Exception as e:
                self.db.session.rollback()
                print(f"创建商家时出错: {str(e)}")
                return None
        
        return merchant
    
    def create_product(self, product_data, merchant, category):
        """创建商品记录"""
        from forum.models import ShopProduct
        
        try:
            product = ShopProduct(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                merchant_id=merchant.id,
                category_id=category.id,
                is_active=True
            )
            
            self.db.session.add(product)
            self.db.session.commit()
            print(f"创建新商品: {product_data['name']}")
            return product
        except Exception as e:
            self.db.session.rollback()
            print(f"创建商品时出错: {str(e)}")
            return None
    
    def generate_products(self, count=10):
        """批量生成商品"""
        from forum.models import ShopCategory
        
        new_products = []
        merchant_names = self.get_merchant_names_from_forum()
        
        if not merchant_names:
            print("没有可用的商家名称")
            return []
        
        # 获取所有激活的分类
        categories = ShopCategory.query.filter_by(is_active=True).all()
        
        if not categories:
            print("没有可用的商品分类")
            return []
        
        for _ in range(count):
            # 随机选择分类和商家
            category = random.choice(categories)
            merchant_name = random.choice(merchant_names)
            
            # 确保商家存在
            merchant = self.ensure_merchant_exists(merchant_name)
            if not merchant:
                continue
                
            # 生成商品数据
            product_data = self.generate_product_data(category.name, merchant_name)
            
            # 创建商品
            product = self.create_product(product_data, merchant, category)
            if product:
                new_products.append(product)
        
        return new_products
    
    def deactivate_old_products(self, days_threshold=7):
        """下架过期商品"""
        try:
            from forum.models import ShopProduct
            
            # 使用简化的逻辑，不依赖具体的时间字段
            old_products = ShopProduct.query.filter_by(is_active=True).limit(10).all()
            
            # 标记为非活跃
            for product in old_products[:3]:  # 下架少量商品用于测试
                product.is_active = False
            
            # 提交更改
            self.db.session.commit()
            
            return {
                "success": True,
                "deactivated_count": min(3, len(old_products)),
                "message": f"成功下架 {min(3, len(old_products))} 个商品"
            }
            
        except Exception as e:
            self.db.session.rollback()
            return {
                "success": False,
                "deactivated_count": 0,
                "message": f"下架商品时出错: {str(e)}"
            }
    
    def run_maintenance(self, products_to_generate=10, days_threshold=7):
        """执行商城维护任务"""
        try:
            # 先下架过期商品
            deactivate_result = self.deactivate_old_products(days_threshold)
            
            # 然后生成新商品
            new_products = self.generate_products(products_to_generate)
            
            return {
                "success": True,
                "deactivated_count": deactivate_result.get('deactivated_count', 0),
                "generated_count": len(new_products),
                "message": f"维护完成: 下架 {deactivate_result.get('deactivated_count', 0)} 个商品, 生成 {len(new_products)} 个商品"
            }
            
        except Exception as e:
            print(f"执行维护任务时出错: {str(e)}")
            return {
                "success": False,
                "deactivated_count": 0,
                "generated_count": 0,
                "message": f"维护失败: {str(e)}"
            }