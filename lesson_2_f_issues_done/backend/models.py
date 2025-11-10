from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserType(str, enum.Enum):
    CUSTOMER = "customer"
    TASKER = "tasker"

class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class BidStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Tasker-specific fields
    skills = Column(Text, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    
    # Relationships
    posted_tasks = relationship("Task", back_populates="customer", foreign_keys="Task.customer_id")
    bids = relationship("Bid", back_populates="tasker")
    customer_reviews = relationship("Review", back_populates="customer", foreign_keys="Review.customer_id")
    tasker_reviews = relationship("Review", back_populates="tasker", foreign_keys="Review.tasker_id")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    budget = Column(Float, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="posted_tasks", foreign_keys=[customer_id])
    bids = relationship("Bid", back_populates="task")
    agreement = relationship("Agreement", back_populates="task", uselist=False)
    reviews = relationship("Review", back_populates="task")

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    tasker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(BidStatus), default=BidStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="bids")
    tasker = relationship("User", back_populates="bids")
    agreement = relationship("Agreement", back_populates="bid", uselist=False)

class Agreement(Base):
    __tablename__ = "agreements"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    bid_id = Column(Integer, ForeignKey("bids.id"), nullable=False)
    agreed_amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="agreement")
    bid = relationship("Bid", back_populates="agreement")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tasker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="reviews")
    customer = relationship("User", back_populates="customer_reviews", foreign_keys=[customer_id])
    tasker = relationship("User", back_populates="tasker_reviews", foreign_keys=[tasker_id])

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)