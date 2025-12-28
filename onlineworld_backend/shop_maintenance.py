#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
商城维护脚本
用于定期执行商城维护任务，包括下架过期商品和自动生成新商品
"""

import sys
import os
import time
import logging
from datetime import datetime

# 添加项目根目录到Python路径，确保能够导入所需模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shop_maintenance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("shop_maintenance")


def run_maintenance(products_to_generate=10, days_threshold=7):
    """
    运行商城维护任务
    
    :param products_to_generate: 要生成的商品数量
    :param days_threshold: 下架天数阈值
    :return: 维护结果
    """
    try:
        # 导入必要的模块
        from app import app  # 直接导入app实例
        from forum.models import db
        from shop_ai_generator import ShopAIGenerator
        
        # 使用应用上下文
        with app.app_context():
            logger.info("开始执行商城维护任务")
            start_time = time.time()
            
            # 初始化商品生成器
            generator = ShopAIGenerator(db, app.config)
            
            # 执行维护任务
            result = generator.run_maintenance(
                products_to_generate=products_to_generate,
                days_threshold=days_threshold
            )
            
            # 记录执行时间
            end_time = time.time()
            execution_time = end_time - start_time
            result["execution_time_seconds"] = execution_time
            
            logger.info(f"商城维护任务执行完成: {result}")
            return result
            
    except Exception as e:
        logger.error(f"执行商城维护任务时出错: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # 解析命令行参数（如果有）
    import argparse
    
    parser = argparse.ArgumentParser(description='商城维护脚本')
    parser.add_argument('--generate', type=int, default=10, help='要生成的商品数量')
    parser.add_argument('--days', type=int, default=7, help='下架天数阈值')
    
    args = parser.parse_args()
    
    # 执行维护任务
    result = run_maintenance(
        products_to_generate=args.generate,
        days_threshold=args.days
    )
    
    # 输出结果
    print(f"维护任务执行结果: {result}")
    
    # 退出状态码
    sys.exit(0 if "status" not in result else 1)