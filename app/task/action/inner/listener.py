from typing import Any

from app.domain.state import DialogueState
from app.task.action.base import Action, ActionResult

# action_listen
class ActionListen(Action):
    name="action_listen"

    async def run(self, state: DialogueState,
            action_kwargs: dict[str, Any]) -> ActionResult:
        pass
