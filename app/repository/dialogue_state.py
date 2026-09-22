from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.repository.base import Base


class DialogueStateRecord(Base):
    """dialogue_states 表：每个用户一行，state_json 存储完整对话状态。"""

    __tablename__ = "dialogue_states"

    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    state_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")