from typing import Any

from app.domain.state import DialogueState
from app.task.action.base import Action, ActionResult


class SubscriptionContextAction(Action):
    name = "action_lookup_subscription_context"

    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        slots = state.active_task.slots
        issue_type = slots.get("subscription_issue_type", "subscription issue")
        payment_order_id = slots.get("payment_order_id", "missing payment_order_id")

        return ActionResult(
            slot_updates={
                "support_ticket_id": _ticket_id("BILL", payment_order_id),
                "route_team": "Billing Support",
                "issue_summary": (
                    f"{issue_type}; payment_order_id={payment_order_id}; "
                    "needs platform receipt verification before refund or entitlement decision."
                ),
                "reply_draft": (
                    "抱歉给你带来不便。We will verify your purchase record first. "
                    f"Please confirm the order ID {payment_order_id} and the purchase platform "
                    "(App Store / Google Play / Stripe). If Premium was charged but not activated, "
                    "we will route it to Billing Support for entitlement recovery or refund guidance."
                ),
            }
        )


class TechnicalTicketAction(Action):
    name = "action_create_technical_ticket"

    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        slots = state.active_task.slots
        app_version = slots.get("app_version", "missing app_version")
        device_model = slots.get("device_model", "missing device_model")

        return ActionResult(
            slot_updates={
                "support_ticket_id": _ticket_id("TECH", app_version),
                "route_team": "Technical Support",
                "issue_summary": (
                    f"Crash or freeze reported on app_version={app_version}, "
                    f"device_model={device_model}; compare with recent release feedback cluster."
                ),
                "reply_draft": (
                    "感谢反馈，我们会优先排查该版本问题。Thanks for reporting this issue. "
                    f"We have recorded your app version ({app_version}) and device ({device_model}). "
                    "If possible, please also share the steps before the crash and a screenshot or screen recording."
                ),
            }
        )


class AdReviewTodoAction(Action):
    name = "action_create_ad_review_todo"

    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        slots = state.active_task.slots
        feedback_id = slots.get("feedback_id", "raw feedback")
        country = slots.get("country", "unknown market")

        return ActionResult(
            slot_updates={
                "operation_todo_id": _ticket_id("ADS", feedback_id),
                "route_team": "Ad Experience Ops",
                "issue_summary": (
                    f"Negative ad-experience feedback from {country}; feedback_id={feedback_id}; "
                    "review ad frequency, interstitial timing, and accidental-click risk."
                ),
                "reply_draft": (
                    "抱歉广告体验影响了你的使用。We are sorry the ad experience felt disruptive. "
                    "Your feedback has been shared with our product and monetization team. "
                    "We will review ad frequency and placement for your market."
                ),
            }
        )


def _ticket_id(prefix: str, seed: str) -> str:
    cleaned = "".join(ch for ch in str(seed).upper() if ch.isalnum())
    suffix = cleaned[-6:] if cleaned else "MOCK01"
    return f"OP-{prefix}-{suffix}"
