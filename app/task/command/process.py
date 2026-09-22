from app.domain.contexts import CanceledSystemContext, StartedSystemContext, ResumedSystemContext, \
    InterruptedSystemContext, TaskContext
from app.domain.state import DialogueState
from app.task.command.models import Command, StartFlowCommand, SetSlotsCommand, CancelFlowCommand, \
    ResumeFlowCommand
from app.task.flow.models import FlowsList


class CommandProcessor:
    def run(self,
        commands: list[Command],
        state: DialogueState,
        flows: FlowsList,
    ) -> None:
        for command in commands:
            self._apply(command, state=state, flows_list=flows)

    def _apply(self, command: Command, *,
               state: DialogueState,
               flows_list: FlowsList):
        # command类型判断
        if isinstance(command, StartFlowCommand):
            self._handle_start_flow(state,command,flows_list)

        elif isinstance(command, SetSlotsCommand):
            self._handle_set_slots(state,command)

        elif isinstance(command, CancelFlowCommand):
            self._handle_cancel_flow(state, flows_list)

        elif isinstance(command, ResumeFlowCommand):
            self._handle_resume_task(command=command,
                                     state=state,
                                     flow_list=flows_list)
        else:
            pass

    # 设置槽数据，更新state对应信息
    def _handle_set_slots(self,state: DialogueState,
                          command: SetSlotsCommand):
        if state.active_task is not None:
            state.set_slots(command.slots)

    # 取消当前业务流程
    def _handle_cancel_flow(self,state: DialogueState,
                            flows_list: FlowsList):
        # 获取当前处理任务
        task = state.active_task
        # 激活系统的取消流程
        # 创建系统的取消流程对象 CanceledSystemContext
        ## CanceledSystemContext有两个参数
        ###  canceled_flow_id
        ### canceled_flow_name

        # 获取取消流程id 和 流程名称
        canceled_flow_id = task.flow_id
        flow=flows_list.get_flow_by_id(canceled_flow_id)
        canceled_flow_name = flow.name

        # # 创建系统的取消流程对象 CanceledSystemContext
        self._active_cancel_system_flow(state,flows_list,
                                canceled_flow_id,canceled_flow_name)

        # self.active_task = None
        state.end_active_task()

#########################通用方法：激活系统不同流程#######################################
    # 激活系统取消流程
    def _active_cancel_system_flow(self,state: DialogueState,
                                   flows_list: FlowsList,
                                   canceled_flow_id: str,
                                   canceled_flow_name: str):

        flow = flows_list.get_flow_by_id("system_task_canceled")
        state.start_system_task(
            CanceledSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                canceled_flow_id=canceled_flow_id,
                canceled_flow_name=canceled_flow_name,
            )
        )

    # 激活系统开始流程
    def _active_start_system_flow(self, state: DialogueState,
                                   flows_list: FlowsList,
                                   started_flow_id: str,
                                   started_flow_name: str):
        flow = flows_list.get_flow_by_id("system_task_started")
        state.start_system_task(
            StartedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                started_flow_id=started_flow_id,
                started_flow_name=started_flow_name,
            )
        )

    # 激活系统恢复流程
    def _active_resumed_system_flow(self, state: DialogueState,
                                   flows_list: FlowsList,
                                   resumed_flow_id: str,
                                   resumed_flow_name: str):
        flow = flows_list.get_flow_by_id("system_task_resumed")
        state.start_system_task(
            ResumedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                resumed_flow_id=resumed_flow_id,
                resumed_flow_name=resumed_flow_name,
            )
        )

    @staticmethod  # 激活系统的中断流程
    def _activate_interrupted_system_task(
            state: DialogueState, flow_list: FlowsList,
            *, interrupted_flow_id: str,
            interrupted_flow_name: str,

            started_flow_id: str, started_flow_name: str):

        flow = flow_list.get_flow_by_id(
            "system_task_interrupted")
        state.start_system_task(
            InterruptedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,

                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,

                started_flow_id=started_flow_id,
                started_flow_name=started_flow_name
            ))
#######################################################################
    # 开启的新的业务流程
    def _handle_start_flow(self, state: DialogueState,
                           command: StartFlowCommand,
                           flows_list: FlowsList):
        # 1 前置校验
        # 1.1 结束之前系统任务
        state.end_system_task()
        # 1.2 判断command的流程id
        if command.flow.startswith("system_"):
            raise ValueError("不能开启系统流程任务")
        # 1.3 command里面流程id是否存在
        target_flow = flows_list.get_flow_by_id(command.flow)
        if target_flow is None:
            raise ValueError("开启流程id不存在")

        # 2 获取当前正在处理任务，判断
        active_task = state.active_task

        # 2.1 如果当前存在处理任务
        if active_task is not None:
            # 子分支A1：活跃任务 == 本次要启动的流程（flow_id相同）
            if active_task.flow_id == command.flow:
                # 不需要重复启动，继续运行
                return

            # todo 修改位置，先赋值，否则先中断interrupt_active_task()，active_task为空了
            #  获取当前active_task流程id和名称
            interrupted_flow_id = active_task.flow_id
            flow = flows_list.get_flow_by_id(interrupted_flow_id)
            interrupted_flow_name = flow.name

            # 子分支A2：活跃任务 ≠ 本次要启动的流程（流程抢占场景）
            # 1） 中断当前正运行的任务
            state.interrupt_active_task()

            # 2） 判断当前新开启任务是否之前中断过
            # 中断任务列表 --不存在--当前要开启任务
            if not state.resume_task(command.flow):
                # 新任务流程id和名称
                start_flow_id = command.flow
                flow = flows_list.get_flow_by_id(start_flow_id)
                start_flow_name = flow.name
                # 开启新任务
                state.start_task(TaskContext(
                    flow_id=target_flow.id,
                    step_id=target_flow.start_step().id,
                ))
            # 中断任务列表 --存在---当前要开启任务
            # 中断流程id ： 1    中断流程名称：退款
            else:
                # 把存在中断列表流程恢复，InterruptedSystemContext
                # 获取中断流程id
                start_flow_id= command.flow
                # 获取中断流程名称
                flow = flows_list.get_flow_by_id(start_flow_id)
                start_flow_name = flow.name

            # 统一调用 _activate_interrupted_system_task
            self._activate_interrupted_system_task(
                state,flows_list,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,

                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name
            )
            return

        # 2.2 不存在正在处理任务
        # 判断新开启任务在暂停列表任务存在
        resumed = state.resume_task(command.flow)
        # 如果暂停列表存在
        if resumed:
            # 恢复
            flow = flows_list.get_flow_by_id(command.flow)
            self._active_resumed_system_flow(state,
                                            flows_list,
                                             resumed_flow_id=command.flow,
                                             resumed_flow_name=flow.name)
            return
        # 如果暂停列表 不存在
        state.start_task(TaskContext(
            flow_id=command.flow,
            step_id=target_flow.start_step().id,
        ))
        # 激活系统开始流程
        flow = flows_list.get_flow_by_id(command.flow)
        self._active_start_system_flow(
            state,flows_list,
            started_flow_id=command.flow,
            started_flow_name=flow.name
        )

        # 恢复业务流程

    # 恢复任务流程
    # {"command": "resume_task", "flow": "subscription_support"}
    def _handle_resume_task(self,
          state:DialogueState,flow_list:FlowsList,
          command: ResumeFlowCommand):
        # 1 校验 command.flow流程id
        ## command.flow不为空
        if command.flow is not None:
            # 根据流程id查询是否存在flowslist
            target_flow = flow_list.get_flow_by_id(command.flow)
            if target_flow is None:
                raise ValueError("流程不存在")
            # 记录流程id和名称，后面使用
            target_flow_id=target_flow.id
            target_flow_name = target_flow.name
        else: ## command.flow 为空
            # 如果command.flow等于空，从中断任务列表获取最新任务（最近放任务）
            if not state.paused_tasks:
                return
            # 从中断任务列表获取最新放的任务
            top_task = state.paused_tasks[-1]
            # 记录流程id和名称，后面使用
            target_flow_id = top_task.flow_id
            target_flow = flow_list.get_flow_by_id(target_flow_id)
            target_flow_name = target_flow.name

        # 2 获取当前活跃任务
        active_task = state.active_task
        # 2.1 活跃任务存在
        if active_task is not None:
            # 要恢复的流程 是否 当前活跃流程
            # 1) 相等
            if active_task.flow_id == target_flow_id:
                return
            # 2) 不相等
            # 把当前活跃任务中断，
            state.interrupt_active_task()

            # 记录当前中断流程id和名称
            interrupted_flow_id = active_task.flow_id
            flow = flow_list.get_flow_by_id(interrupted_flow_id)
            interrupted_flow_name = flow.name

            # 尝试恢复任务target_flow_id
            ## 恢复失败
            if not state.resume_task(flow_id=target_flow_id):
                # 回滚
                state.resume_task()
                return
            ## 恢复成功
            # 设置为新的active_task，在resume_task实现了
            # 激活系统任务
            self._activate_interrupted_system_task(
                state,flow_list,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,

                started_flow_id=target_flow_id,
                started_flow_name=target_flow_name
            )

        # 2.2 活跃任务不存在
        else:
            # 尝试恢复任务target_flow_id
            ## 恢复失败
            if not state.resume_task(flow_id=target_flow_id):
                return

            resumed = state.active_task
            flow = flow_list.get_flow_by_id(resumed.flow_id)
            # 激活系统任务
            self._active_resumed_system_flow(
                state,flow_list,
                resumed_flow_id=resumed.flow_id,
                resumed_flow_name=flow.name
            )
