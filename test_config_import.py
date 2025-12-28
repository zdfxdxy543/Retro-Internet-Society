#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试脚本：验证所有修改后的AI工具文件能否正确导入配置"""

print("===== 开始测试配置导入 =====")

try:
    print("\n1. 测试 config.py 导入")
    from config import Config
    print(f"   ✓ 成功导入 Config 类")
    print(f"   ✓ 配置项测试: API_KEY={Config.SILICON_FLOW_API_KEY[:10]}...")
    print(f"   ✓ 配置项测试: API_URL={Config.SILICON_FLOW_API_URL}")
    print(f"   ✓ 配置项测试: MODEL_NAME={Config.AI_MODEL_NAME}")
    print(f"   ✓ 配置项测试: TEST_MODE={Config.TEST_MODE}")
    
except Exception as e:
    print(f"   ✗ config.py 导入失败: {e}")

try:
    print("\n2. 测试 ai_content_generator.py 导入")
    from ai_content_generator import AIContentGenerator
    print(f"   ✓ 成功导入 AIContentGenerator 类")
    # 简单测试实例化（不实际运行API调用）
    generator = AIContentGenerator()
    print(f"   ✓ 成功实例化 AIContentGenerator")
    print(f"   ✓ 配置项验证: generator.api_key={generator.api_key[:10]}...")
    print(f"   ✓ 配置项验证: generator.api_url={generator.api_url}")
    print(f"   ✓ 配置项验证: generator.model_name={generator.model_name}")
    
except Exception as e:
    print(f"   ✗ ai_content_generator.py 导入失败: {e}")

try:
    print("\n3. 测试 ai_tools.py 导入")
    from ai_tools import tool_registry
    print(f"   ✓ 成功导入 tool_registry")
    tools = tool_registry.list_tools()
    print(f"   ✓ 工具注册表中有 {len(tools)} 个工具")
    for tool in tools:
        print(f"   ✓ 工具: {tool.name()} - {tool.description()[:30]}...")
    
except Exception as e:
    print(f"   ✗ ai_tools.py 导入失败: {e}")

try:
    print("\n4. 测试 shop_ai_generator.py 导入")
    from shop_ai_generator import ShopAIGenerator
    print(f"   ✓ 成功导入 ShopAIGenerator 类")
    # 由于ShopAIGenerator需要数据库对象，这里只测试导入
    
except Exception as e:
    print(f"   ✗ shop_ai_generator.py 导入失败: {e}")

print("\n===== 测试完成 =====")
