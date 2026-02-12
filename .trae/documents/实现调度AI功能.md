# 实现调度AI功能计划

## 项目分析

基于对现有项目的分析，我发现：

1. **现有AI工具系统**：在 `ai_tools.py` 中定义了基础工具类和各种具体工具，包括论坛信息、公司信息、地图位置和商店信息工具。

2. **AI内容生成函数**：在 `ai_content_generator.py` 中实现了AI内容生成函数，包括：

   * `generate_new_posts()`：生成新帖子（包含数据库写入）

   * `generate_replies()`：生成回复（包含数据库写入）

   * `generate_content_with_tools()`：带工具调用的内容生成

   * `call_siliconflow_api()`：调用硅基流动API

3. **网盘功能**：在 `disk_file_generator.py` 中实现了 `DiskFileGenerator` 类，用于生成网盘文件并在数据库中注册。

4. **API接口**：在 `api.py` 中定义了各种API接口，包括网盘文件下载等。

## 实现方案

### 1. 创建调度器核心模块

**文件**：`onlineworld_backend/ai_scheduler.py`

**功能**：

* 定义 `AIScheduler` 类，负责生成执行序列并按照序列执行

* 实现 `ResourcePool` 类，存储中间生成结果

* 实现 `StepExecutor` 类，执行具体的生成步骤

* **调用现有AI生成函数**：直接调用 `ai_content_generator.py` 中的函数

* **使用现有网盘生成**：使用 `DiskFileGenerator` 生成网盘文件

### 2. 实现执行序列生成

**功能**：

* 调用API生成执行步骤序列

* 解析序列并转换为可执行的步骤

* 支持步骤间的依赖关系处理

* **可扩展性**：通过配置文件或动态注册支持新的生成函数

### 3. 实现资源池管理

**功能**：

* 存储和管理中间生成结果

* 支持步骤间的数据传递

* 提供资源查询和获取接口

### 4. 实现步骤执行器

**功能**：

* 执行具体的生成步骤

* 处理步骤执行结果

* 管理步骤执行状态

* **调用现有生成函数**：直接使用现有的AI生成函数执行具体任务

### 5. 添加API接口

**文件**：`onlineworld_backend/forum/blueprints/api.py`

**功能**：

* 添加调度AI的API接口

* 支持接收任务请求

* 返回执行结果和状态

### 6. 测试和集成

**功能**：

* 测试调度AI的完整流程

* 集成到现有系统中

* 确保与现有功能的兼容性

## 示例流程

### 示例：生成服务器运维的帖子和对应的运维工具

1. **接收任务请求**：

   ```json
   {
     "task": "生成一个服务器运维的帖子和对应的运维工具",
     "parameters": {
       "board_id": 1,
       "title": "服务器运维经验分享"
     }
   }
   ```

2. **生成执行序列**：

   ```json
   {
     "steps": [
       {
         "id": "step_1",
         "type": "disk_file",
         "params": {
           "content": "服务器运维指南内容...",
           "file_name": "服务器运维指南"
         }
       },
       {
         "id": "step_2",
         "type": "post",
         "params": {
           "board_id": 1,
           "title": "服务器运维经验分享",
           "use_resources": ["step_1"]
         }
       },
       {
         "id": "step_3",
         "type": "reply",
         "params": {
           "post_id": "step_2",
           "content": "分享一些运维工具推荐"
         }
       }
     ]
   }
   ```

3. **执行步骤**：

   * **步骤1**：使用 `DiskFileGenerator.generate_disk_file()` 生成网盘文件，内容为服务器运维指南，存储到资源池

   * **步骤2**：使用 `ai_content_generator.py` 中的函数生成帖子，使用步骤1的资源（网盘文件链接）

   * **步骤3**：使用 `ai_content_generator.py` 中的函数生成回复，回复步骤2生成的帖子

4. **返回结果**：

   ```json
   {
     "status": "success",
     "result": {
       "disk_file": {
         "share_id": "ABC123",
         "password": "123456",
         "file_name": "服务器运维指南.txt",
         "file_path": "/static/files/online_disk/服务器运维指南.txt"
       },
       "post": {
         "id": 123,
         "title": "服务器运维经验分享",
         "content": "...包含网盘链接...",
         "author": "运维老司机"
       },
       "reply": {
         "id": 456,
         "content": "分享一些运维工具推荐...",
         "author": "技术爱好者"
       }
     }
   }
   ```

## 技术要点

1. **模块化设计**：将调度器、资源池和执行器分离，提高可维护性

2. **架构遵循**：

   * 前端显示 → 后端API → 数据库 → AI工具 → AI内容生成 → AI调度

   * 确保每个组件都在正确的层级

3. **扩展性**：

   * 支持配置文件定义新的生成函数

   * 支持动态注册生成函数

   * 新添加的API和工具会自动被识别和使用

4. **错误处理**：完善的错误处理机制，确保系统稳定性

5. **性能优化**：合理的资源管理和执行流程，提高执行效率

6. **兼容性**：确保与现有系统的无缝集成

## 实现步骤

1. 创建 `ai_scheduler.py` 文件，实现调度器核心功能

2. 修改 `api.py`，添加调度AI的API接口

3. 编写测试代码，验证调度AI的功能

4. 集成到现有系统中，确保与现有功能的兼容性

5. 优化和完善系统，提高性能和稳定性

## 可扩展性示例

### 添加新生成函数的示例

如果未来添加了新的生成函数，例如 `generate_company_product()`，只需：

1. 在相应的模块中定义新生成函数
2. 在调度器配置中注册该函数
3. 调度器会自动识别并使用该函数

### 执行序列示例（包含新生成函数）

```json
{
  "steps": [
    {
      "id": "step_1",
      "type": "company_product",
      "params": {
        "product_name": "新服务器型号",
        "category_id": 1
      }
    },
    {
      "id": "step_2",
      "type": "post",
      "params": {
        "board_id": 1,
        "title": "新服务器型号发布",
        "use_resources": ["step_1"]
      }
    }
  ]
}
```

调度器会
