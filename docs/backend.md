# OpsPilot Backend Notes

## 改造范围

本次只改后端内容，不包含前端页面。

保留内容：

- FastAPI 应用入口
- `/api/chat` 接口协议
- DialogueState / Turn / Message 状态结构
- Flow YAML 驱动的任务流程
- LangChain PromptTemplate 调用方式

替换内容：

- 原电商订单、物流、商品、退款流程替换为海外 App 支持流程。
- Knowledge intent 替换为订阅政策、版本反馈、广告体验、回复 SOP、人工升级。
- Provider 从外部中台调用改为本地 mock。
- Prompt 角色从电商客服改为 OpsPilot 出海 App 支持与运营协同助手。

## 成功标准

- 用户提出订阅/Premium 问题时能进入 `subscription_support`。
- 用户提出 crash/freeze/slow/update issue 时能进入 `crash_issue_support`。
- 用户提出 too many ads/广告太多/差评时能进入 `ad_experience_escalation`。
- 知识问答能调用本地 mock provider，而不是停在 `pass`。
- 用户可看到中英混合 reply draft、负责团队和后续处理建议。

## 示例问题

- `用户说 charged but Premium not activated，需要处理订阅问题`
- `The app crashes after update, version iOS 3.8.2`
- `US 用户评论 too many ads and unusable，评分 1 星`
- `订阅退款 SOP 是什么？需要哪些字段？`

## 当前限制

- 工单号和运营待办号由本地 action mock 生成。
- 版本反馈、广告体验聚类和订阅政策均为合成 demo 数据。
- 没有真实连接 App Store、Google Play、CRM、工单系统或数据指标平台。
- `atuguigu/__init__.py` 是兼容层：原课程代码使用 `atuguigu.*` import，当前源码仍放在 `app/` 目录下。
