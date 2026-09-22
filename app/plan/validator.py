from typing import List

from app.domain.state import DialogueState
from app.plan.turn_plan import TurnPlan, TurnPlanValidationResult, ClarifyReason
from app.task.command.models import StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumeFlowCommand
from app.task.flow.models import FlowsList

# 执行计划校验
class TurnPlanValidator:

    def validate(self,
                 state:DialogueState,
                 turn_plan:TurnPlan,
                 flows:FlowsList)->TurnPlanValidationResult:
        # 1 获取前一步意图识别内容轨道
        # active_tracks类型列表，因为识别轨道可能有多个
        active_tracks = self._active_tracks(turn_plan)

        # 2 如果意图识别内容没有轨道，返回false和失败信息
        if not active_tracks:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TRACK
            )

        # 3 如果有轨道，判断是否多个轨道
        # 3.1 如果多个轨道，返回校验失败和失败信息
        if len(active_tracks) > 1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TRACKS
            )

        # 3.2 只有一个轨道，根据轨道类型，对不同轨道进一步校验
        active_track = active_tracks[0]

        # 4 task任务轨道校验，成功返回true，失败：返回false和失败信息
        if active_track == "task": # 任务流程
            return self._validate_task_track(turn_plan,flows)

        # todo 5 knowledge 和 chitchat校验
        if active_track == "knowledge": # 知识文档
            return TurnPlanValidationResult(valid=True)
        if active_track == "chitchat":
            return TurnPlanValidationResult(valid=True)

        return TurnPlanValidationResult(valid=False, reason=ClarifyReason.MISSING_TRACK)

    # 从TurnPlan获取轨道
    def _active_tracks(self,turn_plan:TurnPlan)->List[str]:
        active_tracks: List[str] = []
        if turn_plan.task is not None:
            active_tracks.append("task")
        if turn_plan.knowledge is not None:
            active_tracks.append("knowledge")
        if turn_plan.chitchat is not None:
            active_tracks.append("chitchat")
        return active_tracks

    # 对任务流程意图识别内容，进一步校验
    def _validate_task_track(self,turn_plan:TurnPlan,
                             flows:FlowsList)->TurnPlanValidationResult:
        # todo 校验规则是自定义的，根据实际需求自己约定
        # 校验1：turn_plan是否存在 commands
        task_turn = turn_plan.task
        if not task_turn.commands:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TASK_COMMANDS
            )

        # 校验2：command值必须在四个中的某一个
        allowed = (StartFlowCommand,SetSlotsCommand,
                   CancelFlowCommand,ResumeFlowCommand)
        # all()
        if not all(isinstance(cmd,allowed)
                      for cmd in task_turn.commands):
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.INVALID_TASK_COMMANDS
            )

        # 校验3：是否存在多个 开启流程命令 start_flow
        # start_flow_cmd列表
        start_flow_cmd = [cmd for cmd in task_turn.commands
                          if isinstance(cmd,StartFlowCommand)]
        if len(start_flow_cmd) > 1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TASK_FLOWS
            )

        # 校验4：判断开启流程具体流程id 在所有流程是否存在
        if start_flow_cmd:
            flow_id = start_flow_cmd[0].flow
            # 根据flow_id查询流程
            flow = flows.get_flow_by_id(flow_id)
            # 判断
            if flow is None:
                return TurnPlanValidationResult(
                    valid=False,
                    reason=ClarifyReason.UNKNOWN_TASK_FLOW
                )
        return TurnPlanValidationResult(valid=True)
