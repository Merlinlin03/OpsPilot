from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from datetime import datetime

from app.domain.messages import BotMessage, UserMessage
from app.domain.state import DialogueState, Turn
from app.infrastructure.llm import llm
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt

# 闲聊
class ChitChatHandler:

    async def handle(self,
                     state: DialogueState)->list[BotMessage]:
        # 准备提示词需要数据
        user_message=state.pending_turn.user_message
        history=state.current_session().turns[-5:]
        # 构建提示词，调用llm
        return await self._call_llm(user_message,history)

    async def _call_llm(self,user_message: UserMessage,
                        turns: list[Turn])->list[BotMessage]:
        user_message_str = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(turns)

        # 加载提示词jinja2
        prompt_text = load_prompt("chitchat_respond")
        prompt_template = PromptTemplate.from_template(
                            template=prompt_text,
                                     template_format="jinja2")

        # 构建调用链
        chain = prompt_template | llm | StrOutputParser()
        response = await chain.ainvoke({
                "user_message": user_message_str,
                "history": history,
                "current_date": datetime.now().strftime("%Y-%m-%d %A"),
            })
        return [BotMessage(text=response)]
