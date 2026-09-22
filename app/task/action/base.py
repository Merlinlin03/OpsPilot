# Action基类
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.domain.messages import BotMessage
from app.domain.state import DialogueState

@dataclass
class ActionResult:
    messages: list[BotMessage] = field(default_factory=list)
    slot_updates: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    name: str

    @abstractmethod
    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        pass


