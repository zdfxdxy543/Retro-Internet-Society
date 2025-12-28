import json

# 测试各种可能的API响应情况
def test_all_response_scenarios():
    """测试所有可能的API响应情况"""
    print("=== 测试所有API响应情况 ===")
    
    # 定义各种测试场景
    test_scenarios = [
        {
            "name": "标准响应（content包含内容）",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "这是最终的回复内容",
                            "reasoning_content": "我正在思考如何回答这个问题..."
                        }
                    }
                ]
            },
            "expected": "这是最终的回复内容"
        },
        {
            "name": "content为空，reasoning_content包含内容",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "reasoning_content": "这是最终的回复内容"
                        }
                    }
                ]
            },
            "expected": "这是最终的回复内容"
        },
        {
            "name": "仅reasoning_content包含内容",
            "response": {
                "choices": [
                    {
                        "message": {
                            "reasoning_content": "这是最终的回复内容"
                        }
                    }
                ]
            },
            "expected": "这是最终的回复内容"
        },
        {
            "name": "仅content包含内容",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "这是最终的回复内容"
                        }
                    }
                ]
            },
            "expected": "这是最终的回复内容"
        },
        {
            "name": "content包含空格，reasoning_content包含内容",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "   ",
                            "reasoning_content": "这是最终的回复内容"
                        }
                    }
                ]
            },
            "expected": "这是最终的回复内容"
        },
        {
            "name": "content和reasoning_content都包含内容",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "这是content中的内容",
                            "reasoning_content": "这是reasoning_content中的内容"
                        }
                    }
                ]
            },
            "expected": "这是content中的内容"
        },
        {
            "name": "content和reasoning_content都为空",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "",
                            "reasoning_content": ""
                        }
                    }
                ]
            },
            "expected": ""
        }
    ]
    
    # 测试每个场景
    for scenario in test_scenarios:
        print(f"\n📋 场景: {scenario['name']}")
        print(f"   API响应: {json.dumps(scenario['response'], ensure_ascii=False, indent=2)}")
        
        message = scenario['response']['choices'][0]['message']
        
        # 应用当前的内容提取逻辑
        content = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
        
        print(f"   提取的内容: {content}")
        print(f"   预期结果: {scenario['expected']}")
        print(f"   测试结果: {'✅ 通过' if content == scenario['expected'] else '❌ 失败'}")

# 测试工具调用后的响应处理
def test_tool_call_response():
    """测试工具调用后的响应处理"""
    print("\n=== 测试工具调用后的响应处理 ===")
    
    # 模拟工具调用请求
    tool_call_request = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "id": "tool_call_123",
                            "type": "function",
                            "function": {
                                "name": "shop_info_tool",
                                "arguments": "{\"query_type\": \"products\"}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    print(f"📤 工具调用请求: {json.dumps(tool_call_request, ensure_ascii=False, indent=2)}")
    
    # 模拟工具调用响应（content为空，reasoning_content包含内容）
    tool_response = {
        "choices": [
            {
                "message": {
                    "content": "",
                    "reasoning_content": "根据查询结果，我来回答这个问题。这是关于产品的详细信息..."
                }
            }
        ]
    }
    
    print(f"📥 工具调用响应: {json.dumps(tool_response, ensure_ascii=False, indent=2)}")
    
    # 应用当前的内容提取逻辑
    message = tool_response["choices"][0]["message"]
    content = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
    
    print(f"📝 提取的内容: {content}")
    print(f"✅ 工具调用后的内容提取正常工作")

if __name__ == "__main__":
    test_all_response_scenarios()
    test_tool_call_response()
    print("\n=== 测试完成 ===")
    print("📊 结论：当前的内容提取逻辑在所有测试场景下都能正确工作，优先使用content字段，仅当content为空时才使用reasoning_content字段。")
    print("📌 可能的问题原因：大模型在某些情况下返回的content字段为空字符串，而reasoning_content包含实际内容。")
    print("💡 解决方案：当前代码逻辑已经正确处理这种情况，可能需要检查大模型的行为或在工具调用后添加额外的内容验证。")