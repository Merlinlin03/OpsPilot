from typing import Any

from app.domain.state import DialogueState
from app.task.action.base import Action, ActionResult
from app.task.action.customer.shared import get_logistics

# 旧版 action 保留为兼容 mock；新 OpsPilot flow 使用 ops_support.py。
class LogisticsAction(Action):
    name ="action_lookup_logistics"
    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        # 获取旧版兼容 id
        order_id = state.active_task.slots.get('order_number')
        # 判断
        if order_id is None:
            return ActionResult(
                slot_updates={
                    "logistics_company": "未知",
                    "tracking_number": "未知",
                    "logistics_status": "暂无兼容信息"
                }
            )

        # 调用
        logistics_data = await get_logistics(order_id)
        # 判断
        if logistics_data is None:
            return ActionResult(
                slot_updates={
                    "logistics_company": "未知",
                    "tracking_number": "未知",
                    "logistics_status": "暂无兼容信息"
                }
            )

        return ActionResult(
            slot_updates={
                "logistics_company": logistics_data.get("logistics_company"),
                "tracking_number": logistics_data.get("tracking_number") ,
                "logistics_status": logistics_data.get("status")
            }
        )

