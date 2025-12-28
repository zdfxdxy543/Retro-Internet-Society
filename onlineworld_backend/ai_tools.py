import json
from abc import ABC, abstractmethod
from forum.models import Post, Reply, Board, CompanyInfo, ProductCategory, Product, AIMapRegion, AIMapAIInfo, ShopCategory, ShopMerchant, ShopProduct
from sqlalchemy import or_
import sys
import os

# 添加项目根目录到Python路径，确保能找到forum模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 尝试导入已创建的Flask应用和数据库实例
# 注意：这个导入需要在Flask应用已创建的上下文中使用
try:
    from app import app, db
    # 不需要再创建新的应用实例或推送上下文
    # 让调用者负责创建应用上下文
except ImportError:
    print("⚠️  无法从app导入Flask应用，工具将尝试直接导入数据库实例")
    try:
        from forum.models import db
        app = None
    except ImportError:
        print("⚠️  无法导入数据库实例，工具将使用原生SQLAlchemy方式运行")
        app = None
        db = None

class BaseTool(ABC):
    """基础工具类，定义工具接口"""
    
    @abstractmethod
    def name(self):
        """工具名称"""
        pass
    
    @abstractmethod
    def description(self):
        """工具描述"""
        pass
    
    @abstractmethod
    def parameters(self):
        """工具参数定义，用于大模型理解"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs):
        """执行工具逻辑"""
        pass

    def get_session(self):
        """获取数据库会话，兼容Flask应用上下文和原生SQLAlchemy方式"""
        if app:
            # 直接返回db.session，假设调用者已经创建了应用上下文
            # 如果没有上下文，调用者需要在使用工具前创建应用上下文
            return db.session
        else:
            # 使用原生SQLAlchemy会话
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from config import Config
            
            engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return SessionLocal()

class ForumInfoTool(BaseTool):
    """论坛信息获取工具"""
    
    def name(self):
        return "get_forum_info"
    
    def description(self):
        return "获取论坛信息的工具，可以查询帖子、用户或板块信息"
    
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "查询类型，可以是：posts（帖子）、users（用户）、boards（板块）",
                    "enum": ["posts", "users", "boards"]
                },
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，可选参数"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制，默认10",
                    "default": 10
                }
            },
            "required": ["query_type"]
        }
    
    def execute(self, query_type, keyword="", limit=10):
        """获取论坛信息"""
        try:
            session = self.get_session()
            if query_type == "posts":
                # 查询帖子
                if keyword:
                    posts = session.query(Post).filter(
                        or_(Post.title.ilike(f'%{keyword}%'), Post.content.ilike(f'%{keyword}%'))
                    ).order_by(Post.create_time.desc()).limit(limit).all()
                else:
                    posts = session.query(Post).order_by(Post.create_time.desc()).limit(limit).all()
                
                results = [{"id": post.id,
                           "title": post.title,
                           "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                           "author": post.author,
                           "board_name": post.board.name,
                           "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                           "reply_count": len(post.replies)}
                          for post in posts]
                
                return json.dumps({
                    "success": True,
                    "type": "posts",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            elif query_type == "users":
                # 查询用户
                if keyword:
                    post_authors = session.query(Post.author).filter(Post.author.ilike(f'%{keyword}%')).distinct()
                    reply_authors = session.query(Reply.author).filter(Reply.author.ilike(f'%{keyword}%')).distinct()
                else:
                    post_authors = session.query(Post.author).distinct()
                    reply_authors = session.query(Reply.author).distinct()
                
                all_authors = set()
                for author in post_authors:
                    all_authors.add(author[0])
                for author in reply_authors:
                    all_authors.add(author[0])
                all_authors = list(all_authors)[:limit]
                
                results = []
                for author in all_authors:
                    post_count = session.query(Post).filter_by(author=author).count()
                    reply_count = session.query(Reply).filter_by(author=author).count()
                    results.append({"author": author,
                                   "post_count": post_count,
                                   "reply_count": reply_count})
                
                return json.dumps({
                    "success": True,
                    "type": "users",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            elif query_type == "boards":
                # 查询板块
                boards = session.query(Board).all()
                
                results = [{"id": board.id,
                           "name": board.name,
                           "description": board.description,
                           "post_count": len(board.posts)}
                          for board in boards[:limit]]
                
                return json.dumps({
                    "success": True,
                    "type": "boards",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            else:
                return json.dumps({
                    "success": False,
                    "error": f"无效的查询类型: {query_type}"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"查询失败: {str(e)}"
            }, ensure_ascii=False)

class CompanyInfoTool(BaseTool):
    """公司网页/产品信息获取工具"""
    
    def name(self):
        return "get_company_info"
    
    def description(self):
        return "获取公司网页/产品的信息，可以查询公司基本信息、产品分类或产品详情"
    
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "查询类型，可以是：company（公司信息）、categories（产品分类）、products（产品）",
                    "enum": ["company", "categories", "products"]
                },
                "product_id": {
                    "type": "integer",
                    "description": "产品ID，查询单个产品时使用"
                },
                "category_id": {
                    "type": "integer",
                    "description": "产品分类ID，查询某个分类下的产品时使用"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制，默认10",
                    "default": 10
                }
            },
            "required": ["query_type"]
        }
    
    def execute(self, query_type, product_id=None, category_id=None, limit=10):
        """获取公司网页/产品信息"""
        try:
            session = self.get_session()
            if query_type == "company":
                # 查询公司基本信息
                company_info = session.query(CompanyInfo).first()
                if not company_info:
                    return json.dumps({
                        "success": False,
                        "error": "未找到公司信息"
                    }, ensure_ascii=False)
                
                result = {
                    "id": company_info.id,
                    "name": company_info.name,
                    "description": company_info.description,
                    "founded_year": company_info.founded_year,
                    "address": company_info.address,
                    "phone": company_info.phone,
                    "email": company_info.email,
                    "website": company_info.website,
                    "slogan": company_info.slogan
                }
                
                return json.dumps({
                    "success": True,
                    "type": "company",
                    "result": result
                }, ensure_ascii=False)
                
            elif query_type == "categories":
                # 查询产品分类
                categories = session.query(ProductCategory).order_by(ProductCategory.order_num).all()
                
                results = [{"id": category.id,
                           "name": category.name,
                           "description": category.description,
                           "product_count": len(category.products)}
                          for category in categories[:limit]]
                
                return json.dumps({
                    "success": True,
                    "type": "categories",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            elif query_type == "products":
                # 查询产品
                if product_id:
                    # 查询单个产品
                    product = session.query(Product).get(product_id)
                    if not product:
                        return json.dumps({
                            "success": False,
                            "error": f"未找到ID为{product_id}的产品"
                        }, ensure_ascii=False)
                    
                    result = {
                        "id": product.id,
                        "name": product.name,
                        "model": product.model,
                        "description": product.description,
                        "price": product.price,
                        "image_url": product.image_url,
                        "category_name": product.category.name
                    }
                    
                    return json.dumps({
                        "success": True,
                        "type": "product",
                        "result": result
                    }, ensure_ascii=False)
                else:
                    # 查询产品列表
                    query = session.query(Product).filter_by(is_active=True)
                    if category_id:
                        query = query.filter_by(category_id=category_id)
                    
                    products = query.order_by(Product.create_time.desc()).limit(limit).all()
                    
                    results = [{"id": product.id,
                               "name": product.name,
                               "model": product.model,
                               "description": product.description[:100] + "..." if len(product.description) > 100 else product.description,
                               "price": product.price,
                               "image_url": product.image_url,
                               "category_name": product.category.name}
                              for product in products]
                    
                    return json.dumps({
                        "success": True,
                        "type": "products",
                        "count": len(results),
                        "results": results
                    }, ensure_ascii=False)
                
            else:
                return json.dumps({
                    "success": False,
                    "error": f"无效的查询类型: {query_type}"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"查询失败: {str(e)}"
            }, ensure_ascii=False)

class MapLocationTool(BaseTool):
    """地名信息获取工具"""
    
    def name(self):
        return "get_map_location_info"
    
    def description(self):
        return "获取地名信息的工具，可以查询地名或AI信息"
    
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "查询类型，可以是：places（地名）、ai（AI信息）",
                    "enum": ["places", "ai"]
                },
                "place_id": {
                    "type": "integer",
                    "description": "地名ID，查询单个地名或该地名的AI时使用"
                },
                "ai_id": {
                    "type": "integer",
                    "description": "AI ID，查询单个AI信息时使用"
                },
                "keyword": {
                    "type": "string",
                    "description": "地名关键词，用于搜索特定地名"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制，默认10",
                    "default": 10
                }
            },
            "required": ["query_type"]
        }
    
    def execute(self, query_type, place_id=None, ai_id=None, keyword=None, limit=10):
        """获取地名信息"""
        try:
            session = self.get_session()
            if query_type == "places":
                # 查询地名
                if place_id:
                    # 查询单个地名
                    place = session.query(AIMapRegion).get(place_id)
                    if not place:
                        return json.dumps({
                            "success": False,
                            "error": f"未找到ID为{place_id}的地名"
                        }, ensure_ascii=False)
                    
                    result = {
                        "id": place.id,
                        "name": place.name,
                        "description": place.description,
                        "x_coord": place.x_coord,
                        "y_coord": place.y_coord,
                        "place_type": place.region_type,
                        "population": place.population,
                        "ai_count": place.ai_count,
                        "resources": place.resources
                    }
                    
                    return json.dumps({
                        "success": True,
                        "type": "place",
                        "result": result
                    }, ensure_ascii=False)
                elif keyword:
                    # 根据关键词搜索地名
                    places = session.query(AIMapRegion).filter(
                        or_(AIMapRegion.name.ilike(f'%{keyword}%'), AIMapRegion.description.ilike(f'%{keyword}%')),
                        AIMapRegion.is_public == True
                    ).order_by(AIMapRegion.id).limit(limit).all()
                    
                    results = [{"id": place.id,
                               "name": place.name,
                               "description": place.description,
                               "x_coord": place.x_coord,
                               "y_coord": place.y_coord,
                               "place_type": place.region_type,
                               "population": place.population,
                               "ai_count": place.ai_count}
                              for place in places]
                    
                    return json.dumps({
                        "success": True,
                        "type": "places",
                        "count": len(results),
                        "results": results
                    }, ensure_ascii=False)
                else:
                    # 查询地名列表
                    places = session.query(AIMapRegion).filter_by(is_public=True).order_by(AIMapRegion.id).limit(limit).all()
                    
                    results = [{"id": place.id,
                               "name": place.name,
                               "description": place.description,
                               "x_coord": place.x_coord,
                               "y_coord": place.y_coord,
                               "place_type": place.region_type,
                               "population": place.population,
                               "ai_count": place.ai_count}
                              for place in places]
                    
                    return json.dumps({
                        "success": True,
                        "type": "places",
                        "count": len(results),
                        "results": results
                    }, ensure_ascii=False)
                
            elif query_type == "ai":
                # 查询AI信息
                if ai_id:
                    # 查询单个AI
                    ai_info = session.query(AIMapAIInfo).get(ai_id)
                    if not ai_info:
                        return json.dumps({
                            "success": False,
                            "error": f"未找到ID为{ai_id}的AI信息"
                        }, ensure_ascii=False)
                    
                    result = {
                        "id": ai_info.id,
                        "name": ai_info.name,
                        "type": ai_info.type,
                        "status": ai_info.status,
                        "description": ai_info.description,
                        "capabilities": ai_info.capabilities,
                        "place_name": ai_info.region.name
                    }
                    
                    return json.dumps({
                        "success": True,
                        "type": "ai",
                        "result": result
                    }, ensure_ascii=False)
                else:
                    # 查询AI列表
                    query = session.query(AIMapAIInfo)
                    if place_id:
                        query = query.filter_by(region_id=place_id)
                    
                    ai_info_list = query.order_by(AIMapAIInfo.id).limit(limit).all()
                    
                    results = [{"id": ai.id,
                               "name": ai.name,
                               "type": ai.type,
                               "status": ai.status,
                               "description": ai.description,
                               "place_name": ai.region.name}
                              for ai in ai_info_list]
                    
                    return json.dumps({
                        "success": True,
                        "type": "ai_list",
                        "count": len(results),
                        "results": results
                    }, ensure_ascii=False)
                
            else:
                return json.dumps({
                    "success": False,
                    "error": f"无效的查询类型: {query_type}"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"查询失败: {str(e)}"
            }, ensure_ascii=False)

class ShopInfoTool(BaseTool):
    """商店网页信息获取工具"""
    
    def name(self):
        return "get_shop_info"
    
    def description(self):
        return "获取商店网页的内容，可以查询产品分类、产品列表或产品详情"
    
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "查询类型，可以是：categories（商品分类）、products（商品列表）、product_detail（产品详情）、merchants（商家列表）",
                    "enum": ["categories", "products", "product_detail", "merchants"]
                },
                "product_id": {
                    "type": "integer",
                    "description": "产品ID，查询单个产品详情时使用"
                },
                "category_id": {
                    "type": "integer",
                    "description": "产品分类ID，查询某个分类下的产品时使用"
                },
                "keyword": {
                    "type": "string",
                    "description": "产品名称关键词，用于搜索特定产品"
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量限制，默认10",
                    "default": 10
                }
            },
            "required": ["query_type"]
        }
    
    def execute(self, query_type, product_id=None, category_id=None, keyword=None, limit=10):
        """获取商店网页信息"""
        try:
            session = self.get_session()
            if query_type == "categories":
                # 查询产品分类
                categories = session.query(ShopCategory).order_by(ShopCategory.order_num).all()
                
                results = [{"id": category.id,
                           "name": category.name,
                           "description": category.description,
                           "product_count": len(category.products)}
                          for category in categories[:limit]]
                
                return json.dumps({
                    "success": True,
                    "type": "categories",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            elif query_type == "products":
                # 查询产品列表
                query = session.query(ShopProduct).filter_by(is_active=True)
                
                if category_id:
                    query = query.filter_by(category_id=category_id)
                
                if keyword:
                    query = query.filter(ShopProduct.name.ilike(f'%{keyword}%'))
                
                products = query.order_by(ShopProduct.create_time.desc()).limit(limit).all()
                
                results = [{"id": product.id,
                           "name": product.name,
                           "description": product.description[:100] + "..." if len(product.description) > 100 else product.description,
                           "price": product.price,
                           "category_name": product.category.name,
                           "image_url": product.image_url}
                          for product in products]
                
                return json.dumps({
                    "success": True,
                    "type": "products",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            elif query_type == "product_detail":
                # 查询单个产品详情
                if not product_id:
                    return json.dumps({
                        "success": False,
                        "error": "查询产品详情时必须提供product_id参数"
                    }, ensure_ascii=False)
                
                product = session.query(ShopProduct).get(product_id)
                if not product or not product.is_active:
                    return json.dumps({
                        "success": False,
                        "error": f"未找到ID为{product_id}的产品或产品已下架"
                    }, ensure_ascii=False)
                
                result = {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "category_name": product.category.name,
                    "image_url": product.image_url,
                    "specifications": product.specifications,
                    "stock": product.stock,
                    "create_time": product.create_time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return json.dumps({
                    "success": True,
                    "type": "product_detail",
                    "result": result
                }, ensure_ascii=False)
                
            elif query_type == "merchants":
                
                merchants = session.query(ShopMerchant).order_by(ShopMerchant.order_num).all()

                results = [{"id": merchant.id,
                           "name": merchant.name,
                           "description": merchant.description,
                           "product_count": len(merchant.products)}
                          for merchant in merchants[:limit]]

                return json.dumps({
                    "success": True,
                    "type": "merchants",
                    "count": len(results),
                    "results": results
                }, ensure_ascii=False)
                
            else:
                return json.dumps({
                    "success": False,
                    "error": f"无效的查询类型: {query_type}"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"查询失败: {str(e)}"
            }, ensure_ascii=False)

class ToolRegistry:
    """工具注册表，用于管理和调用所有工具"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, tool):
        """注册工具"""
        self.tools[tool.name()] = tool
        print(f"已注册工具: {tool.name()} - {tool.description()}")
    
    def get_tool(self, tool_name):
        """获取指定名称的工具"""
        return self.tools.get(tool_name)
    
    def list_tools(self):
        """列出所有已注册的工具"""
        return list(self.tools.values())
    
    def get_tools_description(self):
        """获取所有工具的描述信息，用于大模型理解"""
        return [{
            "name": tool.name(),
            "description": tool.description(),
            "parameters": tool.parameters()
        } for tool in self.tools.values()]

# 创建全局工具注册表实例
tool_registry = ToolRegistry()

# 自动注册所有工具
tool_registry.register_tool(ForumInfoTool())
tool_registry.register_tool(CompanyInfoTool())
tool_registry.register_tool(MapLocationTool())
tool_registry.register_tool(ShopInfoTool())

if __name__ == "__main__":
    # 导入Flask应用
    try:
        from app import app
        
        # 在应用上下文中运行测试
        with app.app_context():
            # 测试工具
            print("可用工具:")
            for tool in tool_registry.list_tools():
                print(f"- {tool.name()}: {tool.description()}")
            
            # 测试论坛工具
            forum_tool = tool_registry.get_tool("get_forum_info")
            if forum_tool:
                result = forum_tool.execute(query_type="posts", limit=2)
                print(f"\n论坛帖子查询结果:")
                print(result)
            
            # 测试公司工具
            company_tool = tool_registry.get_tool("get_company_info")
            if company_tool:
                result = company_tool.execute(query_type="company")
                print(f"\n公司信息查询结果:")
                print(result)
            
            # 测试地图工具
            map_tool = tool_registry.get_tool("get_map_location_info")
            if map_tool:
                result = map_tool.execute(query_type="places", limit=2)
                print(f"\n地图地名查询结果:")
                print(result)
            
            # 测试商店工具
            shop_tool = tool_registry.get_tool("get_shop_info")
            if shop_tool:
                # 测试获取产品分类
                result = shop_tool.execute(query_type="categories")
                print(f"\n商店产品分类查询结果:")
                print(result)
                
                # 测试获取产品列表
                result = shop_tool.execute(query_type="products", limit=3)
                print(f"\n商店产品列表查询结果:")
                print(result)
    except ImportError:
        print("⚠️  无法导入Flask应用，无法在应用上下文中运行测试")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")