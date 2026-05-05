from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    status = Column(String, default="OPEN", nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)
    mttr = Column(Float, nullable=True)

    # Relationship
    rca = relationship("RCA", back_populates="work_item", uselist=False)


class RCA(Base):
    __tablename__ = "rca"

    id = Column(Integer, primary_key=True, index=True)
    work_item_id = Column(Integer, ForeignKey("work_items.id"))
    root_cause = Column(String)
    fix = Column(String)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    work_item = relationship("WorkItem", back_populates="rca")