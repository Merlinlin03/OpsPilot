from dataclasses import asdict
from typing import List

from app.domain.contexts import CollectSystemContext
from app.domain.messages import BotMessage
from app.domain.state import DialogueState

from app.task.action.base import ActionResult
from app.task.action.runner import ActionRunner, ActionCall
from app.task.command.models import Command
from app.task.flow.links import StaticLink, ConditionalLink, FallbackLink
from app.task.flow.models import FlowsList
from app.task.flow.steps import FlowStep, StartFlowStep, CollectSlotStep, EndFlowStep, ActionFlowStep


# 推进流程里面步骤实现
class FlowExecutor:

    async def run_task(self, state:DialogueState,
                       commands:List[Command],
                       flow_list:FlowsList,
                       action_runner:ActionRunner)->List[BotMessage]:
        # 定义变量 封装最终数据
        final_messages:List[BotMessage] = []
        # 外层循环: 处理步骤的action调用过程
        while True:
            # 在步骤执行过程中，遇到step是action类型，
            # 封装ActionCall对象，返回外循环，执行action
            action_call:ActionCall = self.advance_until_action(state,flow_list)
            # 特殊类型action
            if action_call.action_name=="action_listen":
                break
            else:
                action_result:ActionResult = await action_runner.run(action_call,state)
                state.set_slots(action_result.slot_updates)
                final_messages.extend(action_result.messages)
        return final_messages

    # 推进 步骤实现
    def advance_until_action(self,state:DialogueState,
                             flow_list:FlowsList)->ActionCall:
        # 内层循环  步骤推进过程
        while True:
            # 1 获取当前运行任务
            current_active_task = state.current_active_task()
            # 2 判断 current_active_task 为空
            if current_active_task is None:
                return ActionCall(action_name="action_listen")

            # current_active_task 不为空
            # 获取流程里面步骤id
            flow_id = current_active_task.flow_id
            flow = flow_list.get_flow_by_id(flow_id)
            step = flow.get_step_by_id(current_active_task.step_id)

            # 开始推进
            action_call:ActionCall = self._run_step(state,step,flow_list)
            if action_call is not None:
                return action_call

    # 开始推进
    def _run_step(self,state:DialogueState,
                  step:FlowStep,
                  flow_list:FlowsList)->ActionCall:
        # 因为step步骤类型不同的，每个类型步骤做的事情不同的
        if isinstance(step,StartFlowStep):
            return self._run_start_step(state,step)
        if isinstance(step,CollectSlotStep):
            return self._run_collect_step(state,step,flow_list)
        if isinstance(step,EndFlowStep):
            return self._run_end_step(state)
        if isinstance(step,ActionFlowStep):
            return self._run_action_step(state,step)

    # 1 step类型start步骤推进
    def _run_start_step(self,state:DialogueState,step:FlowStep)->None:
        self._advance_next_step(state,step)
        return None

    def _advance_next_step(self,state:DialogueState,step:FlowStep)->None:
        # 获取当前步骤的next值，把设置当前执行步骤id
        # 获取当前步骤的next值
        next_step_id = self._select_next_step(state,step)
        # 把设置当前执行步骤id
        state.current_active_task().step_id = next_step_id

    def _select_next_step(self,state:DialogueState,step:FlowStep)->str:
        for link in step.next:
            # 如果next值字符串，表示无条件跳转
            if isinstance(link,StaticLink):
                return link.target

            if isinstance(link,ConditionalLink):
                # 条件判断，如果成立
                if self._select_condition(state,link.condition):
                    return link.target
            if isinstance(link,FallbackLink):
                return link.target
        return "next not exist"

    def _select_condition(self,state:DialogueState,codition:str)->bool:
        data = {
            "slots":state.active_task.slots,
            "context":asdict(state.current_active_task())
        }
        return bool(eval(codition,{},data))

    # 2 step类型 end  结束
    def _run_end_step(self,state:DialogueState)->None:
        if state.active_system_task:
            state.end_system_task()
        else:
            state.end_active_task()
        return None

    # 3 step类型action
    def _run_action_step(self,
                         state:DialogueState,
                         step:FlowStep)->ActionCall:
        # 步骤推进
        self._advance_next_step(state,step)
        # 内层步骤类型action时候，封装ActionCall，包含action名称和参数，返回ActionCall
        # 在外层循环得到返回ActionCall，根据名称得到action对象，调用
        return self._build_action_call(state,step)


    def _build_action_call(self,state:DialogueState,step:ActionFlowStep)->ActionCall:
        action_name = step.action
        action_args = step.args
        if isinstance(action_args, str):
            action_args = asdict(state.active_system_task)[action_args.split('.')[1]]
        return ActionCall(action_name=action_name,action_kwargs=action_args)

    # 4 step类型 collect
    def _run_collect_step(self,state:DialogueState,
                          step:CollectSlotStep,
                          flow_list:FlowsList):
        # 1 如果消息是对象类型，从对象类型获取槽位数据，设置到state里面
        self._fill_to_slots_data(state,step)
        # 2 如果槽位数据存在
        if state.active_task.slots.get(step.slot_name):
            # 2.1 进一步判断，是否有validation属性
            if step.validation:
                ## 2.1.1如果有validation，判断条件是否成立，如果成立
                if self._select_condition(step.validation.condition,state):
                    ### 推进next步骤
                    self._advance_next_step(state,step)
                    return None
                else: # 条件不成立，返回信息
                    if step.validation.failure_response:
                        return ActionCall(
                            action_name="action_response",
                            action_kwargs=asdict(step.validation.failure_response))
                    else:
                        return ActionCall(
                            action_name="action_response",
                            action_kwargs={
                                "mode":"static",
                                "text":"必填信息不能为空"
                            })
            else: # 没有validation属性
                # 直接推进
                self._advance_next_step(state,step)
                return None

        # 3 没有槽位数据
        else:
            ## 开启系统流程
            state.start_system_task(CollectSystemContext(
                flow_id="system_collect_information",
                step_id=
                flow_list.get_flow_by_id("system_collect_information").start_step().id,

                slot_name=step.slot_name,
                response=asdict(step.response),
            ))

    def _fill_to_slots_data(self,state:DialogueState,step:CollectSlotStep)->None:
        if state.focused_object is None:
            return None

        # 兼容前端对象消息：后续前端可传 app、feedback、payment 等业务对象。
        if (step.slot_name=="order_number"
                and state.focused_object.type=="order"):
            state.set_slots({step.slot_name:state.focused_object.id})

        if (step.slot_name=="product_id"
                and state.focused_object.type=="product"):
            state.set_slots({step.slot_name:state.focused_object.id})

        if (step.slot_name=="payment_order_id"
                and state.focused_object.type in ("payment", "subscription_order")):
            state.set_slots({step.slot_name: state.focused_object.id})

        if (step.slot_name=="app_version"
                and state.focused_object.type == "app_version"):
            state.set_slots({step.slot_name: state.focused_object.id})

        if (step.slot_name=="feedback_id"
                and state.focused_object.type == "feedback"):
            state.set_slots({step.slot_name: state.focused_object.id})

if __name__ == "__main__":
    # next:
    # - if: "slots.get('feedback_id')"  # 有反馈编号就创建运营待办
    #     then: respond
    # - else: missing_product_context
    conditon = "slots.get('product_id')=='abc'"

    # 数据
    data = {
        "slots":{
            "product_id":"wwww",
        }
    }

    flag = bool(eval(conditon,{},data))
    print(flag)


