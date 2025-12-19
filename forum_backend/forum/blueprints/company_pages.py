from flask import Blueprint
from .base import BasePageView, register_page_route
from ..models import CompanyInfo, ProductCategory, Product, db
from flask import session
from datetime import datetime

# 导入API蓝图而不是创建新蓝图
from .api import api_bp

# 首页视图类
class CompanyIndexView(BasePageView):
    def get_data(self):
        # 获取公司基本信息
        company_info = CompanyInfo.query.first()
        if not company_info:
            # 如果没有公司信息，创建默认信息
            company_info = CompanyInfo(
                name="未来科技有限公司",
                description="未来科技有限公司成立于2005年，是一家专注于软件开发、硬件设计和人工智能技术的高科技企业。我们致力于为客户提供最先进的技术解决方案，帮助客户在数字化时代取得成功。",
                founded_year=2005,
                address="北京市海淀区中关村科技园区",
                phone="010-12345678",
                email="contact@futuretech.com",
                website="www.futuretech.com",
                slogan="科技创造未来，创新引领时代",
                logo_url="/static/images/logo.png"
            )
            db.session.add(company_info)
            db.session.commit()
        
        # 获取产品分类
        categories = ProductCategory.query.order_by(ProductCategory.order_num).all()
        category_list = [{
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "product_count": len(category.products)
        } for category in categories]
        
        # 获取最新产品
        latest_products = Product.query.filter_by(is_active=True).order_by(Product.create_time.desc()).limit(3).all()
        product_list = [{
            "id": product.id,
            "name": product.name,
            "model": product.model,
            "description": product.description[:100] + "..." if len(product.description) > 100 else product.description,
            "image_url": product.image_url,
            "category_name": product.category.name
        } for product in latest_products]
        
        return {
            "title": f"{company_info.name} - 首页",
            "company": {
                "name": company_info.name,
                "description": company_info.description,
                "founded_year": company_info.founded_year,
                "address": company_info.address,
                "phone": company_info.phone,
                "email": company_info.email,
                "website": company_info.website,
                "slogan": company_info.slogan,
                "logo_url": company_info.logo_url
            },
            "categories": category_list,
            "latest_products": product_list
        }

# 产品列表页视图类
class ProductListView(BasePageView):
    def get_data(self, category_id=None):
        # 获取产品分类
        categories = ProductCategory.query.order_by(ProductCategory.order_num).all()
        category_list = [{
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "product_count": len(category.products)
        } for category in categories]
        
        # 查询产品
        query = Product.query.filter_by(is_active=True)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.order_by(Product.create_time.desc()).all()
        product_list = [{
            "id": product.id,
            "name": product.name,
            "model": product.model,
            "description": product.description[:150] + "..." if len(product.description) > 150 else product.description,
            "price": product.price,
            "image_url": product.image_url,
            "category_name": product.category.name
        } for product in products]
        
        # 获取当前分类名称
        current_category = None
        if category_id:
            current_category_obj = ProductCategory.query.get(category_id)
            if current_category_obj:
                current_category = current_category_obj.name
        
        return {
            "title": f"产品中心{' - ' + current_category if current_category else ''}",
            "categories": category_list,
            "current_category_id": category_id,
            "products": product_list
        }

# 产品详情页视图类
class ProductDetailView(BasePageView):
    def get_data(self, product_id):
        # 查询产品详情
        product = Product.query.get_or_404(product_id)
        
        # 获取产品分类
        categories = ProductCategory.query.order_by(ProductCategory.order_num).all()
        category_list = [{
            "id": category.id,
            "name": category.name
        } for category in categories]
        
        # 获取相关产品
        related_products = Product.query.filter_by(
            category_id=product.category_id, 
            is_active=True
        ).filter(Product.id != product_id).order_by(Product.create_time.desc()).limit(3).all()
        
        related_product_list = [{
            "id": related.id,
            "name": related.name,
            "model": related.model,
            "description": related.description[:100] + "..." if len(related.description) > 100 else related.description,
            "image_url": related.image_url
        } for related in related_products]
        
        return {
            "title": f"产品详情 - {product.name}",
            "product": product.to_dict(),
            "categories": category_list,
            "related_products": related_product_list
        }

# 关于我们视图类
class AboutView(BasePageView):
    def get_data(self):
        # 获取公司基本信息
        company_info = CompanyInfo.query.first()
        if not company_info:
            # 如果没有公司信息，创建默认信息
            company_info = CompanyInfo(
                name="未来科技有限公司",
                description="未来科技有限公司成立于2005年，是一家专注于软件开发、硬件设计和人工智能技术的高科技企业。我们致力于为客户提供最先进的技术解决方案，帮助客户在数字化时代取得成功。",
                founded_year=2005,
                address="北京市海淀区中关村科技园区",
                phone="010-12345678",
                email="contact@futuretech.com",
                website="www.futuretech.com",
                slogan="科技创造未来，创新引领时代",
                logo_url="/static/images/logo.png"
            )
            db.session.add(company_info)
            db.session.commit()
        
        return {
            "title": f"{company_info.name} - 关于我们",
            "company": {
                "name": company_info.name,
                "description": company_info.description,
                "founded_year": company_info.founded_year,
                "address": company_info.address,
                "phone": company_info.phone,
                "email": company_info.email,
                "website": company_info.website,
                "slogan": company_info.slogan,
                "logo_url": company_info.logo_url
            }
        }

# 联系我们视图类
class ContactView(BasePageView):
    def get_data(self):
        # 获取公司基本信息
        company_info = CompanyInfo.query.first()
        if not company_info:
            # 如果没有公司信息，创建默认信息
            company_info = CompanyInfo(
                name="未来科技有限公司",
                description="未来科技有限公司成立于2005年，是一家专注于软件开发、硬件设计和人工智能技术的高科技企业。我们致力于为客户提供最先进的技术解决方案，帮助客户在数字化时代取得成功。",
                founded_year=2005,
                address="北京市海淀区中关村科技园区",
                phone="010-12345678",
                email="contact@futuretech.com",
                website="www.futuretech.com",
                slogan="科技创造未来，创新引领时代",
                logo_url="/static/images/logo.png"
            )
            db.session.add(company_info)
            db.session.commit()
        
        return {
            "title": f"{company_info.name} - 联系我们",
            "company": {
                "name": company_info.name,
                "address": company_info.address,
                "phone": company_info.phone,
                "email": company_info.email,
                "website": company_info.website
            }
        }

# 注册所有公司网站路由到API蓝图
register_page_route(api_bp, "/company/", CompanyIndexView)  # 公司首页，注意添加末尾的斜杠以匹配前端请求
register_page_route(api_bp, "/company/products", ProductListView, endpoint="product_list_all")  # 产品列表页
register_page_route(api_bp, "/company/products/category/<int:category_id>", ProductListView, endpoint="product_list_by_category")  # 分类产品列表页
register_page_route(api_bp, "/company/product/<int:product_id>", ProductDetailView)  # 产品详情页
register_page_route(api_bp, "/company/about", AboutView)  # 关于我们
register_page_route(api_bp, "/company/contact", ContactView)  # 联系我们