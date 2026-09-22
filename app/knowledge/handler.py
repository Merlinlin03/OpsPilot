from typing import Dict, Any

from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent, KNOWLEDGE_INTENTS
from app.knowledge.provider import KnowledgeChunk
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder
from app.domain.messages import BotMessage


class KnowLedgeHandler:

    def __init__(self,
            knowledge_intents:Dict[str,KnowledgeIntent],
            provider_registry:KnowledgeProviderRegistry,
            knowledge_responder:KnowledgeResponder):
        self.knowledge_intents=knowledge_intents
        self.provider_registry=provider_registry
        self.knowledge_responder=knowledge_responder

    async def handle(self,state:DialogueState,
      knowledge_intents:list[str])->list[BotMessage]:
        # 根据 LLM 识别出的 OpsPilot 知识意图选择本地 mock provider。
        provier_ids:list[str] = self._get_provider_ids(knowledge_intents)

        final_result:list[KnowledgeChunk] = []
        for provier_id in provier_ids:
            provider_obj = self.provider_registry.get(provier_id)
            result = await provider_obj.retrieve(state)
            final_result.extend(result)

        response = await self.knowledge_responder.respond(
            user_message=state.pending_turn.user_message,
            recent_turns=state.current_session().turns[-5:],
            chunks=final_result)
        return response

    def _get_provider_ids(self,
                knowledge_intents:list[str])->list[str]:
        final_provider_ids:list[str] = []
        for intent in knowledge_intents:
            final_provider_ids.extend(
                KNOWLEDGE_INTENTS[intent].provider_ids)
        # (去重处理)
        return list(set(final_provider_ids))
