from app.domain.messages import UserMessage, ProcessResult
from app.domain.state import DialogueState
from app.engine.dialogue_engine import DialogueEngine
from app.repository.dialogue_state_repository import DialogueStateRepository

"""
    业务逻辑层，具体调用实现业务
    service调用repository和engine，这两个对象注入到service里面
"""
class DialogueService:
    # 初始化注入
    def __init__(self,
                 dialogue_state_repository:DialogueStateRepository,
                 dialogue_engine:DialogueEngine):
        self.dialogue_state_repository = dialogue_state_repository
        self.dialogue_engine = dialogue_engine

    # 具体业务
    async def process_message(self,
                    user_message:UserMessage)->ProcessResult:
        # 1 根据UserMessage对象里面sender_id查询历史会话信息
        state:DialogueState = await self.dialogue_state_repository.load_state(
                                            user_message.sender_id)

        #### ############核心部分################
        # 2 根据历史会话信息 + 当前消息UserMessage，
        #  调用dialogue_engine方法，进行这一条消息处理
        process_result:ProcessResult = await (
            self.dialogue_engine.process_message(
                                              state, user_message))

        # 3 dialogue_engine处理这条信息之后，返回处理完整结果信息
        # 把返回处理完整结果信息存储数据库里面
        await self.dialogue_state_repository.save_state(state)
        return process_result