# 商城自动管理功能说明

## 概述

本模块实现了一个基于硅基流动大模型的商城商品自动生成和管理系统，类似于咸鱼的虚拟P2P交易平台功能。主要功能包括：

1. 从论坛用户中自动提取商家名称
2. 通过硅基流动大模型生成商品数据
3. 自动创建商家和商品信息
4. 定期下架过期商品（标记为非活动状态而非删除）

## 文件结构

- `shop_ai_generator.py` - 核心功能实现，包含ShopAIGenerator类
- `shop_maintenance.py` - 维护脚本，可定期执行商品管理任务

## 核心类：ShopAIGenerator

### 主要方法

1. **get_merchant_names_from_forum(limit=20)**
   - 从论坛的Post和Reply表中提取作者名称作为商家名称
   - 自动去重并返回指定数量的名称

2. **generate_product_data(category_name, merchant_name)**
   - 调用硅基流动大模型API生成商品数据
   - 参数：商品分类名称、商家名称
   - 返回：包含商品名称、描述、价格、图片数量和标签的字典

3. **generate_products(count=10)**
   - 批量生成指定数量的商品
   - 自动创建商家和商品记录

4. **deactivate_old_products(days_threshold=7)**
   - 下架超过指定天数的商品
   - 将商品状态从"active"改为"inactive"

5. **run_maintenance(products_to_generate=10, days_threshold=7)**
   - 执行完整的维护任务：下架过期商品并生成新商品

## 使用方法

### 1. 手动调用API

在应用中导入ShopAIGenerator类并使用：

```python
from shop_ai_generator import ShopAIGenerator
from forum.models import db

# 初始化生成器
generator = ShopAIGenerator(db, app.config)

# 生成5个新商品
new_products = generator.generate_products(count=5)

# 下架14天前的商品
deactivated_count = generator.deactivate_old_products(days_threshold=14)
```

### 2. 使用维护脚本

可以直接运行维护脚本来执行定期维护：

```bash
python shop_maintenance.py --generate 15 --days 7
```

参数说明：
- `--generate`: 指定要生成的商品数量（默认10）
- `--days`: 指定商品下架的天数阈值（默认7天）

### 3. 设置定时任务

可以通过系统的crontab或Windows计划任务来定期执行维护脚本，例如每天凌晨3点执行：

```
# Linux/Mac (crontab)
0 3 * * * cd /path/to/onlineworld_backend && python shop_maintenance.py

# Windows (计划任务)
创建计划任务，设置执行路径和参数
```

## 配置要求

在应用配置中需要设置：

```python
# 硅基流动大模型API配置
SILICON_FLOW_API_KEY = 'your_api_key_here'
SILICON_FLOW_API_BASE = 'https://api.siliconflow.cn/v1/chat/completions'
```

## 注意事项

1. 确保数据库中有可用的商品分类（ShopCategory表）
2. 商品下架是通过修改status字段实现，不会删除数据
3. 使用API时会有请求延迟，建议合理设置请求间隔
4. 定期检查维护日志以监控系统运行状态
