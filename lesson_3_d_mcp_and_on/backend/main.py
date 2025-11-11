from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import models
import schemas
from database import engine, get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tasker Marketplace API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoints
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        user_type=user.user_type,
        skills=user.skills,
        hourly_rate=user.hourly_rate
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
@app.get("/users/me/profile", response_model=schemas.UserProfile)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """
    Get the complete profile of the currently authenticated user.
    
    Returns:
        UserProfile: Complete user profile including tasker-specific fields if applicable
    
    Raises:
        HTTPException: 401 if authentication fails
    """
    return current_user
@app.put("/users/me", response_model=schemas.UserProfile)
def update_user_profile(
    user_data: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile information."""
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user



# Task endpoints
@app.post("/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != models.UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create tasks")
    
    db_task = models.Task(**task.dict(), customer_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[schemas.Task])
def list_tasks(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Task)
    
    if status:
        query = query.filter(models.Task.status == status)
    
    # Taskers see open tasks, customers see their own tasks
    if current_user.user_type == models.UserType.TASKER:
        query = query.filter(models.Task.status == models.TaskStatus.OPEN)
    else:
        query = query.filter(models.Task.customer_id == current_user.id)
    
    return query.all()

@app.get("/tasks/{task_id}", response_model=schemas.TaskWithBids)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    task.status = status
    db.commit()
    return {"message": "Task status updated"}

# Bid endpoints
@app.post("/bids", response_model=schemas.Bid)
def create_bid(
    bid: schemas.BidCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != models.UserType.TASKER:
        raise HTTPException(status_code=403, detail="Only taskers can create bids")
    
    task = db.query(models.Task).filter(models.Task.id == bid.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.OPEN:
        raise HTTPException(status_code=400, detail="Task is not open for bidding")
    
    db_bid = models.Bid(**bid.dict(), tasker_id=current_user.id)
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

@app.get("/bids/my-bids", response_model=List[schemas.Bid])
def get_my_bids(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != models.UserType.TASKER:
        raise HTTPException(status_code=403, detail="Only taskers can view their bids")
    
    return db.query(models.Bid).filter(models.Bid.tasker_id == current_user.id).all()

@app.put("/bids/{bid_id}/accept")
def accept_bid(
    bid_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bid = db.query(models.Bid).filter(models.Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    task = db.query(models.Task).filter(models.Task.id == bid.task_id).first()
    
    # Check if current user is the customer who posted the task
    if task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create agreement
    agreement = models.Agreement(
        task_id=task.id,
        bid_id=bid.id,
        agreed_amount=bid.amount
    )
    bid.status = models.BidStatus.ACCEPTED
    task.status = models.TaskStatus.IN_PROGRESS
    
    db.add(agreement)
    db.commit()
    
    return {"message": "Bid accepted, agreement created"}

# Agreement endpoints
@app.get("/agreements", response_model=List[schemas.Agreement])
def get_agreements(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type == models.UserType.CUSTOMER:
        tasks = db.query(models.Task).filter(models.Task.customer_id == current_user.id).all()
        task_ids = [task.id for task in tasks]
        return db.query(models.Agreement).filter(models.Agreement.task_id.in_(task_ids)).all()
    else:
        bids = db.query(models.Bid).filter(models.Bid.tasker_id == current_user.id).all()
        bid_ids = [bid.id for bid in bids]
        return db.query(models.Agreement).filter(models.Agreement.bid_id.in_(bid_ids)).all()

@app.put("/agreements/{agreement_id}/pay")
def mark_as_paid(
    agreement_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agreement = db.query(models.Agreement).filter(models.Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    task = db.query(models.Task).filter(models.Task.id == agreement.task_id).first()
    if task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    agreement.is_paid = True
    task.status = models.TaskStatus.COMPLETED
    db.commit()
    
    return {"message": "Payment confirmed, task completed"}

# Review endpoints
@app.post("/reviews", response_model=schemas.Review)
def create_review(
    review: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != models.UserType.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create reviews")
    
    task = db.query(models.Task).filter(models.Task.id == review.task_id).first()
    if not task or task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if task.status != models.TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed tasks")
    
    db_review = models.Review(
        **review.dict(),
        customer_id=current_user.id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/reviews/tasker/{tasker_id}", response_model=List[schemas.Review])
def get_tasker_reviews(tasker_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.tasker_id == tasker_id).all()

# Message endpoints
@app.post("/messages", response_model=schemas.Message)
def send_message(
    message: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_message = models.Message(**message.dict(), sender_id=current_user.id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages", response_model=List[schemas.Message])
def get_messages(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Message).filter(
        (models.Message.sender_id == current_user.id) |
        (models.Message.receiver_id == current_user.id)
    ).all()

@app.put("/messages/{message_id}/read")
def mark_message_read(
    message_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message or message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    message.is_read = True
    db.commit()
    return {"message": "Message marked as read"}

@app.get("/")
def root():
    return {"message": "Tasker Marketplace API"}