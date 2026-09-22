from typing import List

from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.task.action.runner import ActionRunner
from app.task.command.models import Command
from app.task.command.process import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.models import FlowsList


# 任务流程处理器
class TaskHandler:
    def __init__(self,
                 flow_list:FlowsList,
                 processor:CommandProcessor,
                 flow_executor:FlowExecutor,
                 action_runner:ActionRunner):
        self.flow_list = flow_list
        self.processor = processor
        self.flow_executor = flow_executor
        self.action_runner = action_runner

    async def handle(self,
                     state:DialogueState,
                     commands:List[Command])->List[BotMessage]:
        # 1 CommandProcessor把意图识别返回Command处理，把相关对应数据更新到state里面
        self.processor.run(state=state,
                           commands=commands,
                           flows=self.flow_list)
        # 2 FlowExecutor根据state更新数据，推进业务流程实现
        # 根据前一步流程id，找到流程具体steps，执行多个step
        # 执行step时候，遇到类型action类型，调用ActionRunner方法执行action（远程调用）
        message = await self.flow_executor.run_task(state=state,
                                   commands=commands,
                                   flow_list=self.flow_list,
                                   action_runner=self.action_runner)
        # 3 把第二步处理结果返回
        return message
