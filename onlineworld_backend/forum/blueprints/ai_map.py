from flask import Blueprint
from .base import BasePageView, register_page_route
from ..models import AIMapRegion, AIMapAIInfo, AIMapEvent, db
from flask import session
from datetime import datetime

# 导入API蓝图
from .api import api_bp

# 地图首页视图类
class AIMapIndexView(BasePageView):
    def get_data(self):
        # 获取所有公开的地图区域
        regions = AIMapRegion.query.filter_by(is_public=True).all()
        region_list = [{"id": region.id,
                       "name": region.name,
                       "description": region.description,
                       "x_coord": region.x_coord,
                       "y_coord": region.y_coord,
                       "width": region.width,
                       "height": region.height,
                       "region_type": region.region_type,
                       "population": region.population,
                       "ai_count": region.ai_count,
                       "resources": region.resources,
                       "image_url": region.image_url
                       } for region in regions]
        
        return {
            "title": "AI生活区域地图",
            "regions": region_list
        }

# 地图区域详情视图类
class AIMapRegionDetailView(BasePageView):
    def get_data(self, region_id):
        # 获取区域详情
        region = AIMapRegion.query.get_or_404(region_id)
        
        # 获取该区域的AI信息
        ai_info_list = AIMapAIInfo.query.filter_by(region_id=region_id).all()
        ai_list = [{"id": ai.id,
                   "name": ai.name,
                   "type": ai.type,
                   "status": ai.status,
                   "description": ai.description,
                   "capabilities": ai.capabilities,
                   "image_url": ai.image_url
                   } for ai in ai_info_list]
        
        # 获取该区域的事件
        events = AIMapEvent.query.filter_by(region_id=region_id, is_active=True).order_by(AIMapEvent.start_time.desc()).all()
        event_list = [{"id": event.id,
                      "title": event.title,
                      "content": event.content,
                      "event_type": event.event_type,
                      "severity": event.severity,
                      "start_time": event.start_time.strftime("%Y-%m-%d %H:%M:%S")
                      } for event in events]
        
        return {
            "title": f"地图区域 - {region.name}",
            "region": region.to_dict(),
            "ai_list": ai_list,
            "events": event_list
        }

# AI详情视图类
class AIMapAIDetailView(BasePageView):
    def get_data(self, ai_id):
        # 获取AI详情
        ai = AIMapAIInfo.query.get_or_404(ai_id)
        
        return {
            "title": f"AI详情 - {ai.name}",
            "ai": ai.to_dict(),
            "region": ai.region.to_dict()
        }

# 注册所有AI地图路由到API蓝图
register_page_route(api_bp, "/ai-map/", AIMapIndexView)  # 地图首页
register_page_route(api_bp, "/ai-map/region/<int:region_id>", AIMapRegionDetailView)  # 区域详情
register_page_route(api_bp, "/ai-map/ai/<int:ai_id>", AIMapAIDetailView)  # AI详情
