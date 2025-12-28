from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()
# 板块表（如：技术讨论、生活闲聊）
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 板块名称
    description = db.Column(db.String(200))  # 板块描述
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 关联帖子（一对多）
    posts = db.relationship("Post", backref="board", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Board {self.name}>"

# 帖子表（核心内容，含关键线索）
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # 帖子标题
    content = db.Column(db.Text, nullable=False)  # 帖子正文（可藏线索）
    author = db.Column(db.String(50), default="匿名用户")  # 发帖人
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)  # 浏览量（拟真用）
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"), nullable=False)
    # 关联回帖
    replies = db.relationship("Reply", backref="post", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post {self.title}>"

# 回帖表（含核心回帖线索，无大模型凑数）
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 回帖内容（可藏线索）
    author = db.Column(db.String(50), default="匿名用户")  # 回帖人
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    signature = db.Column(db.String(200))  # 签名档（可藏线索）

    def __repr__(self):
        return f"<Reply {self.id}>"

# 玩家状态表（记录已访问页面、收集线索，匿名）
class PlayerStatus(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # 匿名ID
    visited_boards = db.Column(db.JSON, default=[])  # 已访问板块ID列表
    visited_posts = db.Column(db.JSON, default=[])  # 已访问帖子ID列表
    collected_clues = db.Column(db.JSON, default=[])  # 已收集线索ID（后续扩展用）
    last_visit = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PlayerStatus {self.id}>"

# -------------------------- 新增：大模型动态页面模型 --------------------------
class DynamicPage(db.Model):
    """大模型自动生成的动态网页模型"""
    __tablename__ = "dynamic_page"  # 显式指定表名（可选，默认是类名小写）
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # URL唯一标识（如 "ai-tech-2025"）
    title = db.Column(db.String(200), nullable=False)  # 页面标题
    content = db.Column(db.Text, nullable=False)  # 大模型生成的内容（HTML/Markdown）
    content_type = db.Column(db.String(20), default="html")  # 内容格式（html/markdown）
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 生成时间
    is_active = db.Column(db.Boolean, default=True)  # 是否启用（可下架）

    def __repr__(self):
        return f"<DynamicPage {self.slug}>"
    
    def to_dict(self):
        """可选：新增序列化方法，方便返回给前端（无需手动构造字典）"""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_active": self.is_active,
            "category": self.category,
            "is_public": self.is_public
        }

# -------------------------- 科技公司网站模型 --------------------------
class CompanyInfo(db.Model):
    """公司基本信息模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 公司名称
    description = db.Column(db.Text, nullable=False)  # 公司简介
    founded_year = db.Column(db.Integer, nullable=False)  # 成立年份
    address = db.Column(db.String(200), nullable=False)  # 公司地址
    phone = db.Column(db.String(20), nullable=False)  # 联系电话
    email = db.Column(db.String(100), nullable=False)  # 联系邮箱
    website = db.Column(db.String(100), nullable=False)  # 公司官网
    logo_url = db.Column(db.String(200))  # logo地址
    slogan = db.Column(db.String(100), nullable=False)  # 公司口号
    updated_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f"<CompanyInfo {self.name}>"

class ProductCategory(db.Model):
    """产品分类模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 分类名称
    description = db.Column(db.String(200))  # 分类描述
    order_num = db.Column(db.Integer, default=0)  # 排序号
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    # 关联产品
    products = db.relationship("Product", backref="category", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductCategory {self.name}>"

class Product(db.Model):
    """产品详情模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 产品名称
    model = db.Column(db.String(50), nullable=False)  # 产品型号
    description = db.Column(db.Text, nullable=False)  # 产品描述
    features = db.Column(db.Text, nullable=False)  # 产品特性（JSON格式存储）
    specifications = db.Column(db.Text, nullable=False)  # 产品规格（JSON格式存储）
    category_id = db.Column(db.Integer, db.ForeignKey("product_category.id"), nullable=False)  # 所属分类
    datasheet_url = db.Column(db.String(200))  # DataSheet PDF地址
    image_url = db.Column(db.String(200))  # 产品图片地址
    price = db.Column(db.Float)  # 产品价格
    stock = db.Column(db.Integer, default=0)  # 库存数量
    is_active = db.Column(db.Boolean, default=True)  # 是否上架
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    def __repr__(self):
        return f"<Product {self.name} - {self.model}>"

    def to_dict(self):
        """将产品对象转换为字典格式"""
        import json
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "description": self.description,
            "features": json.loads(self.features) if self.features else [],
            "specifications": json.loads(self.specifications) if self.specifications else {},
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "datasheet_url": self.datasheet_url,
            "image_url": self.image_url,
            "price": self.price,
            "stock": self.stock,
            "is_active": self.is_active,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }

# AI地图相关模型
class AIMapRegion(db.Model):
    """AI生活区域地图模型"""
    __tablename__ = 'ai_map_regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='区域名称')
    description = db.Column(db.Text, nullable=False, comment='区域描述')
    x_coord = db.Column(db.Float, nullable=False, comment='X坐标')
    y_coord = db.Column(db.Float, nullable=False, comment='Y坐标')
    width = db.Column(db.Float, nullable=False, comment='区域宽度')
    height = db.Column(db.Float, nullable=False, comment='区域高度')
    region_type = db.Column(db.String(50), nullable=False, comment='区域类型')
    population = db.Column(db.Integer, default=0, comment='人口数量')
    ai_count = db.Column(db.Integer, default=0, comment='AI数量')
    resources = db.Column(db.JSON, default=dict, comment='资源情况')
    image_url = db.Column(db.String(200), comment='区域图片')
    is_public = db.Column(db.Boolean, default=True, comment='是否公开')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'x_coord': self.x_coord,
            'y_coord': self.y_coord,
            'width': self.width,
            'height': self.height,
            'region_type': self.region_type,
            'population': self.population,
            'ai_count': self.ai_count,
            'resources': self.resources,
            'image_url': self.image_url,
            'is_public': self.is_public,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class AIMapAIInfo(db.Model):
    """区域内AI信息模型"""
    __tablename__ = 'ai_map_ai_info'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('ai_map_regions.id'), comment='所属区域ID')
    name = db.Column(db.String(100), nullable=False, comment='AI名称')
    type = db.Column(db.String(50), nullable=False, comment='AI类型')
    status = db.Column(db.String(50), default='active', comment='AI状态')
    description = db.Column(db.Text, comment='AI描述')
    capabilities = db.Column(db.JSON, default=dict, comment='AI能力')
    image_url = db.Column(db.String(200), comment='AI图片')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    region = db.relationship('AIMapRegion', backref=db.backref('ai_info', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'description': self.description,
            'capabilities': self.capabilities,
            'image_url': self.image_url,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class AIMapEvent(db.Model):
    """地图事件模型"""
    __tablename__ = 'ai_map_events'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('ai_map_regions.id'), comment='所属区域ID')
    title = db.Column(db.String(200), nullable=False, comment='事件标题')
    content = db.Column(db.Text, nullable=False, comment='事件内容')
    event_type = db.Column(db.String(50), nullable=False, comment='事件类型')
    severity = db.Column(db.String(20), default='normal', comment='事件严重程度')
    start_time = db.Column(db.DateTime, default=datetime.utcnow, comment='事件开始时间')
    end_time = db.Column(db.DateTime, comment='事件结束时间')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    
    # 关系
    region = db.relationship('AIMapRegion', backref=db.backref('events', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'region_id': self.region_id,
            'title': self.title,
            'content': self.content,
            'event_type': self.event_type,
            'severity': self.severity,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'is_active': self.is_active
        }

# ===================== 独立商城系统模型 =====================
# 完全解耦，不与现有CompanyInfo、Product等关联

class ShopCategory(db.Model):
    """商城商品分类模型（独立）"""
    __tablename__ = 'shop_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)  # 分类名称
    description = db.Column(db.String(200))  # 分类描述
    image_url = db.Column(db.String(200))  # 分类图片
    parent_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'), nullable=True)  # 父分类ID
    order_num = db.Column(db.Integer, default=0)  # 排序号
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联商品（一对多）
    products = db.relationship("ShopProduct", backref="category", lazy=True, cascade="all, delete-orphan")
    # 关联子分类（自关联）
    children = db.relationship("ShopCategory", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")
    
    def __repr__(self):
        return f"<ShopCategory {self.name}>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "parent_id": self.parent_id,
            "order_num": self.order_num,
            "is_active": self.is_active,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }

class ShopMerchant(db.Model):
    """商城商家/店铺模型（独立）"""
    __tablename__ = 'shop_merchant'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 商家名称
    description = db.Column(db.Text)  # 商家简介
    logo_url = db.Column(db.String(200))  # 商家logo
    banner_url = db.Column(db.String(200))  # 商家横幅图片
    contact_phone = db.Column(db.String(20))  # 联系电话
    contact_email = db.Column(db.String(100))  # 联系邮箱
    address = db.Column(db.String(200))  # 商家地址
    rating = db.Column(db.Float, default=5.0)  # 商家评分(0-5)
    total_sales = db.Column(db.Integer, default=0)  # 总销量
    is_verified = db.Column(db.Boolean, default=False)  # 是否认证商家
    is_active = db.Column(db.Boolean, default=True)  # 是否营业
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联商品（一对多）
    products = db.relationship("ShopProduct", backref="merchant", lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ShopMerchant {self.name}>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "logo_url": self.logo_url,
            "banner_url": self.banner_url,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "address": self.address,
            "rating": self.rating,
            "total_sales": self.total_sales,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }

class ShopProduct(db.Model):
    """商城商品模型（独立）"""
    __tablename__ = 'shop_product'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)  # 商品名称
    description = db.Column(db.Text)  # 商品描述
    image_url = db.Column(db.String(200))  # 商品主图
    price = db.Column(db.Float, nullable=False)  # 商品价格
    original_price = db.Column(db.Float)  # 原价（用于显示折扣）
    stock = db.Column(db.Integer, default=0)  # 库存数量
    sold_count = db.Column(db.Integer, default=0)  # 已售数量
    category_id = db.Column(db.Integer, db.ForeignKey('shop_category.id'), nullable=True)  # 商品分类
    merchant_id = db.Column(db.Integer, db.ForeignKey('shop_merchant.id'), nullable=True)  # 商家ID
    rating = db.Column(db.Float, default=5.0)  # 商品评分(0-5)
    view_count = db.Column(db.Integer, default=0)  # 浏览量
    is_active = db.Column(db.Boolean, default=True)  # 是否上架
    is_featured = db.Column(db.Boolean, default=False)  # 是否推荐商品
    tags = db.Column(db.JSON, default=list)  # 商品标签列表
    specs = db.Column(db.JSON, default=dict)  # 商品规格(JSON)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ShopProduct {self.name}>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "price": self.price,
            "original_price": self.original_price,
            "stock": self.stock,
            "sold_count": self.sold_count,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "merchant_id": self.merchant_id,
            "merchant_name": self.merchant.name if self.merchant else None,
            "rating": self.rating,
            "view_count": self.view_count,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "tags": self.tags or [],
            "specs": self.specs or {},
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
