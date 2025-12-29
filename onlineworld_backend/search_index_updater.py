import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.blocking import BlockingScheduler

# 导入配置
from config import Config

# 导入模型（直接导入，无Flask依赖）
from forum.models import db, SearchIndex, Board, Post, ShopProduct, DynamicPage, ShopCategory, ShopMerchant, Product, ProductCategory

# -------------------------- 配置 --------------------------
# 数据库配置
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# 更新频率配置
UPDATE_INTERVAL_HOURS = 1  # 每小时更新一次

# -------------------------- 数据库初始化（无Flask依赖！）--------------------------
# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite需加此参数
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------- 工具函数 --------------------------
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def build_search_index():
    """
    构建搜索索引，从所有可搜索的模型中提取标题并存储到SearchIndex表
    """
    print(f"\n{'='*60}")
    print(f"🔄 开始构建搜索索引 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        db = next(get_db())
        
        # 首先清空现有的索引
        db.query(SearchIndex).delete()
        db.commit()
        
        # 从各个模型中提取标题并创建索引
        search_indexes = []
        
        # 0. 各个模块的首页
        # 论坛首页
        search_indexes.append(SearchIndex(
            title="论坛首页", entity_type="forum_home", 
            entity_id=0, url="/forum"
        ))
        
        # 商城首页
        search_indexes.append(SearchIndex(
            title="商城首页", entity_type="shop_home", 
            entity_id=0, url="/shop"
        ))
        
        # 产品首页
        search_indexes.append(SearchIndex(
            title="产品首页", entity_type="product_home", 
            entity_id=0, url="/products"
        ))
        
        # 动态页面首页
        search_indexes.append(SearchIndex(
            title="动态页面首页", entity_type="dynamic_home", 
            entity_id=0, url="/dynamic"
        ))
        
        print(f"📋 已处理模块首页: {len([i for i in search_indexes if i.entity_type.endswith('_home')])}条")
        
        # 1. 论坛板块 (Board)
        boards = db.query(Board).all()
        for board in boards:
            index = SearchIndex(
                title=board.name,
                entity_type="forum_board",
                entity_id=board.id,
                url=f"/forum/board/{board.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理论坛板块: {len(boards)}条")
        
        # 2. 论坛帖子 (Post)
        posts = db.query(Post).all()
        for post in posts:
            index = SearchIndex(
                title=post.title,
                entity_type="forum_post",
                entity_id=post.id,
                url=f"/forum/post/{post.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理论坛帖子: {len(posts)}条")
        
        # 3. 商城商品 (ShopProduct)
        products = db.query(ShopProduct).filter_by(is_active=True).all()
        for product in products:
            index = SearchIndex(
                title=product.name,
                entity_type="shop_product",
                entity_id=product.id,
                url=f"/shop/product/{product.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理商城商品: {len(products)}条")
        
        # 4. 动态页面 (DynamicPage)
        pages = db.query(DynamicPage).filter_by(is_active=True, is_public=True).all()
        for page in pages:
            index = SearchIndex(
                title=page.title,
                entity_type="dynamic_page",
                entity_id=page.id,
                url=f"/dynamic/{page.slug}"
            )
            search_indexes.append(index)
        print(f"📋 已处理动态页面: {len(pages)}条")
        
        # 5. 商城分类 (ShopCategory)
        shop_categories = db.query(ShopCategory).filter_by(is_active=True).all()
        for category in shop_categories:
            index = SearchIndex(
                title=category.name,
                entity_type="shop_category",
                entity_id=category.id,
                url=f"/shop/category/{category.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理商城分类: {len(shop_categories)}条")
        
        # 6. 商城商家 (ShopMerchant)
        shop_merchants = db.query(ShopMerchant).filter_by(is_active=True).all()
        for merchant in shop_merchants:
            index = SearchIndex(
                title=merchant.name,
                entity_type="shop_merchant",
                entity_id=merchant.id,
                url=f"/shop/merchant/{merchant.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理商城商家: {len(shop_merchants)}条")
        
        # 7. 产品 (Product)
        products = db.query(Product).filter_by(is_active=True).all()
        for product in products:
            index = SearchIndex(
                title=product.name,
                entity_type="product",
                entity_id=product.id,
                url=f"/products/{product.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理产品: {len(products)}条")
        
        # 8. 产品分类 (ProductCategory)
        product_categories = db.query(ProductCategory).all()
        for category in product_categories:
            index = SearchIndex(
                title=category.name,
                entity_type="product_category",
                entity_id=category.id,
                url=f"/products/category/{category.id}"
            )
            search_indexes.append(index)
        print(f"📋 已处理产品分类: {len(product_categories)}条")
        
        # 批量添加索引
        db.add_all(search_indexes)
        db.commit()
        
        total_records = len(search_indexes)
        print(f"✅ 搜索索引构建完成！共添加 {total_records} 条记录")
        print(f"{'='*60}\n")
        
        return {
            "status": "success",
            "message": f"共添加 {total_records} 条记录",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"❌ 构建索引失败: {str(e)}")
        print(f"{'='*60}\n")
        return {
            "status": "error",
            "message": f"构建索引失败：{str(e)}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """主程序入口"""
    print("=" * 60)
    print("🚀 搜索索引自动更新服务启动成功")
    print(f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库：{DATABASE_URL}")
    print(f"更新频率：每{UPDATE_INTERVAL_HOURS}小时")
    print("=" * 60)
    
    # 初始化定时任务
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    
    # 添加索引更新任务
    scheduler.add_job(
        func=build_search_index,
        trigger="interval",
        hours=UPDATE_INTERVAL_HOURS,
        id="auto_update_search_index",
        name="自动更新搜索索引"
    )
    
    # 立即执行一次索引构建
    build_search_index()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("⚠️  服务已停止")

if __name__ == "__main__":
    main()
