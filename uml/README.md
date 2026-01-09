# 二手交易平台 UML 顺序图说明

本目录包含二手交易平台的 PlantUML 格式顺序图，描述了系统的主要交互流程。

## 图表列表

### 01-用户聊天消息流程.puml
描述用户之间的基本聊天消息交互流程：
- 用户加入聊天室
- 获取历史消息
- 发送和接收实时消息
- WebSocket 通信机制

### 02-买家发起议价流程.puml
描述买家如何发起议价的完整流程：
- 浏览商品详情
- 点击砍价按钮
- 输入期望价格
- 发送议价消息到卖家
- 消息通过 Socket.IO 实时推送

### 03-卖家AI智能回复流程.puml
描述卖家使用 AI 智能助手回复买家议价的流程：
- 卖家点击智能回复按钮
- 调用 Agent Service 获取 AI 建议
- SellerAgent 分析议价场景
- 返回建议动作（接受/还价/拒绝）
- 卖家可调整价格和话术
- 采纳建议并发送消息

### 04-买家再次还价流程.puml
描述买家收到卖家还价后继续还价的流程：
- 买家收到卖家还价消息
- 点击"我要还价"按钮
- 输入新的出价
- 发送还价消息
- 创建新的议价记录

### 05-卖家处理议价流程.puml
描述卖家处理买家议价的三种方式：
- 直接同意：更新商品价格，修改议价状态
- 直接拒绝：更新议价状态为已拒绝
- 使用 AI 智能回复：详见图 03

### 06-买家下单支付流程.puml
描述买家下单和支付的完整流程：
- 查看商品详情
- 点击立即购买
- 确认订单信息
- 提交订单
- 模拟支付
- 更新订单状态和商品状态

### 07-系统整体架构图.puml
系统的整体架构视图：
- 前端组件（Vue3 + Vant）
- 后端服务（Flask REST API）
- WebSocket 实时通信
- AI 智能体服务（Agent Service）
- MySQL 数据库
- 各层之间的交互关系

## 如何查看

### 在线查看
将 `.puml` 文件内容复制到以下在线工具：
- [PlantUML 官方在线编辑器](http://www.plantuml.com/plantuml/uml/)
- [PlantText](https://www.planttext.com/)

### VS Code 查看
安装 PlantUML 扩展：
1. 安装 `PlantUML` 插件
2. 安装 Java（PlantUML 需要）
3. 安装 Graphviz（用于渲染）
4. 右键点击 `.puml` 文件，选择 `Preview Current Diagram`

### 导出图片
使用 PlantUML 命令行工具：
```bash
# 安装 PlantUML
# 导出为 PNG
java -jar plantuml.jar *.puml

# 导出为 SVG
java -jar plantuml.jar -tsvg *.puml
```

## 技术栈说明

### 前端
- Vue 3 + Vite
- Vant UI 组件库
- Socket.IO Client（实时通信）
- Axios（HTTP 请求）

### 后端
- Flask（Python Web 框架）
- Flask-SocketIO（WebSocket 支持）
- SQLAlchemy（ORM）
- MySQL（数据库）

### AI 智能体
- 独立的 Flask 服务（端口 5011）
- SellerAgent 和 BuyerAgent
- 基于规则的议价策略
- 市场数据分析

## 关键交互说明

### 实时通信
- 使用 Socket.IO 实现 WebSocket 通信
- 用户加入时触发 `join` 事件
- 发送消息时触发 `send_msg` 事件
- 接收消息时监听 `new_msg` 事件

### 议价机制
- 买家发起议价创建 `BargainLog` 记录
- 卖家可以：接受、拒绝、还价
- 支持多轮议价
- 集成 AI 智能建议

### AI 决策
- SellerAgent 根据多个因素决策：
  - 买家出价
  - 卖家底价
  - 市场均价
  - 买家信用评分
  - 商品成色和类别
- 返回建议动作和理由
- 卖家可自定义调整

## 开发指南

如需修改流程，请：
1. 更新对应的 `.puml` 文件
2. 检查前后端代码是否需要同步修改
3. 更新本 README 说明文档
4. 重新生成图片（如果有需要）

## 联系方式

如有问题或建议，请联系开发团队。
