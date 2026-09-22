
"""
    DialogueStateRepository操作数据库层
    # 操作数据库和会话AsyncSession注入进来

    # orm ：如果简单curd操作不需要写sql语句，调用sqlalchemy方法实现
    #       如果有复杂需求，编写sql语句，比如多表查询，分组等
    # load_state方法：根据sender_id查询数据
    # save_state方法：保存数据（如果sender_id不存在添加，如果存在更新）
"""
import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.state import DialogueState
from app.repository.dialogue_state import DialogueStateRecord


class DialogueStateRepository:

    # # 操作数据库和会话AsyncSession注入进来
    def __init__(self, session: AsyncSession):
        self.session = session

    # 根据sender_id查询数据
    async def load_state(self, sender_id:str)->DialogueState:
        # sqlalchemy方法构建sql语句
        # SELECT * FROM dialogue_states WHERE sender_id=?
        # sql1 = "SELECT * FROM dialogue_states WHERE sender_id=:sid"
        # result1 = await self.session.execute(sql1,{'sid':sender_id})

        sql = select(DialogueStateRecord).where(
                 DialogueStateRecord.sender_id == sender_id)

        # 调用session方法执行sql语句
        result = await self.session.execute(sql)

        # 从result获取数据
        # 获取一条记录 如果获取不到空
        state = result.scalar_one_or_none()

        # 封装DialogueState对象数据
        if state:
            dialogue_state:DialogueState = DialogueState.from_dict(
                 json.loads(state.state_json))
            return dialogue_state
        else:
            return DialogueState(sender_id=sender_id)

    # 添加方法
    async def save_state(self, state:DialogueState):

        # 构建sql语句
        # INSERT INTO dialogue_states(sender_id,state_json) VALUES('1','{....}')
        state_json = json.dumps(state.to_dict(),ensure_ascii=False)
        insert_sql = insert(DialogueStateRecord).values(
            sender_id=state.sender_id,
            state_json=state_json
        )

        # 需求：如果sender_id不存在添加，如果存在更新
        # 实现方式一：
        # 1 根据sender_id查询数据库，得到结果
        # 2 对查询结果判断，如果不存在结果，添加
        # 3              如果结果存在，更新 （构建更新sql语句）

        # 实现方式二：
        # 使用sqlalchemy封装方式实现
        upsert_stmt = insert_sql.on_duplicate_key_update(
            state_json=insert_sql.inserted.state_json
        )

        # 执行sql语句
        await self.session.execute(upsert_stmt)
        # session提交
        await self.session.commit()
