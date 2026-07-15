from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import utcnow

# Estados posibles: pending, running, completed, failed, cancelled


class Search(Base):
    __tablename__ = "searches"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    original_query: Mapped[str] = mapped_column(Text)
    search_type: Mapped[str] = mapped_column(String(30))  # person | company | supplier | ...
    status: Mapped[str] = mapped_column(String(20), default="pending")
    criteria_json: Mapped[dict] = mapped_column(JSON)
    requested_fields_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    max_results: Mapped[int] = mapped_column(Integer, default=20)
    progress_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
