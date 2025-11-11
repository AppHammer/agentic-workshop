from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserType, TaskStatus, BidStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    user_type: UserType

class UserCreate(UserBase):
    password: str
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
class UserProfile(BaseModel):
    """Complete user profile schema with all fields"""
    id: int
    username: str
    email: EmailStr
    user_type: UserType
    created_at: datetime
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    
    class Config:
        from_attributes = True


# Task schemas
class TaskBase(BaseModel):
    title: str
    description: str
    location: str
    date: datetime
    budget: float

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    status: TaskStatus
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskWithBids(Task):
    bids: List['Bid'] = []

# Bid schemas
class BidBase(BaseModel):
    amount: float
    message: Optional[str] = None

class BidCreate(BidBase):
    task_id: int

class Bid(BidBase):
    id: int
    task_id: int
    tasker_id: int
    status: BidStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Agreement schemas
class AgreementCreate(BaseModel):
    task_id: int
    bid_id: int

class Agreement(BaseModel):
    id: int
    task_id: int
    bid_id: int
    agreed_amount: float
    is_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Review schemas
class ReviewCreate(BaseModel):
    task_id: int
    tasker_id: int
    rating: int
    comment: Optional[str] = None

class Review(BaseModel):
    id: int
    task_id: int
    customer_id: int
    tasker_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    receiver_id: int
    task_id: Optional[int] = None
    content: str

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    task_id: Optional[int] = None
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Resolve forward references
TaskWithBids.model_rebuild()