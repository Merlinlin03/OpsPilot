"""
    消息分为
    用户消息
    客服（机器人）消息

    消息类型分为两种
    * 文本
    * 对象

    序列化： 对象 =》字典
    反序列化：字典 =》 对象
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Literal


# 消息类型:文本 text  对象 object
# Enum 枚举
class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"

# 对象类型消息
@dataclass
class ObjectTypeMessage:
    id: str
    type: str
    title: str=""
    # 下面代码，每次创建全新的字典，
    attributes: Dict[str, Any]=field(default_factory=dict)

    # 序列化： 对象 =》字典
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "attributes": self.attributes
        }

    # 反序列化：字典 =》 对象
    # clz 当前类  ObjectType
    @classmethod
    def from_dict(clz,data:Dict[str, Any]) -> "ObjectType":
        return clz(
            id=data["id"],
            type=data["type"],
            title=data.get("title",""),
            attributes=data.get("attributes", {})
        )

# 用户消息
@dataclass
class UserMessage:
    # 发送者id  用户id
    sender_id: str
    message_id: str # 消息id
    type: MessageType # 消息类型 ：文本 对象
    text: str | None = None  # 文本类型消息
    object: ObjectTypeMessage | None = None # 对象类型消息

    # 序列化
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            # 调用ObjectTypeMessage方法转换字典
            "object": self.object.to_dict() if self.object else None
        }

    # 反序列化
    @classmethod
    def from_dict(clz,data:Dict[str, Any]) -> "UserMessage":
        return clz(
            sender_id=data['sender_id'],
            message_id=data["message_id"],
            type=MessageType(data["type"]),
            text=data["text"],
            object=ObjectTypeMessage.from_dict(data['object'])
                        if data.get('object') else None
        )

# 机器人消息
@dataclass
class BotMessage:
    text: str | None = None
    object: ObjectTypeMessage | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotMessage":
        return cls(
            text=data["text"],
            object=ObjectTypeMessage.from_dict(data["object"])
                                if data["object"] else None
        )

@dataclass
class ProcessResult:
    sender_id: str
    message_id: str
    messages: list[BotMessage]


@dataclass(slots=True)
class ChatHistoryMessage:
    session_id: str
    role: Literal["user", "bot"]
    text: str | None = None
    object: ObjectTypeMessage | None = None

