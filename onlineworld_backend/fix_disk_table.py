# 修复online_disk_share表结构的脚本
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app
from forum.models import OnlineDiskShare, db
from sqlalchemy import text
from sqlalchemy import inspect

with app.app_context():
    try:
        # 获取inspector对象
        inspector = inspect(db.engine)
        
        # 检查表是否存在
        table_exists = inspector.has_table('online_disk_share')
        
        if table_exists:
            # 删除旧表
            db.session.execute(text('DROP TABLE online_disk_share;'))
            db.session.commit()
            print("已删除旧的online_disk_share表")
        
        # 重新创建表
        OnlineDiskShare.__table__.create(db.engine)
        db.session.commit()
        print("已创建新的online_disk_share表")
        
    except Exception as e:
        print(f"修复表结构失败: {str(e)}")
        db.session.rollback()