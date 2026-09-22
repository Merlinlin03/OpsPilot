from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.infrastructure.llm import llm
from app.domain.messages import UserMessage, BotMessage
from app.domain.state import Turn
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import  load_prompt
from app.knowledge.provider import KnowledgeChunk

class KnowledgeResponder:

    async def respond(self,
                      user_message: UserMessage,
                      recent_turns: list[Turn],
                      chunks: list[KnowledgeChunk]
                      ) -> list[BotMessage]:
        # 准备提示词上下文
        user_message = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)
        knowledge_content = "\n\n".join([chunk.content for chunk in chunks])

        # 构造chain
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm | StrOutputParser()

        # 运行chain
        response = await chain.ainvoke({
            "user_message": user_message,
            "history": history,
            "knowledge_content": knowledge_content,
        })

        return [BotMessage(text=response)]
