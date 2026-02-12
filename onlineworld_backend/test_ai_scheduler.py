#!/usr/bin/env python3
"""
测试调度AI功能
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_scheduler import AIScheduler
from app import app

def test_scheduler():
    """测试调度器功能"""
    print("🚀 开始测试调度AI功能")
    print("=" * 60)
    
    # 创建调度器实例
    scheduler = AIScheduler()
    
    # 测试1: 生成执行计划
    print("\n📋 测试1: 生成执行计划")
    print("-" * 40)
    
    task_description = "生成一个服务器运维的帖子和对应的运维工具"
    print(f"任务描述: {task_description}")
    
    plan = scheduler.generate_execution_plan(task_description)
    print(f"生成的执行计划: {json.dumps(plan, ensure_ascii=False, indent=2)}")
    
    # 测试2: 执行计划
    print("\n🔄 测试2: 执行计划")
    print("-" * 40)
    
    try:
        with app.app_context():
            results = scheduler.execute_plan(plan)
            print(f"执行结果: {json.dumps(results, ensure_ascii=False, indent=2)}")
            print(f"✅ 执行成功，共生成 {len(results)} 个内容")
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
    
    # 测试3: 完整任务流程
    print("\n🎯 测试3: 完整任务流程")
    print("-" * 40)
    
    try:
        with app.app_context():
            result = scheduler.run_task(task_description)
            print(f"任务结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            if result.get("status") == "success":
                print("✅ 完整任务流程执行成功")
            else:
                print("❌ 完整任务流程执行失败")
    except Exception as e:
        print(f"❌ 完整任务流程失败: {str(e)}")
    
    # 测试4: 测试不同类型的任务
    print("\n🧪 测试4: 测试不同类型的任务")
    print("-" * 40)
    
    test_tasks = [
        "生成一个关于编程技巧的帖子",
        "生成一个生活闲聊的帖子并添加回复",
        "生成一个游戏攻略的帖子"
    ]
    
    for i, test_task in enumerate(test_tasks):
        print(f"\n测试任务 {i+1}: {test_task}")
        try:
            with app.app_context():
                result = scheduler.run_task(test_task)
                if result.get("status") == "success":
                    print(f"✅ 任务 {i+1} 执行成功")
                else:
                    print(f"❌ 任务 {i+1} 执行失败")
        except Exception as e:
            print(f"❌ 任务 {i+1} 失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ 调度AI功能测试完成")

if __name__ == "__main__":
    test_scheduler()
