from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Enum as SQLAREnum, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

Base = declarative_base()

class PlatformType(enum.Enum):
    STEAM = "Steam"
    EPIC = "Epic"
    GOG = "GOG"
    UNKNOWN = "Unknown"

class LedgerEventType(enum.Enum):
    CLAIM = "CLAIM"
    BONUS = "BONUS"
    LEVEL_UP = "LEVEL_UP"

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Identity (The "Unique Constraint")
    platform = Column(SQLAREnum(PlatformType), nullable=False)
    external_id = Column(String(255), nullable=False)
    
    # Metadata
    title = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=False)
    image_url = Column(String(1024), nullable=True)
    
    # Economics (Mutable)
    price_original = Column(Float, nullable=True)
    price_discount = Column(Float, nullable=True)
    is_free_now = Column(Boolean, default=False)
    
    # Lifecycle
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('platform', 'external_id', name='uq_offers_platform_external_id'),
    )

class UserOfferState(Base):
    __tablename__ = "user_offer_state"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id"), primary_key=True)
    
    # UX States
    opened_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    # The Economic Assert
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    
    # UI housekeeping
    is_focused = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

class LedgerEvent(Base):
    __tablename__ = "ledger_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    type = Column(SQLAREnum(LedgerEventType), nullable=False)
    value_delta = Column(Integer, nullable=False) # e.g. +1500 XP
    
    # Optional link to an offer (if the event was a Claim)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id"), nullable=True)
    
    metadata_snapshot = Column(JSON, nullable=True) # Snapshot of deal data at claim time
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
