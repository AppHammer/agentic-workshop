from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List

import database
import schemas
import auth

app = FastAPI(title="Tasker Platform API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup():
    database.init_db()

# Authentication endpoints
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user exists
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = database.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        location=user.location,
        skills=user.skills,
        hourly_rate=user.hourly_rate,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(database.User).filter(database.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/users/me", response_model=schemas.UserResponse)
def get_current_user(current_user: database.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(database.User).filter(database.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Task endpoints
@app.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != database.UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can post tasks")
    
    db_task = database.Task(
        customer_id=current_user.id,
        title=task.title,
        description=task.description,
        location=task.location,
        date=task.date,
        budget=task.budget
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[schemas.TaskResponse])
def list_tasks(
    status: database.TaskStatus = None,
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_user)
):
    query = db.query(database.Task)
    if status:
        query = query.filter(database.Task.status == status)
    return query.all()

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    db_task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/user/my-tasks", response_model=List[schemas.TaskResponse])
def get_my_tasks(
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role == database.UserRole.CUSTOMER:
        return db.query(database.Task).filter(database.Task.customer_id == current_user.id).all()
    else:
        # For taskers, return tasks they've bid on or have agreements for
        return db.query(database.Task).join(database.Bid).filter(database.Bid.tasker_id == current_user.id).all()

# Bid endpoints
@app.post("/bids", response_model=schemas.BidResponse)
def create_bid(
    bid: schemas.BidCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != database.UserRole.TASKER:
        raise HTTPException(status_code=403, detail="Only taskers can bid on tasks")
    
    # Check if task exists
    task = db.query(database.Task).filter(database.Task.id == bid.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if already bid
    existing_bid = db.query(database.Bid).filter(
        database.Bid.task_id == bid.task_id,
        database.Bid.tasker_id == current_user.id
    ).first()
    if existing_bid:
        raise HTTPException(status_code=400, detail="Already bid on this task")
    
    db_bid = database.Bid(
        task_id=bid.task_id,
        tasker_id=current_user.id,
        amount=bid.amount,
        message=bid.message
    )
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

@app.get("/tasks/{task_id}/bids", response_model=List[schemas.BidResponse])
def get_task_bids(task_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.Bid).filter(database.Bid.task_id == task_id).all()

# Offer endpoints
@app.post("/offers", response_model=schemas.OfferResponse)
def create_offer(
    offer: schemas.OfferCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != database.UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can make offers")
    
    # Verify the task belongs to the customer
    task = db.query(database.Task).filter(database.Task.id == offer.task_id).first()
    if not task or task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_offer = database.Offer(
        task_id=offer.task_id,
        customer_id=current_user.id,
        tasker_id=offer.tasker_id,
        amount=offer.amount,
        message=offer.message
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer

@app.post("/offers/{offer_id}/accept", response_model=schemas.AgreementResponse)
def accept_offer(
    offer_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    offer = db.query(database.Offer).filter(database.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if offer.tasker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mark offer as accepted
    offer.accepted = True
    
    # Create agreement
    agreement = database.Agreement(
        task_id=offer.task_id,
        tasker_id=current_user.id,
        amount=offer.amount
    )
    db.add(agreement)
    
    # Update task status
    task = db.query(database.Task).filter(database.Task.id == offer.task_id).first()
    task.status = database.TaskStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(agreement)
    return agreement

@app.post("/bids/{bid_id}/accept", response_model=schemas.AgreementResponse)
def accept_bid(
    bid_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    bid = db.query(database.Bid).filter(database.Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    task = db.query(database.Task).filter(database.Task.id == bid.task_id).first()
    if task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create agreement
    agreement = database.Agreement(
        task_id=bid.task_id,
        tasker_id=bid.tasker_id,
        amount=bid.amount
    )
    db.add(agreement)
    
    # Update task status
    task.status = database.TaskStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(agreement)
    return agreement

@app.get("/offers/my-offers", response_model=List[schemas.OfferResponse])
def get_my_offers(
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role == database.UserRole.CUSTOMER:
        return db.query(database.Offer).filter(database.Offer.customer_id == current_user.id).all()
    else:
        return db.query(database.Offer).filter(database.Offer.tasker_id == current_user.id).all()

# Agreement endpoints
@app.post("/agreements/{agreement_id}/complete")
def complete_agreement(
    agreement_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    agreement = db.query(database.Agreement).filter(database.Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    
    task = db.query(database.Task).filter(database.Task.id == agreement.task_id).first()
    if task.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the customer can mark task as complete")
    
    agreement.status = database.AgreementStatus.COMPLETED
    agreement.completed_at = datetime.utcnow()
    task.status = database.TaskStatus.COMPLETED
    
    db.commit()
    return {"message": "Task marked as complete"}

@app.get("/agreements", response_model=List[schemas.AgreementResponse])
def get_agreements(
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role == database.UserRole.CUSTOMER:
        return db.query(database.Agreement).join(database.Task).filter(
            database.Task.customer_id == current_user.id
        ).all()
    else:
        return db.query(database.Agreement).filter(
            database.Agreement.tasker_id == current_user.id
        ).all()

# Message endpoints
@app.post("/messages", response_model=schemas.MessageResponse)
def send_message(
    message: schemas.MessageCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    db_message = database.Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        task_id=message.task_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@app.get("/messages", response_model=List[schemas.MessageResponse])
def get_messages(
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    return db.query(database.Message).filter(
        (database.Message.sender_id == current_user.id) | 
        (database.Message.receiver_id == current_user.id)
    ).order_by(database.Message.created_at.desc()).all()

@app.put("/messages/{message_id}/read")
def mark_message_read(
    message_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    message = db.query(database.Message).filter(database.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    message.read = True
    db.commit()
    return {"message": "Message marked as read"}
# Task-specific message endpoints
@app.get("/tasks/{task_id}/messages", response_model=List[schemas.MessageResponse])
def get_task_messages(
    task_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Get the task
    task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the agreement for this task
    agreement = db.query(database.Agreement).filter(
        database.Agreement.task_id == task_id
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=403, detail="No agreement for this task")
    
    # Verify user is either customer or tasker
    if task.customer_id != current_user.id and agreement.tasker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view messages for this task")
    
    # Get all messages for this task
    messages = db.query(database.Message).filter(
        database.Message.task_id == task_id
    ).order_by(database.Message.created_at).all()
    
    return messages

@app.post("/tasks/{task_id}/messages", response_model=schemas.MessageResponse)
def send_task_message(
    task_id: int,
    message: schemas.TaskMessageCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Get the task
    task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the agreement for this task
    agreement = db.query(database.Agreement).filter(
        database.Agreement.task_id == task_id,
        database.Agreement.status == database.AgreementStatus.ACCEPTED
    ).first()
    
    if not agreement:
        raise HTTPException(status_code=403, detail="Agreement must be accepted before messaging")
    
    # Verify user is either customer or tasker
    if task.customer_id != current_user.id and agreement.tasker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send messages for this task")
    
    # Determine receiver
    receiver_id = agreement.tasker_id if current_user.id == task.customer_id else task.customer_id
    
    # Create message
    db_message = database.Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        task_id=task_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


# Review endpoints
@app.post("/reviews", response_model=schemas.ReviewResponse)
def create_review(
    review: schemas.ReviewCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Verify the task is completed
    task = db.query(database.Task).filter(database.Task.id == review.task_id).first()
    if not task or task.status != database.TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed tasks")
    
    # Check if user is involved in the task
    agreement = db.query(database.Agreement).filter(database.Agreement.task_id == review.task_id).first()
    if not agreement:
        raise HTTPException(status_code=400, detail="No agreement found for this task")
    
    if current_user.id != task.customer_id and current_user.id != agreement.tasker_id:
        raise HTTPException(status_code=403, detail="Not authorized to review this task")
    
    # Check if already reviewed
    existing_review = db.query(database.Review).filter(
        database.Review.task_id == review.task_id,
        database.Review.reviewer_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Already reviewed this task")
    
    db_review = database.Review(
        task_id=review.task_id,
        reviewer_id=current_user.id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/users/{user_id}/reviews", response_model=List[schemas.ReviewResponse])
def get_user_reviews(user_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.Review).filter(database.Review.reviewee_id == user_id).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)