#!/usr/bin/env python3
"""
查询搜索索引表内容的临时脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from forum.models import SearchIndex

# 创建数据库引擎和会话
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

try:
    print('=== 搜索索引表内容（前20条） ===')
    search_items = session.query(SearchIndex).limit(20).all()
    for idx, item in enumerate(search_items, 1):
        print(f'{idx}. ID: {item.id}, 标题: {item.title}, 类型: {item.entity_type}, URL: {item.url}')
    
    print('\n=== 搜索索引总数 ===')
    total_count = session.query(SearchIndex).count()
    print(f'总共有 {total_count} 条搜索索引记录')
    
    # 搜索包含"商品"或"论坛"的记录
    print('\n=== 包含"商品"或"论坛"的索引记录 ===')
    keyword_items = session.query(SearchIndex).filter(
        SearchIndex.title.ilike('%商品%') | SearchIndex.title.ilike('%论坛%')
    ).all()
    
    if keyword_items:
        for idx, item in enumerate(keyword_items, 1):
            print(f'{idx}. ID: {item.id}, 标题: {item.title}, 类型: {item.entity_type}, URL: {item.url}')
    else:
        print('没有找到包含"商品"或"论坛"的记录')
        
finally:
    session.close()
