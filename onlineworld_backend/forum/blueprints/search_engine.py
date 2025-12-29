from flask import Blueprint, request, jsonify
from .base import BasePageView, register_page_route
from ..models import SearchIndex

# 创建搜索引擎蓝图
search_engine_bp = Blueprint('search_engine', __name__, url_prefix='/search-engine')

# 搜索引擎首页视图类
class SearchEngineHomeView(BasePageView):
    def get_data(self):
        # 搜索引擎首页数据
        return {
            "title": "NexusSearch - 首页",  # 搜索引擎名称：NexusSearch（连接搜索）
            "description": "搜索互联网上的一切页面",
            "search_placeholder": "输入关键词进行搜索..."
        }

# 搜索结果页面视图类
class SearchResultView(BasePageView):
    def get_data(self):
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return {
                "title": "NexusSearch - 搜索结果",
                "keyword": keyword,
                "results": [],
                "message": "请输入搜索关键词"
            }
        
        # 改进的搜索算法：支持多关键词搜索
        # 1. 分割关键词，去除空字符串
        keywords = [k.strip() for k in keyword.split() if k.strip()]
        
        # 调试：输出原始关键词和分割后的关键词
        print(f"[调试] 原始搜索关键词: '{keyword}'")
        print(f"[调试] 分割后的关键词列表: {keywords}")
        
        if not keywords:
            return {
                "title": "NexusSearch - 搜索结果",
                "keyword": keyword,
                "results": [],
                "message": "请输入有效搜索关键词"
            }
        
        # 2. 基本搜索（包含所有关键词）
        query = SearchIndex.query
        
        # 调试：输出查询构建过程
        print(f"[调试] 开始构建查询")
        for k in keywords:
            # 转义特殊字符，避免SQL注入
            safe_k = k.replace('%', '\\%').replace('_', '\\_')
            print(f"[调试] 添加关键词过滤: '{k}' (转义后: '{safe_k}')")
            print(f"[调试] 过滤条件: SearchIndex.title.ilike('%{safe_k}%')")
            query = query.filter(SearchIndex.title.ilike(f'%{safe_k}%', escape='\\'))
        
        # 3. 获取结果
        results = query.all()
        print(f"[调试] 查询结果数量: {len(results)}")
        print(f"[调试] 查询结果详情: {[(r.id, r.title, r.entity_type) for r in results]}")
        
        # 4. 三级排序：完全相符 > 开头匹配 > 包含匹配
        def get_sort_level(title, keyword_string):
            """获取排序级别：1级=完全匹配，2级=开头匹配，3级=包含匹配"""
            title_lower = title.lower()
            keyword_lower = keyword_string.lower()
            
            # 调试：排序级别计算
            print(f"[调试] 标题: '{title_lower}', 关键词: '{keyword_lower}'")
            
            # 1级：完全匹配
            if title_lower == keyword_lower:
                print(f"[调试]  完全匹配，返回级别1")
                return 1
            
            # 2级：开头匹配（标题以搜索词开头）
            if title_lower.startswith(keyword_lower):
                print(f"[调试]  开头匹配，返回级别2")
                return 2
            
            # 3级：包含匹配（标题包含搜索词）
            print(f"[调试]  包含匹配，返回级别3")
            return 3
        
        # 按级别排序，同一级别内按更新时间降序
        print(f"[调试] 开始三级排序，结果数量: {len(results)}")
        sorted_results = sorted(
            results, 
            key=lambda r: (get_sort_level(r.title, keyword), r.update_time), 
            reverse=True
        )
        print(f"[调试] 排序完成，排序后结果数量: {len(sorted_results)}")
        print(f"[调试] 排序后结果详情: {[(r.id, r.title, r.entity_type) for r in sorted_results]}")
        
        # 5. 格式化结果
        formatted_results = []
        for r in sorted_results:
            formatted_results.append({
                "id": r.id, 
                "title": r.title, 
                "type": r.entity_type, 
                "url": r.url, 
                "update_time": r.update_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {
            "title": f"NexusSearch - '{keyword}'的搜索结果",
            "keyword": keyword,
            "results": formatted_results,
            "result_count": len(formatted_results),
            "message": f"找到 {len(formatted_results)} 条相关结果" if results else "没有找到相关结果"
        }

# 注册路由
register_page_route(search_engine_bp, "/", SearchEngineHomeView)  # 搜索引擎首页
register_page_route(search_engine_bp, "/search", SearchResultView)  # 搜索结果页面
