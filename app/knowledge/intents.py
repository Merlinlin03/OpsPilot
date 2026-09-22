from dataclasses import dataclass, field


@dataclass
class KnowledgeIntent:
    id: str
    description: str
    provider_ids: list[str] = field(default_factory=list)
    requires_object: str | None = None


KNOWLEDGE_INTENTS: dict[str, KnowledgeIntent] = {
    "app_profile": KnowledgeIntent(
        id="app_profile",
        description="App 基础信息、功能模块、订阅权益和目标市场咨询",
        provider_ids=["mock.app_profile"],
        requires_object="app",
    ),
    "subscription_policy": KnowledgeIntent(
        id="subscription_policy",
        description="订阅扣费、退款、Premium 未生效和平台订单核验 SOP",
        provider_ids=["mock.subscription", "mock.knowledge_base"],
    ),
    "version_feedback": KnowledgeIntent(
        id="version_feedback",
        description="版本反馈、崩溃卡顿、设备兼容性和技术支持排查建议",
        provider_ids=["mock.feedback", "mock.knowledge_base"],
    ),
    "ad_experience_policy": KnowledgeIntent(
        id="ad_experience_policy",
        description="广告体验投诉、插屏频控、负面评论升级和运营跟进规则",
        provider_ids=["mock.ad_experience", "mock.knowledge_base"],
    ),
    "multilingual_reply_sop": KnowledgeIntent(
        id="multilingual_reply_sop",
        description="中英混合或多语言客服回复草稿、本地化表达和升级口径",
        provider_ids=["mock.knowledge_base"],
    ),
    "human_handoff_rule": KnowledgeIntent(
        id="human_handoff_rule",
        description="付款争议、隐私权限、高风险差评和人工升级标准",
        provider_ids=["mock.knowledge_base"],
    ),
}
