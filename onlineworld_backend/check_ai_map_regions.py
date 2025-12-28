from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from forum.models import AIMapRegion

# 创建数据库引擎和会话，使用instance目录下的forum.db
engine = create_engine('sqlite:///instance/forum.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    # 查询所有地名
    regions = session.query(AIMapRegion).all()
    
    print('数据库中的地名列表：')
    for region in regions:
        print(f'- {region.name}')
        print(f'  描述：{region.description}')
        print(f'  类型：{region.region_type}')
        print()
        
    print(f'总共找到 {len(regions)} 个地名')
    
finally:
    # 关闭会话
    session.close()