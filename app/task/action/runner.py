from dataclasses import dataclass, field
from typing import Any

from app.domain.state import DialogueState
from app.task.action.base import Action, ActionResult
from app.task.action.register import ActionRegistry


@dataclass
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)

# 入口
class ActionRunner:
    def __init__(self,actionRegistry:ActionRegistry):
        self.actionRegistry = actionRegistry

    # 入口方法
    async def run(self,action_all:ActionCall,
                  state:DialogueState)->ActionResult:
        # action_all得到action‘名称
        action_name = action_all.action_name
        # 根据action_name到注册中心获取对应action对象
        action_obj = self.actionRegistry.getAction(action_name)
        # 调用action对象的方法实现
        return await action_obj.run(state=state,
                       action_kwargs=action_all.action_kwargs)