"""
    # 编写接口方法，约定访问路径
    # 获取前端提交数据
    # 调用service方法执行业务处理
    # 返回前端最终数据
"""
import uuid

from fastapi import APIRouter
from fastapi.params import Depends

from app.api.dependencies import get_dialogue_service
from app.api.schemas import ChatRequest, ChatResponse, ChatBotMessage, ChatObject, ChatMessageResponse
from app.domain.messages import ProcessResult, UserMessage, MessageType, ObjectTypeMessage
from app.service.dialogue_service import DialogueService

# 创建路由对象
chat_router = APIRouter()

# 聊天接口，设置访问路径
@chat_router.post("/api/chat")
async def chat(chat_request: ChatRequest,
               dialogue_service: DialogueService=Depends(get_dialogue_service)
                            )->ChatResponse:
    # 因为web层调用service层，
    # 把service对象注入进来
    # 1  获取前端提交数据 chat_request

    # 2 把web层获取数据模型ChatRequest =》转换 service数据模型 UserMessage
    user_message = _build_user_message(chat_request)

    # 3 调用service层方法实现具体业务
    process_result:ProcessResult=await dialogue_service.process_message(
                                                        user_message)

    # 4 把service返回数据转换 web层返回数据模型ChatResponse，返回给前端
    chat_response = _build_chat_response(process_result)
    return chat_response


# 2 把web层获取数据模型ChatRequest =》转换 service数据模型 UserMessage
def _build_user_message(chat_request:ChatRequest)->UserMessage:
    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id
              if chat_request.message_id else str(uuid.uuid4()),
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,
        object=ObjectTypeMessage(
            type=chat_request.object.type,
            id=chat_request.object.id,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes)
        if chat_request.object else None
    )

# 4 把service返回数据转换 web层返回数据模型ChatResponse
def _build_chat_response(process_result:ProcessResult)->ChatResponse:
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,

        messages=[
            ChatBotMessage(
                text=message.text,
                object=ChatObject(
                    type=message.object.type,
                    id=message.object.id,
                    title=message.object.title,
                    attributes=message.object.attributes
                )
                if message.object else None
            )
            for message in process_result.messages
        ]
    )

##############################
@chat_router.get("/api/chat/history", response_model=ChatMessageResponse)
async def chat_history_endpoint(sender_id: str,
                                service: DialogueService = Depends(get_dialogue_service)
                                ) -> ChatMessageResponse:
    return ChatMessageResponse(sender_id=sender_id, messages=[])