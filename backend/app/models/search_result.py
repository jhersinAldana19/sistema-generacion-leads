from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import utcnow

# status: candidate | probable | confirmed | outdated | needs_review | discarded
# review_status: pending | confirmed | discarded | flagged


class SearchResult(Base):
    __tablename__ = "search_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_id: Mapped[int] = mapped_column(ForeignKey("searches.id"), index=True)
    result_data_json: Mapped[dict] = mapped_column(JSON)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="candidate")
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
