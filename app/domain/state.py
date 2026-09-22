import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any

from app.domain.contexts import TaskContext, SystemContext
from app.domain.messages import UserMessage, BotMessage, ObjectTypeMessage


# 本轮对话对象
# 用户一个提问，客服一个或者多个回答
@dataclass
class Turn:
    # 本轮对话id
    turn_id: str
    # 用户一个提问
    user_message: UserMessage
    # 客服一个或者多个回答
    bot_messages: list[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict(),
            "bot_messages": [bot_message.to_dict()
                             for bot_message in self.bot_messages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data['turn_id'],
            user_message=UserMessage.from_dict(data['user_message']),
            bot_messages=[BotMessage.from_dict(bot_msg_dict)
                          for bot_msg_dict in data['bot_messages']]
        )

# 会话对象
@dataclass
class Session:
    # 会话id
    session_id: str
    # 会话开始时间戳
    started_at: float
    # 最后一次活跃时间戳
    last_activity_at: float
    # 关闭会话时间戳
    closed_at: float | None = None
    # 多轮对话
    turns: list[Turn]=field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activity_at": self.last_activity_at,
            "closed_at": self.closed_at,
            "turns": [turn.to_dict() for turn in self.turns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        return cls(
            session_id=data['session_id'],
            started_at=data['started_at'],
            last_activity_at=data['last_activity_at'],
            closed_at=data['closed_at'],
            turns=[Turn.from_dict(turn) for turn in data['turns']],
        )

# 封装用户做操作全量数据
@dataclass
class DialogueState:
    sender_id: str # 用户id
    active_task: TaskContext | None = None # 当前活跃任务
    # 中断任务（暂停）
    paused_tasks: list[TaskContext] = field(default_factory=list)
    # 当前活跃系统任务
    active_system_task: SystemContext | None = None

    # 如果用户消息是对象类型
    focused_object: ObjectTypeMessage | None = None
    # 多次会话，列表
    # 用户做一个操作，可能经过多轮会话
    sessions: list[Session] = field(default_factory=list)
    # 当前会话id
    current_session_id: str | None = None
    # 当前处理轮次
    pending_turn: Turn | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task.to_dict()
                          if self.active_task else None,
            "paused_tasks": [paused_task.to_dict()
                             for paused_task in self.paused_tasks],

            "active_system_task": self.active_system_task.to_dict()
                            if self.active_system_task else None,

            "focused_object": self.focused_object.to_dict()
                        if self.focused_object else None,

            "sessions": [session.to_dict()
                         for session in self.sessions],
            "current_session_id": self.current_session_id,
            "pending_turn": self.pending_turn.to_dict()
                            if self.pending_turn else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueState":
        return cls(
            sender_id=data['sender_id'],
            active_task = TaskContext.from_dict(data['active_task']),
            paused_tasks = [TaskContext.from_dict(paused_task)
                            for paused_task in data['paused_tasks']],

            active_system_task=SystemContext.from_dict(data['active_system_task'])
                    if data.get('active_system_task') else None,
            focused_object=ObjectTypeMessage.from_dict(data['focused_object'])
                if data.get('focused_object') else None,
            sessions=[Session.from_dict(session_dict)
                      for session_dict in data['sessions']],
            current_session_id=data.get('current_session_id'),
            pending_turn=Turn.from_dict(data['pending_turn'])
                    if data.get('pending_turn') else None
        )

    #---------任务相关的--------
    # 开始任务
    def start_task(self, task: TaskContext):
        self.active_task = task

    # 结束任务
    def end_active_task(self):
        self.active_task = None

    # 取消任务
    def cancel_active_task(self):
        self.active_task = None
        self.active_system_task = None

    # 中断任务
    def interrupt_active_task(self):
        # 把任务放到中断列表  追加
        self.paused_tasks.append(self.active_task)
        # 把active_task空
        self.active_task = None


    # 恢复任务
    def resume_task(self,flow_id: str=None)->bool:

        if not self.paused_tasks:
            return False

        if flow_id is None:
            task = self.paused_tasks.pop()
            self.active_task = task
            return True

        # 从paused_tasks获取所有中断任务
        for task in self.paused_tasks:
            # 找到和flow_id相同中断任务
            if task.flow_id == flow_id:
                # 找到之后，active_task设置任务
                self.active_task = task
                # 从中断列表删除任务
                self.paused_tasks.remove(task)
                return True
        return False

    # 系统任务开始和结束
    def start_system_task(self, system_context: SystemContext):
        self.active_system_task = system_context

    def end_system_task(self):
        self.active_system_task = None

    #-----------槽位相关方法----------
    def set_slots(self, slots: Dict[str, Any]):
        # {a:1,b:2} .update({c:3}) => {a:1,b:2,c:3}
        self.active_task.slots.update(slots)

    def remove_slot(self, slot_name: str):
        self.active_task.slots.pop(slot_name)


   # --------------当前信息（当前任务、当前session）--------------------------
    # 当前正在执行的任务（系统流程、业务任务）
    def current_active_task(self):
        # 先获取系统流程 如果获取不到 获取业务任务
        return self.active_system_task or self.active_task

    # 返回当前session
    def current_session(self)->Session | None:
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session
        return None

    # --------------session相关的--------------------------

    def start_session(self): # 开启session
        if self.current_session() is None:
            now = time.time()
            session=Session(
                session_id=str(uuid.uuid4()),
                    started_at=now,
                            last_activity_at=now)
            self.sessions.append(session)
            self.current_session_id=session.session_id

    def close_session(self):
        if self.current_session() is not None:
            # 1. 修改session的时间closed_at
            self.current_session().closed_at=time.time()
            # 2. 清空当前的session_id
            self.current_session_id = None

##########################################################################
##########################################################################
    def reset_running_state_for_new_session(self):
        """
        session会话超时（60min超时时间）
        :return:
        """
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.pending_turn = None
        self.current_session_id = None

    # --------------turn相关的--------------------------

    def begin_turn(self, message: UserMessage):
        if self.current_session():
            turn = Turn(turn_id=str(uuid.uuid4()),
                        user_message=message,bot_messages=[])
            self.pending_turn = turn

    def commit_turn(self):
        if self.current_session():
            self.current_session().turns.append(self.pending_turn)
            self.pending_turn = None

    # --------------FocusedObject相关的--------------------------
    def set_focused_object(self,focused_object:ObjectTypeMessage):
        self.focused_object = focused_object
