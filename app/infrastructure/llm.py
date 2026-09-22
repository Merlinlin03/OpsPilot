# 创建llm对象
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from app.config.config import settings

# 创建llm对象
llm:BaseChatModel = init_chat_model(
    model=settings.LLM_MODEL,
    model_provider="openai",
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    temperature=0,
)

if __name__ == '__main__':
    print(llm.invoke("hello").content)