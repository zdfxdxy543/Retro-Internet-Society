import os
import sys
from app import app, db
from forum.datasheet_generator import DataSheetGenerator

try:
    with app.app_context():
        # 创建DataSheetGenerator实例
        generator = DataSheetGenerator()
        
        # 批量生成所有产品的DataSheet
        result = generator.generate_all_datasheets()
        
        # 打印生成结果
        print(f"批量生成DataSheet结果：")
        print(f"总产品数：{result.get('total', 'N/A')}")
        print(f"成功生成：{result.get('generated', 'N/A')}")
        print(f"已存在跳过：{result.get('skipped', 'N/A')}")
        print(f"生成失败：{result.get('failed', 'N/A')}")
        print(f"状态：{'成功' if result.get('success', False) else '失败'}")
        print(f"消息：{result.get('message', '无消息')}")
        
        # 如果有失败，设置退出码
        if result.get('failed', 0) > 0 or not result.get('success', False):
            sys.exit(1)
except ImportError as e:
    print(f"导入模块失败: {str(e)}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"执行过程中发生错误: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)