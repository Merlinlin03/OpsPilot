# OpsPilot

OpsPilot 是面向海外 App 最终用户的智能客服应用，提供中文 Web 聊天页面、订阅支持、应用故障排查和广告体验反馈。

后端基于 FastAPI、Flow YAML 状态机、LLM TurnPlanner 和 Action 执行器。模型负责理解和生成，流程模板负责必要信息收集；业务资料与工单动作目前为本地模拟。

## 安装与部署

需要 Python 3.12+、MySQL 和 OpenAI 兼容的模型接口。参考 `.env.example` 配置环境变量，不要提交真实密钥。默认示例模型为 `qwen-plus`。

```sh
pip install -r requirements.txt
python -m app.init_db
python main.py
```

数据库需预先创建。容器部署、外网访问与数据持久化说明见 [部署文档](docs/deployment.md)。

## 核心能力

- 订阅支持：处理 charged but Premium not activated、误扣费、取消订阅后仍扣费等问题。
- 崩溃/版本支持：收集 App 版本、设备型号、系统版本和复现信息，生成技术支持工单。
- 广告体验投诉升级：识别 too many ads、误触广告、1 星差评等反馈，生成运营待办。
- 知识问答：基于本地 mock SOP 生成 evidence、missing fields、route team 和 reply draft。
- 用户回复：默认中文直接回应用户，不展示内部路由字段或回复草稿。

## 后端接口

保留原接口：

```http
POST /api/chat
```

请求示例：

```json
{
  "sender_id": "demo-user-001",
  "text": "用户说 charged but Premium not activated，想处理订阅问题"
}
```

对象消息也保留，后端已支持这些 OpsPilot 对象类型：

- `payment` / `subscription_order` -> `payment_order_id`
- `app_version` -> `app_version`
- `feedback` -> `feedback_id`

## Demo Flows

1. `subscription_support`
   - 收集 `subscription_issue_type` 和 `payment_order_id`
   - 本地 mock 生成 `support_ticket_id`、`route_team`、`issue_summary`、`reply_draft`

2. `crash_issue_support`
   - 收集 `app_version` 和 `device_model`
   - 生成技术支持工单和英文回复草稿

3. `ad_experience_escalation`
   - 收集 `feedback_id` 和 `country`
   - 生成广告体验运营待办和用户回复草稿

## Mock Integration Boundary

当前没有接入真实外部服务，所有业务知识来自本地 mock provider：

- `AppProfileProvider`
- `SubscriptionProvider`
- `FeedbackProvider`
- `AdExperienceProvider`
- `KnowledgeBaseProvider`

后续可以替换为真实 adapter：

- `KnowledgeAdapter` -> Global Knowledge Hub
- `MetricsAdapter` -> InsightQuery
- `FeedbackClassifierAdapter` -> RouteMind
- `TicketRoutingAdapter` -> VoiceFlow Agent
- `AdInsightAdapter` -> AdInsight Agent

## 本地启动

```bash
uvicorn app.api.app:app --host 0.0.0.0 --port 18082
```

实际 LLM、数据库和端口配置仍读取项目根目录 `.env`。

## 前端 Demo

已新增无依赖静态前端：

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`

启动后端后访问：

```text
http://127.0.0.1:18082/
```

前端默认调用：

```text
POST http://127.0.0.1:18082/api/chat
```
