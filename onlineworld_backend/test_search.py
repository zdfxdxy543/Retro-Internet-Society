#!/usr/bin/env python3
"""
搜索功能测试脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from forum.models import SearchIndex, Board, Post, ShopProduct, DynamicPage, ShopCategory, ShopMerchant, Product, ProductCategory

# 数据库配置
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# 创建数据库引擎和会话
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_search(keyword):
    """测试搜索功能"""
    print(f"\n{'='*60}")
    print(f"测试搜索: '{keyword}'")
    print('='*60)
    
    db = SessionLocal()
    try:
        # 1. 分割关键词，去除空字符串
        keywords = [k.strip() for k in keyword.split() if k.strip()]
        
        # 调试：输出原始关键词和分割后的关键词
        print(f"[调试] 原始搜索关键词: '{keyword}'")
        print(f"[调试] 分割后的关键词列表: {keywords}")
        
        if not keywords:
            print("❌ 请输入有效搜索关键词")
            return
        
        # 2. 基本搜索（包含所有关键词）
        # 使用原生SQLAlchemy查询，避免Flask上下文问题
        from sqlalchemy import and_
        from sqlalchemy.sql import text
        
        # 构建查询条件
        print(f"[调试] 开始构建查询")
        query = db.query(SearchIndex)
        for k in keywords:
            # 转义特殊字符，避免SQL注入
            safe_k = k.replace('%', '\\%').replace('_', '\\_')
            print(f"[调试] 添加关键词过滤: '{k}' (转义后: '{safe_k}')")
            print(f"[调试] 过滤条件: SearchIndex.title.ilike('%{safe_k}%')")
            query = query.filter(SearchIndex.title.ilike(f'%{safe_k}%', escape='\\'))
        
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
        
        # 5. 输出结果
        print(f"找到 {len(sorted_results)} 条相关结果:")
        print('-'*60)
        
        for idx, r in enumerate(sorted_results, 1):
            sort_level = get_sort_level(r.title, keyword)
            level_name = {1: "完全匹配", 2: "开头匹配", 3: "包含匹配"}[sort_level]
            print(f"{idx}. [{level_name}] [{r.entity_type}] {r.title}")
            print(f"   URL: {r.url}")
            print(f"   更新时间: {r.update_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
        if not sorted_results:
            print("❌ 没有找到相关结果")
            
    finally:
        db.close()

def main():
    """主函数"""
    print("🚀 搜索功能测试工具")
    print("="*60)
    print("支持的测试用例:")
    print("1. 单关键词搜索: python test_search.py '测试'")
    print("2. 多关键词搜索: python test_search.py '测试 关键词'")
    print("3. 特殊字符搜索: python test_search.py '测试%关键词'")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("❌ 请提供搜索关键词")
        print("用法: python test_search.py '搜索关键词'")
        sys.exit(1)
    
    keyword = sys.argv[1]
    test_search(keyword)

if __name__ == "__main__":
    main()