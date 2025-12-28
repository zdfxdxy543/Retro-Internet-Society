import os
import sys
from app import app, db
from forum.models import Product, ProductCategory

with app.app_context():
    # 获取所有产品
    products = Product.query.all()
    categories = ProductCategory.query.all()
    
    print(f"当前数据库中有 {len(categories)} 个产品分类：")
    for category in categories:
        print(f"  - {category.name} ({category.description})")
    
    print(f"\n当前数据库中有 {len(products)} 个产品：")
    
    # 检查每个产品的DataSheet状态
    for product in products:
        has_datasheet = "是" if product.datasheet_url else "否"
        print(f"  - {product.name} ({product.model}) - DataSheet: {has_datasheet}")
        if product.datasheet_url:
            # 检查文件是否实际存在
            file_path = os.path.join(app.root_path, "static", "files", "datasheets", f"{product.model}_datasheet.pdf")
            if os.path.exists(file_path):
                print(f"    文件路径: {file_path}")
                print(f"    文件大小: {os.path.getsize(file_path)/1024:.2f} KB")
            else:
                print(f"    警告: 文件不存在: {file_path}")
