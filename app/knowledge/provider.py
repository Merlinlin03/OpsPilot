import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.domain.state import DialogueState


@dataclass(slots=True)
class KnowledgeChunk:
    content: str


class KnowledgeProvider(ABC):
    provider_id = ""

    @abstractmethod
    async def retrieve(
            self,
            state: DialogueState,
    ) -> list[KnowledgeChunk]:
        pass


class AppProfileProvider(KnowledgeProvider):
    provider_id = "mock.app_profile"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        data: dict[str, Any] = {
            "app_name": "FocusFlow",
            "business": "海外效率类订阅 App",
            "markets": ["US", "DE", "BR", "ID"],
            "languages": ["en", "de", "pt-BR", "id"],
            "modules": ["premium_subscription", "habit_tracker", "focus_timer", "ad_monetization"],
            "subscription_entitlements": [
                "ad-free experience",
                "cloud sync",
                "advanced statistics",
                "custom focus plans",
            ],
        }
        if state.focused_object is not None:
            data["focused_object"] = state.focused_object.to_dict()
        return [_chunk("App profile mock data", data)]


class SubscriptionProvider(KnowledgeProvider):
    provider_id = "mock.subscription"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        data = {
            "required_fields": ["payment_order_id", "purchase_platform", "user_region"],
            "common_cases": [
                {
                    "intent": "premium_not_activated",
                    "evidence": "用户已扣费但 Premium 权益未生效",
                    "route_team": "Billing Support",
                    "first_reply": "Sorry for the trouble. Please send us your purchase order ID so we can verify the subscription status.",
                },
                {
                    "intent": "refund_request",
                    "evidence": "用户要求退款或认为被误扣费",
                    "route_team": "Billing Support",
                    "policy_note": "App Store / Google Play 订单需按平台退款流程处理，客服提供指引但不承诺立即退款。",
                },
            ],
            "escalation": "涉及重复扣费、未成年人付款、强烈投诉或 chargeback 风险时升级人工。",
        }
        return [_chunk("Subscription SOP mock data", data)]


class FeedbackProvider(KnowledgeProvider):
    provider_id = "mock.feedback"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        data = {
            "recent_release": "iOS 3.8.2 / Android 5.1.0",
            "signals": [
                {"market": "US", "version": "iOS 3.8.2", "issue": "crash on launch", "device": "iPhone 14", "count": 18},
                {"market": "DE", "version": "Android 5.1.0", "issue": "freeze after focus timer ends", "device": "Pixel 8", "count": 9},
            ],
            "required_fields": ["app_version", "device_model", "os_version", "repro_steps"],
            "route_team": "Technical Support",
            "suggested_reply": "Thanks for reporting this. Could you share your app version, device model, and what you were doing before the crash?",
        }
        return [_chunk("Version feedback mock data", data)]


class AdExperienceProvider(KnowledgeProvider):
    provider_id = "mock.ad_experience"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        data = {
            "risk_keywords": ["too many ads", "unusable", "annoying", "1 star", "广告太多", "误触"],
            "review_threshold": "评分 <= 2 星或包含退款/卸载威胁时创建运营待办",
            "route_team": "Ad Experience Ops",
            "todo_template": {
                "title": "Review ad frequency for negative feedback cluster",
                "owner": "monetization_ops",
                "evidence_fields": ["feedback_id", "country", "app_version", "rating"],
            },
            "suggested_reply": "We are sorry the ad experience felt disruptive. Your feedback has been shared with our product team for review.",
        }
        return [_chunk("Ad experience mock data", data)]


class KnowledgeBaseProvider(KnowledgeProvider):
    provider_id = "mock.knowledge_base"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        data = {
            "reply_principles": [
                "先共情，再说明需要核验的证据字段",
                "不要承诺超出平台政策的退款或补偿",
                "给出明确下一步和负责团队",
                "英文草稿保持简洁、礼貌、可直接发送",
            ],
            "handoff_rules": [
                "payment dispute or chargeback risk",
                "privacy or permission complaint",
                "high-risk negative review from key market",
                "crash affects latest release with multiple reports",
            ],
            "future_adapters": [
                "KnowledgeAdapter -> Global Knowledge Hub",
                "MetricsAdapter -> InsightQuery",
                "FeedbackClassifierAdapter -> RouteMind",
                "TicketRoutingAdapter -> VoiceFlow Agent",
                "AdInsightAdapter -> AdInsight Agent",
            ],
        }
        return [_chunk("OpsPilot SOP mock knowledge", data)]


def _chunk(title: str, data: dict[str, Any]) -> KnowledgeChunk:
    return KnowledgeChunk(
        content=f"{title}:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
    )
