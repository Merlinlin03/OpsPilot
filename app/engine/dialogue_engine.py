import time
from typing import List

from sqlalchemy.util import await_only

from app.chitchat.handler import ChitChatHandler
from app.clarify.responder import ClarifyResponder
from app.domain.messages import ProcessResult, BotMessage, UserMessage, MessageType
from app.domain.state import DialogueState, Session
from app.knowledge.handler import KnowLedgeHandler
from app.plan.turn_plan import TurnPlan, ClarifyReason
from app.plan.turn_planner import TurnPlanner
from app.plan.validator import TurnPlanValidator
from app.task.command.models import Command, SetSlotsCommand
from app.task.flow.models import FlowsList
from app.task.flow.steps import CollectSlotStep
from app.task.handler import TaskHandler


# 消息处理引擎
class DialogueEngine:

    def __init__(self,
                 turn_planner:TurnPlanner,
                 turn_plan_validator:TurnPlanValidator,
                 task_handler:TaskHandler,
                 clarify_responder:ClarifyResponder,
                 chitchat_handler:ChitChatHandler,
                 knowledge_handler:KnowLedgeHandler):
        self.turn_planner = turn_planner
        self.turn_plan_validator = turn_plan_validator
        self.task_handler = task_handler
        self.clarify_responder = clarify_responder
        self.chitchat_handler = chitchat_handler
        self.knowledge_handler = knowledge_handler

    # 负责处理一条消息：提出一个问题-到回复过程
    async def process_message(self,
            state: DialogueState,
            user_message:UserMessage) -> ProcessResult:
        # 1 准备session
        self._prepare_session(state)

        # 2 准备turn
        self._begin_turn(state, user_message)

        # 3 判断用户消息类型
        # 用户消息在 user_message里面，user_message有字段type，代表消息类型
        #  3.1 如果文本消息
        if user_message.type is MessageType.TEXT:
            msg = await self._handle_text_msg(state,
                                self.task_handler.flow_list,
                                user_message)
        # 3.2 如果对象消息
        else:
            msg = await self.handle_object_msg(state,
                             user_message,
                             self.task_handler.flow_list)

        # 4 提交本轮记录
        state.pending_turn.bot_messages.extend(msg)
        state.commit_turn()

        # 5 返回
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=msg,
        )

    # 准备session
    def _prepare_session(self,state:DialogueState):
        # 1 获取当前session，判断是否存在
        current_session:Session = state.current_session()
        # 2 如果不存在，创建新的
        if current_session is None:
            # 创建新的
            state.start_session()
            return
        # 3 如果存在 -- session过期 创建新的，没有过期使用当前session
        # 判断session是否过期 约定规则：60分钟
        now = time.time() # 秒
        # 如果最后活跃时间大于60分钟，过期了
        if now - current_session.last_activity_at > 60*60:
            # 手动过期，不会自动60分钟过期
            state.close_session()
            state.reset_running_state_for_new_session()
            # 创建新的
            state.start_session()
        else:
            # 更新最后一次活跃时间
            current_session.last_activity_at = now
        return

    # 2 准备turn
    def _begin_turn(self,state:DialogueState,user_message:UserMessage):
        state.begin_turn(user_message)

    # 3 处理文本类型消息
    async def _handle_text_msg(self,state:DialogueState,
                              flows:FlowsList,
                              user_message:UserMessage) :
        # 1 调用TurnPlanner方法意图识别
        ## 构建提示词，调用LLM，得到执行哪条轨道 （任务流程、知识查询、闲聊）
        # 返回结果TrunPlan对象
        turn_plan:TurnPlan = await self.turn_planner.predict(state,flows)

        # 2 调用TurnPlanValidator校验
        ## 返回bool
        validated = self.turn_plan_validator.validate(state,turn_plan,flows)

        # 3 如果校验通过，调用对应处理器执行消息处理
        if not validated.valid:
            return await self.clarify_responder.respond(state,validated.reason)

        # todo 处理器包含： 任务流程、知识查询、闲聊、反问澄清
        if turn_plan.task is not None:
            result = await self.task_handler.handle(state,commands=turn_plan.task.commands)

        if turn_plan.knowledge is not None:
            result = await self.knowledge_handler.handle(
                state, turn_plan.knowledge.intents)
        if turn_plan.chitchat is not None:
            # 闲聊hanler
            result = await self.chitchat_handler.handle(state)
        return result

    # 处理对象类型消息
    async def handle_object_msg(self,state:DialogueState,
                                user_message:UserMessage,
                    flows:FlowsList) ->List[BotMessage] :
        # 1 把对象类型消息，构建成commond类型 SetSlotsCommand
        commands =self._build_slotcommond_object(user_message,state,flows)

        # 2 如果 command，调用TaskHandler方法
        if commands:
            return await self.task_handler.handle(state,commands=commands)

        # 3. 业务流程存在
        if state.active_task is not None:
            return await self.task_handler.handle(state, commands=[])

        return await self.clarify_responder.respond(
            state,reason=ClarifyReason.OBJECT_REQUIRES_INTENT)


    def _build_slotcommond_object(self,user_message:UserMessage,
                state:DialogueState,flows:FlowsList) -> List[Command] :
        # 判断user_message存在对象类型消息
        user_obj = user_message.object
        if user_obj is None:
            return []

        object_type = user_obj.type
        object_slot_map = {
            "payment": "payment_order_id",
            "subscription_order": "payment_order_id",
            "app_version": "app_version",
            "feedback": "feedback_id",
        }
        slot_name = object_slot_map.get(object_type)
        if slot_name and self._is_setslot_data(state, flows, slot_name):
            return [SetSlotsCommand(command="set_slots", slots={slot_name: user_obj.id})]
        return []

    def _is_setslot_data(self,
            state:DialogueState, flows:FlowsList, slot_name:str)->bool:
        # 当前运行任务，
        active_task = state.active_task
        if active_task is None:
            return False

        # 获取运行任务流程id
        flow_id = active_task.flow_id
        # 根据流程id获取flow对象
        flow = flows.get_flow_by_id(flow_id)
        if flow is None:
            return False

        # 4. 判断该流程中的上下文当前槽位是否已经填过
        if active_task.slots.get(slot_name):
            return False

        for step in flow.steps:
            if (isinstance(step,CollectSlotStep)
                    and step.slot_name == slot_name):
                return True
        return False
