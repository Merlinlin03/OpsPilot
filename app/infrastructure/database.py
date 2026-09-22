import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.config import settings

# 定义变量
engine : AsyncEngine | None = None
async_session : async_sessionmaker[AsyncSession]

# 初始化的方法
def init_engine():
    global engine, async_session
    # 创建异步引擎对象
    engine = create_async_engine(
        settings.database_url,
        echo=False
    )
    # 创建会话对象
    async_session = async_sessionmaker(engine,
                                       expire_on_commit=False)

# 关闭方法
async def close_engine():
    await engine.dispose()

# 测试方法
async def main():
    init_engine()
    async with async_session() as session:
        result = await session.execute(text("select 1"))
        print(result.fetchone())
    await close_engine()

if __name__ == '__main__':
    asyncio.run(main())
