from dataclasses import dataclass, field, asdict
from typing import Dict, Any

# 业务任务**的执行快照（用户想做的事）
@dataclass
class TaskContext:
    flow_id:str # 流程id，比如 subscription_support
    step_id:str | None=None  # 步骤id ask_order_number
    # 收集槽数据 字典
    slots: Dict[str, Any]=field(default_factory=dict)

    # 序列化
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # 反序列化
    @classmethod
    def from_dict(clz, data: Dict[str, Any]) -> "TaskContext":
        if data:
            return clz(
                flow_id=data.get("flow_id",""),
                step_id=data.get("step_id",""),
                slots=data.get("slots","")
            )
        else:
            return None

# **系统流程**的执行快照（系统插播的过场）
@dataclass
class SystemContext:
    flow_id:str
    step_id:str | None=None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(clz, data: Dict[str, Any]) -> "SystemContext":
        clz = FLOW_ID_TO_CONTEXT_CLASS[data["flow_id"]]
        return clz(**data)

# 任务正常开始
@dataclass
class StartedSystemContext(SystemContext):
    # 开始的业务流程 ID，来自 user_flows.yml
    started_flow_id: str = ""
    # # 开始的业务流程
    started_flow_name: str = ""

# 中断任务
@dataclass
class InterruptedSystemContext(SystemContext):
    # 中断（暂停）业务流程id  和 名称
    interrupted_flow_id: str = ""
    interrupted_flow_name: str = ""

    # 新开始的业务流程 ID 和名称
    started_flow_id: str = ""
    started_flow_name: str = ""

# 取消任务
@dataclass
class CanceledSystemContext(SystemContext):
    canceled_flow_id: str = ""
    canceled_flow_name: str = ""

# 恢复任务
@dataclass
class ResumedSystemContext(SystemContext):
    resumed_flow_id: str = ""
    resumed_flow_name: str = ""

# 收集槽数据
@dataclass
class CollectSystemContext(SystemContext):
    slot_name: str = ""
    response: dict[str, Any] = field(default_factory=dict)

FLOW_ID_TO_CONTEXT_CLASS = {
    "system_task_started": StartedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_canceled": CanceledSystemContext,
    "system_task_resumed": ResumedSystemContext,
    "system_collect_information": CollectSystemContext
}



