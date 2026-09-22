from typing import List, Dict, Any
from app.domain.state import Turn, Session
from app.domain.messages import UserMessage, BotMessage, ObjectTypeMessage, MessageType


class HistoryBuilder:
    """

    1. 将用户消息的UserMessage对象序列化为字符串---->"USER: 我准备处理订阅问题"
    2. 将历史对话的Q(UserMessage)A(BotMessage)对象序列化为字符串："USER: App 更新后崩溃\n BOT: 好的，先提供 App 版本"

    """

    @staticmethod
    def build(turns: List[Turn]) -> str:
        """
        构建历史对话
        :param turns:
        :return:
        """

        msgs: List[str] = []
        for turn in turns:
            # 1. 用户消息
            user_message = turn.user_message
            user_message_str = HistoryBuilder._render_user_message(user_message)
            msgs.append(f"USER: {user_message_str}")
            # 2. 机器人回复消息
            for bot_msg in turn.bot_messages:
                bot_msg_str = HistoryBuilder._render_bot_message(bot_msg)
                msgs.append(f"BOT: {bot_msg_str}")
        return "\n".join(msgs)

    @staticmethod
    def _render_user_message(user_message: UserMessage) -> str:
        """
        渲染用户消息
        :param user_message:
        :return:
        """
        if user_message.type is MessageType.TEXT:
            return HistoryBuilder._render_text_msg(user_message.text)
        else:
            return HistoryBuilder._render_obj_msg(user_message.object)

    @staticmethod
    def _render_text_msg(text: str) -> str:
        return text.strip()

    @classmethod
    def _render_obj_msg(cls, object_msg: ObjectTypeMessage) -> str:
        """
        id
        type
        title
        attributes
        :param object_msg:
        :return:
        "[id='对象编号', type='业务对象类型', title='对象描述', attributes='key=value']"
        """
        labels = {
            "payment": "支付记录",
            "subscription_order": "订阅订单",
            "app": "App对象",
            "app_version": "App版本",
            "feedback": "用户反馈",
        }
        label = labels.get(object_msg.type, object_msg.type)
        id = object_msg.id
        title = object_msg.title
        attributes: Dict[str, Any] = object_msg.attributes
        attributes_str = " ".join([f"{key}={value}" for key, value in attributes.items()])

        return f"[label={label}, id={id}, title={title}, attributes={attributes_str}]"

    @classmethod
    def _render_bot_message(cls, bot_msg: BotMessage) -> str:
        if bot_msg.text:
            return HistoryBuilder._render_text_msg(bot_msg.text)
        else:
            return HistoryBuilder._render_obj_msg(bot_msg.object)  # 基本走不到
