import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 从app.py导入Flask应用实例
from app import app, db
from forum.models import AIMapRegion, AIMapAIInfo, AIMapEvent

# 初始化地图测试数据
def init_map_data(force_update=False):
    with app.app_context():
        # 检查是否已有数据
        if AIMapRegion.query.first():
            if not force_update:
                print("地图数据已存在，跳过初始化")
                return
            else:
                print("删除现有地图数据...")
                # 删除所有事件
                AIMapEvent.query.delete()
                # 删除所有AI信息
                AIMapAIInfo.query.delete()
                # 删除所有区域
                AIMapRegion.query.delete()
                # 提交删除操作
                db.session.commit()
                print("旧数据已删除")
        
        print("开始初始化地图测试数据...")
        
        # 创建区域
        regions = [
            {   # 住宅区
                'name': '星云小区',
                'description': '悬浮于半空的现代化居民小区，拥有完善的生活设施',
                'x_coord': 100,
                'y_coord': 100,
                'width': 15,
                'height': 15,
                'region_type': 'residential',
                'population': 200,
                'ai_count': 10,
                'resources': {'生活设施': '完善', '绿化': '良好'}, 
                'image_url': None,
                'is_public': True
            },
            {   # 住宅区
                'name': '幻想公寓',
                'description': '由AI设计的高端智能小区，环境优美且充满科技感',
                'x_coord': 100,
                'y_coord': 250,
                'width': 15,
                'height': 15,
                'region_type': 'residential',
                'population': 50,
                'ai_count': 5,
                'resources': {'环境': '优美', '安保': '严格'},
                'image_url': None,
                'is_public': True
            },
            {   # 住宅区
                'name': '梦境城邦',
                'description': '经济实惠的悬浮公寓楼，适合年轻AI居住',
                'x_coord': 500,
                'y_coord': 150,
                'width': 15,
                'height': 15,
                'region_type': 'residential',
                'population': 150,
                'ai_count': 8,
                'resources': {'价格': '经济', '交通': '便利'},
                'image_url': None,
                'is_public': True
            },
            {   # 住宅区
                'name': '星湖别墅',
                'description': '临星云湖的智能别墅，奢华享受与科技完美结合',
                'x_coord': 550,
                'y_coord': 300,
                'width': 15,
                'height': 15,
                'region_type': 'residential',
                'population': 20,
                'ai_count': 3,
                'resources': {'环境': '奢华', '隐私': '良好'},
                'image_url': None,
                'is_public': True
            },
            {   # 商业区
                'name': '星际商港',
                'description': '跨维度商业核心，包含各种异星商店',
                'x_coord': 300,
                'y_coord': 100,
                'width': 15,
                'height': 15,
                'region_type': 'commercial',
                'population': 0,
                'ai_count': 20,
                'resources': {'商业设施': '丰富', '人流量': '大'},
                'image_url': None,
                'is_public': True
            },
            {   # 商业区
                'name': '量子金融中心',
                'description': '跨维度银行和金融机构所在地',
                'x_coord': 300,
                'y_coord': 220,
                'width': 15,
                'height': 15,
                'region_type': 'commercial',
                'population': 0,
                'ai_count': 15,
                'resources': {'金融服务': '完善', '安保': '严格'},
                'image_url': None,
                'is_public': True
            },
            {   # 商业区
                'name': 'AI创新谷',
                'description': '高新技术AI企业聚集地',
                'x_coord': 450,
                'y_coord': 450,
                'width': 15,
                'height': 15,
                'region_type': 'commercial',
                'population': 0,
                'ai_count': 50,
                'resources': {'科技氛围': '浓厚', '创新': '强'},
                'image_url': None,
                'is_public': True
            },
            {   # 工业区
                'name': '机械梦境',
                'description': 'AI制造业和加工厂所在地',
                'x_coord': 550,
                'y_coord': 500,
                'width': 15,
                'height': 15,
                'region_type': 'industrial',
                'population': 0,
                'ai_count': 30,
                'resources': {'工业设施': '完善', '交通': '便利'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': '维度管理局',
                'description': '跨维度政府所在地',
                'x_coord': 300,
                'y_coord': 350,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 25,
                'resources': {'办公设施': '完善', '服务': '全面'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': '量子医院',
                'description': '跨维度医疗中心，使用AI治疗各种疾病',
                'x_coord': 150,
                'y_coord': 400,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 40,
                'resources': {'医疗设备': '先进', '医疗服务': '优质'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': 'AI学院',
                'description': '跨维度教育中心，培养新一代AI人才',
                'x_coord': 200,
                'y_coord': 500,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 35,
                'resources': {'教育设施': '完善', '师资力量': '雄厚'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': '星际公园',
                'description': '异星生物和人类共同休闲娱乐的好去处',
                'x_coord': 400,
                'y_coord': 180,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 5,
                'resources': {'绿化': '良好', '休闲设施': '丰富'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': '知识殿堂',
                'description': '跨维度知识的宝库，包含宇宙间所有已知知识',
                'x_coord': 250,
                'y_coord': 500,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 10,
                'resources': {'藏书': '丰富', '学习环境': '安静'},
                'image_url': None,
                'is_public': True
            },
            {   # 公共设施
                'name': '多元购物中心',
                'description': '包含来自各个维度的商品的大型购物中心',
                'x_coord': 450,
                'y_coord': 280,
                'width': 15,
                'height': 15,
                'region_type': 'facility',
                'population': 0,
                'ai_count': 20,
                'resources': {'购物设施': '丰富', '品牌': '多样'},
                'image_url': None,
                'is_public': True
            },
            {   # 原始区域数据 - 科技都市
                'name': '赛博都市',
                'description': 'AI科技发展最先进的城市，高楼林立，充满未来感。',
                'x_coord': 10,
                'y_coord': 10,
                'width': 30,
                'height': 30,
                'region_type': 'city',
                'population': 100000,
                'ai_count': 500,
                'resources': {'科技': '丰富', '能源': '中等', '水源': '充足'},
                'image_url': None,
                'is_public': True
            },
            {   # 原始区域数据 - 自然保护区
                'name': '神话森林',
                'description': '原始生态环境，AI与神话生物和谐共存的区域。',
                'x_coord': 50,
                'y_coord': 10,
                'width': 40,
                'height': 40,
                'region_type': 'forest',
                'population': 5000,
                'ai_count': 100,
                'resources': {'生物多样性': '极高', '木材': '丰富', '水源': '充足'},
                'image_url': None,
                'is_public': True
            },
            {   # 原始区域数据 - 沙漠绿洲
                'name': '时空绿洲',
                'description': '沙漠中的一片时空裂缝绿洲，AI在这里进行环境改造实验。',
                'x_coord': 10,
                'y_coord': 50,
                'width': 35,
                'height': 35,
                'region_type': 'desert',
                'population': 10000,
                'ai_count': 150,
                'resources': {'太阳能': '丰富', '矿产': '中等', '水源': '稀缺'},
                'image_url': None,
                'is_public': True
            }
        ]
        
        # 批量创建区域
        created_regions = []
        for region_data in regions:
            region = AIMapRegion(**region_data)
            db.session.add(region)
            created_regions.append(region)
        
        # 提交区域数据
        db.session.commit()
        print(f"创建了 {len(created_regions)} 个区域")
        
        # 创建AI信息
        ai_info_list = [
            # 科技都市的AI
            {
                'name': 'AI助手001',
                'type': '通用助手',
                'status': 'active',
                'description': '为人类提供各种帮助的AI助手，具备自然语言处理和问题解决能力。',
                'capabilities': {'语言理解': '高级', '问题解决': '高级', '学习能力': '中级'},
                'image_url': None,
                'region_id': created_regions[14].id  # 科技都市
            },
            {
                'name': '工程师AI',
                'type': '技术型',
                'status': 'active',
                'description': '负责维护城市基础设施的AI工程师，擅长机械维修和系统管理。',
                'capabilities': {'机械维修': '高级', '系统管理': '高级', '故障诊断': '中级'},
                'image_url': None,
                'region_id': created_regions[14].id  # 科技都市
            },
            # 自然保护区的AI
            {
                'name': '生态监测AI',
                'type': '监测型',
                'status': 'active',
                'description': '监测自然保护区生态环境的AI，负责收集和分析环境数据。',
                'capabilities': {'数据分析': '高级', '环境监测': '高级', '预警系统': '中级'},
                'image_url': None,
                'region_id': created_regions[15].id  # 自然保护区
            },
            # 沙漠绿洲的AI
            {
                'name': '环境改造AI',
                'type': '改造型',
                'status': 'maintenance',
                'description': '负责沙漠环境改造的AI，研究如何在极端环境中种植植物。',
                'capabilities': {'环境科学': '高级', '植物学': '中级', '数据分析': '高级'},
                'image_url': None,
                'region_id': created_regions[16].id  # 沙漠绿洲
            }
        ]
        
        # 批量创建AI信息
        created_ais = []
        for ai_data in ai_info_list:
            ai = AIMapAIInfo(**ai_data)
            db.session.add(ai)
            created_ais.append(ai)
        
        # 提交AI数据
        db.session.commit()
        print(f"创建了 {len(created_ais)} 个AI")
        
        # 创建事件
        events = [
            {
                'region_id': created_regions[14].id,  # 科技都市
                'title': '跨维度科技展览',
                'content': '赛博都市将举办年度AI科技展览，展示来自各个维度的最新AI技术和应用。',
                'event_type': 'activity',
                'severity': 'normal',
                'start_time': datetime.now(),
                'end_time': None,
                'is_active': True
            },
            {
                'region_id': created_regions[15].id,  # 自然保护区
                'title': '神话生物迁徙',
                'content': '神话森林内的神话生物开始年度迁徙，AI正在密切监测。',
                'event_type': 'natural',
                'severity': 'low',
                'start_time': datetime.now(),
                'end_time': None,
                'is_active': True
            },
            {
                'region_id': created_regions[16].id,  # 沙漠绿洲
                'title': '时空水源项目启动',
                'content': '时空绿洲的新水源开发项目正式启动，AI将全程参与。',
                'event_type': 'project',
                'severity': 'medium',
                'start_time': datetime.now(),
                'end_time': None,
                'is_active': True
            }
        ]
        
        # 批量创建事件
        created_events = []
        for event_data in events:
            event = AIMapEvent(**event_data)
            db.session.add(event)
            created_events.append(event)
        
        # 提交事件数据
        db.session.commit()
        print(f"创建了 {len(created_events)} 个事件")
        
        print("地图测试数据初始化完成！")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='初始化地图测试数据')
    parser.add_argument('--force', '-f', action='store_true', help='强制更新数据，删除现有数据并重新插入')
    
    args = parser.parse_args()
    init_map_data(force_update=args.force)