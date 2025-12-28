import os
import sys
from app import app, db
from forum.datasheet_generator import DataSheetGenerator

with app.app_context():
    # 创建DataSheetGenerator实例
    generator = DataSheetGenerator()
    
    # 批量生成所有产品的DataSheet
    result = generator.generate_all_datasheets()
    
    # 打印生成结果
    print(f"批量生成DataSheet结果：")
    print(f"总产品数：{result['total']}")
    print(f"成功生成：{result['generated']}")
    print(f"已存在跳过：{result['skipped']}")
    print(f"生成失败：{result['failed']}")
    print(f"状态：{'成功' if result['success'] else '失败'}")
    print(f"消息：{result['message']}")
