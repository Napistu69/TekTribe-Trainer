"""CurrencyLedger model — tracks all currency balances per user."""
from datetime import datetime, timezone

import sqlalchemy
from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CurrencyLedger(Base):
    __tablename__ = "currency_ledgers"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), primary_key=True
    )
    dust_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    shard_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    cuboid_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    ele_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    transaction_log: Mapped[list] = mapped_column(JSONB, default=[])
