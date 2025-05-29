from datetime import datetime, timezone

from sqlalchemy import event
from sqlmodel import Field, Session, SQLModel


class TimestampMixin(SQLModel):
    """Mixin that just uses Python to set timestamps."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


@event.listens_for(Session, "before_flush")
def update_timestamp(session, _flush_context, _instances):
    for obj in session.dirty:
        if isinstance(obj, SQLModel) and hasattr(obj, "updated_at"):
            obj.updated_at = datetime.now(timezone.utc)
