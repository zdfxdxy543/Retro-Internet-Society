import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 从app.py导入Flask应用实例
from app import app, db
from forum.models import AIMapRegion

def check_places():
    with app.app_context():
        # 查询所有地图区域
        regions = AIMapRegion.query.all()
        print(f"数据库中共有 {len(regions)} 个地图区域：")
        for i, region in enumerate(regions, 1):
            print(f"\n{i}. 地名：{region.name}")
            print(f"   ID：{region.id}")
            print(f"   类型：{region.region_type}")
            print(f"   描述：{region.description}")
            print(f"   坐标：({region.x_coord}, {region.y_coord})")

if __name__ == '__main__':
    check_places()