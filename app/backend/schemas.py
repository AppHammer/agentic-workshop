from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from database import UserRole, TaskStatus, AgreementStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: str
    location: str
    date: datetime
    budget: float

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None
    budget: Optional[float] = None
    status: Optional[TaskStatus] = None

class TaskResponse(TaskBase):
    id: int
    customer_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Bid schemas
class BidBase(BaseModel):
    task_id: int
    amount: float
    message: Optional[str] = None

class BidCreate(BidBase):
    pass

class BidResponse(BidBase):
    id: int
    tasker_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Offer schemas
class OfferBase(BaseModel):
    task_id: int
    tasker_id: int
    amount: float
    message: Optional[str] = None

class OfferCreate(OfferBase):
    pass

class OfferResponse(OfferBase):
    id: int
    customer_id: int
    accepted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Agreement schemas
class AgreementResponse(BaseModel):
    id: int
    task_id: int
    tasker_id: int
    amount: float
    status: AgreementStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    receiver_id: int
    task_id: Optional[int] = None
    content: str

class MessageCreate(MessageBase):
    pass

class TaskMessageCreate(BaseModel):
    content: str

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageResponseWithTask(MessageResponse):
    """Enhanced message response including task context"""
    task_title: Optional[str] = None
    task_status: Optional[TaskStatus] = None
    sender_name: Optional[str] = None
    sender_role: Optional[UserRole] = None
    receiver_name: Optional[str] = None
    receiver_role: Optional[UserRole] = None
    
    class Config:
        from_attributes = True

# Review schemas
class ReviewBase(BaseModel):
    task_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    reviewer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True