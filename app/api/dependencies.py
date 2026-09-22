
"""
    web层 获取service对象

    service层 获取 repository和engine对象
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.engine.builder import build_dialogue_engine
from app.engine.dialogue_engine import DialogueEngine
from app.infrastructure import database
from app.repository.dialogue_state_repository import DialogueStateRepository
from app.service.dialogue_service import DialogueService

def init_dialogue_engine():
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()

# 创建DialogueEngine对象方法
async def get_dialogue_engine():
    return _dialogue_engine


# 获取操作数据库会话对象
async def get_session():
    async with database.async_session() as session:
        # yield
        yield session

# 获取DialogueStateRepository对象
# 注入session会话对象
async def get_dialogue_state_repository(
        session:AsyncSession=Depends(get_session)):
    return DialogueStateRepository(session)

# 获取DialogueService对象
# 注入DialogueStateRepository，操作mysql数据库
# 注入DialogueEngine，调用llm
async def get_dialogue_service(
    dialogue_state_repository:DialogueStateRepository=Depends(get_dialogue_state_repository),
    dialogue_engine:DialogueEngine=Depends(get_dialogue_engine)
) -> DialogueService:
    return DialogueService(
        dialogue_state_repository=dialogue_state_repository,
        dialogue_engine=dialogue_engine
    )

