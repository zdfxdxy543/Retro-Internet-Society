#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
商城商品自动管理定时任务脚本
用于定期执行商品生成和下架任务
"""

import sys
import os
import time
import logging
import threading
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shop_auto_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("shop_auto_manager")


class ShopAutoManager:
    """
    商城自动管理类
    负责定期生成商品和下架过期商品
    """
    
    def __init__(self, db=None, config=None):
        """
        初始化自动管理器
        
        :param db: 数据库实例
        :param config: 配置字典
        """
        self.db = db
        self.config = config
        self.running = False
        self.generate_interval = 6 * 60 * 60  # 6小时，单位秒
        self.deactivate_interval = 24 * 60 * 60  # 24小时，单位秒
        self.generate_thread = None
        self.deactivate_thread = None
    
    def generate_products_task(self):
        """
        定期生成商品任务
        """
        while self.running:
            try:
                logger.info("开始执行商品生成任务")
                
                # 导入必要模块
                from app import app  # 直接导入app实例
                from forum.models import db
                from shop_ai_generator import ShopAIGenerator
                
                # 使用应用上下文
                with app.app_context():
                    # 初始化生成器
                    generator = ShopAIGenerator(db, app.config)
                    
                    # 生成5个商品
                    result = generator.generate_products(5)
                    logger.info(f"商品生成任务执行完成: {result}")
                    
            except Exception as e:
                logger.error(f"执行商品生成任务时出错: {str(e)}")
                
            # 等待下一次执行
            time.sleep(self.generate_interval)
    
    def deactivate_products_task(self):
        """
        定期下架过期商品任务
        """
        while self.running:
            try:
                logger.info("开始执行商品下架任务")
                
                # 导入必要模块
                from app import app  # 直接导入app实例
                from forum.models import db
                from shop_ai_generator import ShopAIGenerator
                
                # 使用应用上下文
                with app.app_context():
                    # 初始化生成器
                    generator = ShopAIGenerator(db, app.config)
                    
                    # 下架7天前的商品
                    result = generator.deactivate_old_products(7)
                    logger.info(f"商品下架任务执行完成: {result}")
                    
            except Exception as e:
                logger.error(f"执行商品下架任务时出错: {str(e)}")
                
            # 等待下一次执行
            time.sleep(self.deactivate_interval)
    
    def start(self):
        """
        启动自动管理任务
        """
        if self.running:
            logger.warning("自动管理任务已经在运行中")
            return {"status": "warning", "message": "自动管理任务已经在运行中"}
            
        self.running = True
        
        # 启动商品生成任务线程
        self.generate_thread = threading.Thread(target=self.generate_products_task)
        self.generate_thread.daemon = True
        self.generate_thread.start()
        
        # 启动商品下架任务线程
        self.deactivate_thread = threading.Thread(target=self.deactivate_products_task)
        self.deactivate_thread.daemon = True
        self.deactivate_thread.start()
        
        logger.info("商城自动管理任务已启动")
        return {"status": "success", "message": "商城自动管理任务已启动"}
    
    def stop(self):
        """
        停止自动管理任务
        """
        if not self.running:
            logger.warning("自动管理任务未在运行")
            return {"status": "warning", "message": "自动管理任务未在运行"}
            
        self.running = False
        
        # 等待线程结束
        if self.generate_thread and self.generate_thread.is_alive():
            self.generate_thread.join(timeout=5.0)
            
        if self.deactivate_thread and self.deactivate_thread.is_alive():
            self.deactivate_thread.join(timeout=5.0)
            
        logger.info("商城自动管理任务已停止")
        return {"status": "success", "message": "商城自动管理任务已停止"}
    
    def run_generate_products(self, count=5):
        """
        手动运行商品生成任务
        
        :param count: 生成数量
        :return: 执行结果
        """
        try:
            logger.info(f"手动执行商品生成任务，生成数量: {count}")
            
            # 导入必要模块
            from app import app  # 直接导入app实例
            from forum.models import db
            from shop_ai_generator import ShopAIGenerator
            
            # 使用应用上下文
            with app.app_context():
                # 初始化生成器
                generator = ShopAIGenerator(db, app.config)
                
                # 生成指定数量的商品
                result = generator.generate_products(count)
                logger.info(f"手动商品生成任务执行完成: {result}")
                return result
                
        except Exception as e:
            logger.error(f"手动执行商品生成任务时出错: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_deactivate_products(self, days_threshold=7):
        """
        手动运行商品下架任务
        
        :param days_threshold: 下架天数阈值
        :return: 执行结果
        """
        try:
            logger.info(f"手动执行商品下架任务，天数阈值: {days_threshold}")
            
            # 导入必要模块
            from app import app  # 直接导入app实例
            from forum.models import db
            from shop_ai_generator import ShopAIGenerator
            
            # 使用应用上下文
            with app.app_context():
                # 初始化生成器
                generator = ShopAIGenerator(db, app.config)
                
                # 下架过期商品
                result = generator.deactivate_old_products(days_threshold)
                logger.info(f"手动商品下架任务执行完成: {result}")
                return result
                
        except Exception as e:
            logger.error(f"手动执行商品下架任务时出错: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_maintenance(self, products_to_generate=5, days_threshold=7):
        """
        手动运行维护任务（先下架，再生成）
        
        :param products_to_generate: 生成商品数量
        :param days_threshold: 下架天数阈值
        :return: 执行结果
        """
        try:
            logger.info(f"手动执行维护任务，生成数量: {products_to_generate}, 下架天数: {days_threshold}")
            
            # 导入必要模块
            from app import app  # 直接导入app实例
            from forum.models import db
            from shop_ai_generator import ShopAIGenerator
            
            # 使用应用上下文
            with app.app_context():
                # 初始化生成器
                generator = ShopAIGenerator(db, app.config)
                
                # 执行维护任务
                result = generator.run_maintenance(
                    products_to_generate=products_to_generate,
                    days_threshold=days_threshold
                )
                logger.info(f"手动维护任务执行完成: {result}")
                return result
                
        except Exception as e:
            logger.error(f"手动执行维护任务时出错: {str(e)}")
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # 创建并启动自动管理器
    manager = ShopAutoManager()
    
    # 命令行交互
    import argparse
    
    parser = argparse.ArgumentParser(description='商城自动管理脚本')
    parser.add_argument('--start', action='store_true', help='启动自动管理任务')
    parser.add_argument('--stop', action='store_true', help='停止自动管理任务')
    parser.add_argument('--generate', type=int, help='生成指定数量的商品')
    parser.add_argument('--deactivate', type=int, help='下架指定天数前的商品')
    parser.add_argument('--maintenance', action='store_true', help='执行维护任务')
    parser.add_argument('--count', type=int, default=5, help='维护任务中生成的商品数量')
    parser.add_argument('--days', type=int, default=7, help='维护任务中的下架天数阈值')
    
    args = parser.parse_args()
    
    # 根据参数执行相应操作
    if args.start:
        manager.start()
        print("自动管理任务已启动，按Ctrl+C停止")
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
            print("自动管理任务已停止")
            
    elif args.stop:
        result = manager.stop()
        print(f"操作结果: {result}")
        
    elif args.generate is not None:
        result = manager.run_generate_products(args.generate)
        print(f"操作结果: {result}")
        
    elif args.deactivate is not None:
        result = manager.run_deactivate_products(args.deactivate)
        print(f"操作结果: {result}")
        
    elif args.maintenance:
        result = manager.run_maintenance(args.count, args.days)
        print(f"操作结果: {result}")
        
    else:
        parser.print_help()