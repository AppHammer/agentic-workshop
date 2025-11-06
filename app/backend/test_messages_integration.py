"""
Integration tests for message endpoint with permission validation.

Tests verify that messaging is properly restricted based on relationships
between users (bids, offers, and agreements).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database import Base, get_db, User, Task, Bid, Offer, Agreement, UserRole, TaskStatus, AgreementStatus
from auth import get_password_hash, create_access_token

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_messages.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_users(test_db):
    """Create test users (customer and tasker)."""
    db = TestingSessionLocal()
    
    customer = User(
        email="customer@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Customer",
        role=UserRole.CUSTOMER,
        location="Test City"
    )
    
    tasker = User(
        email="tasker@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Tasker",
        role=UserRole.TASKER,
        location="Test City",
        skills="Testing",
        hourly_rate=50.0
    )
    
    other_user = User(
        email="other@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Other User",
        role=UserRole.CUSTOMER,
        location="Test City"
    )
    
    db.add_all([customer, tasker, other_user])
    db.commit()
    db.refresh(customer)
    db.refresh(tasker)
    db.refresh(other_user)
    
    users = {
        "customer": customer,
        "tasker": tasker,
        "other": other_user
    }
    
    db.close()
    return users


@pytest.fixture
def auth_headers(test_users):
    """Create authentication headers for test users."""
    headers = {}
    for role, user in test_users.items():
        token = create_access_token(data={"sub": user.email})
        headers[role] = {"Authorization": f"Bearer {token}"}
    return headers


def test_send_message_with_bid_relationship(client, test_users, auth_headers):
    """Test authorized message creation when bid relationship exists."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create bid (tasker bids on customer's task)
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0,
        message="I can do this"
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Tasker should be able to message customer
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Hello, I bid on your task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sender_id"] == test_users["tasker"].id
    assert data["receiver_id"] == test_users["customer"].id
    assert data["content"] == "Hello, I bid on your task"
    
    # Customer should be able to message tasker back
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker"].id,
            "task_id": task.id,
            "content": "Thanks for your bid"
        }
    )
    
    assert response.status_code == 200


def test_send_message_with_offer_relationship(client, test_users, auth_headers):
    """Test authorized message creation when offer relationship exists."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create offer (customer offers to tasker)
    offer = Offer(
        task_id=task.id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker"].id,
        amount=95.0,
        message="Are you interested?"
    )
    db.add(offer)
    db.commit()
    db.close()
    
    # Customer should be able to message tasker
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker"].id,
            "task_id": task.id,
            "content": "I sent you an offer"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["sender_id"] == test_users["customer"].id
    assert data["receiver_id"] == test_users["tasker"].id
    
    # Tasker should be able to message customer back
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Thanks for the offer"
        }
    )
    
    assert response.status_code == 200


def test_send_message_with_agreement_relationship(client, test_users, auth_headers):
    """Test authorized message creation when agreement relationship exists."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.IN_PROGRESS
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=100.0,
        status=AgreementStatus.ACCEPTED
    )
    db.add(agreement)
    db.commit()
    db.close()
    
    # Both parties should be able to message each other
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker"].id,
            "task_id": task.id,
            "content": "How is the task going?"
        }
    )
    
    assert response.status_code == 200
    
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Making good progress!"
        }
    )
    
    assert response.status_code == 200


def test_send_message_without_relationship_forbidden(client, test_users, auth_headers):
    """Test that messaging is forbidden when no relationship exists."""
    # Try to send message without any bid, offer, or agreement
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["other"].id,
            "content": "Random message"
        }
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "permission" in data["detail"].lower()
    assert "bid, offer, or agreement" in data["detail"]


def test_forbidden_response_format(client, test_users, auth_headers):
    """Test that 403 error response has proper format and user-friendly message."""
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["other"].id,
            "content": "Unauthorized message"
        }
    )
    
    assert response.status_code == 403
    data = response.json()
    
    # Verify error structure
    assert "detail" in data
    assert isinstance(data["detail"], str)
    
    # Verify message is user-friendly and informative
    error_message = data["detail"]
    assert "permission" in error_message.lower()
    assert "bid" in error_message.lower()
    assert "offer" in error_message.lower()
    assert "agreement" in error_message.lower()


def test_user_id_from_jwt_not_request_body(client, test_users, auth_headers):
    """Test that user ID is extracted from JWT token, not from request body."""
    db = TestingSessionLocal()
    
    # Create bid relationship between customer and tasker
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Send message - sender_id should come from JWT, not request
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Test message"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify sender_id matches the JWT user (tasker), not any value in request
    assert data["sender_id"] == test_users["tasker"].id
    assert data["receiver_id"] == test_users["customer"].id


def test_cannot_message_self(client, test_users, auth_headers):
    """Test that users cannot message themselves."""
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["customer"].id,
            "content": "Message to myself"
        }
    )
    
    assert response.status_code == 403


def test_multiple_relationship_types(client, test_users, auth_headers):
    """Test that messaging works with multiple types of relationships."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create both bid and offer for same users
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    
    offer = Offer(
        task_id=task.id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker"].id,
        amount=95.0
    )
    
    db.add_all([bid, offer])
    db.commit()
    db.close()
    
    # Messaging should work (permission validation short-circuits on first match)
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "We have multiple relationships"
        }
    )
    
    assert response.status_code == 200


def test_unauthenticated_message_attempt(client, test_users):
    """Test that unauthenticated users cannot send messages."""
    response = client.post(
        "/messages",
        json={
            "receiver_id": test_users["customer"].id,
            "content": "Unauthenticated message"
        }
    )
    
    assert response.status_code == 401


def test_message_with_valid_task_id(client, test_users, auth_headers):
    """Test message creation with valid task_id."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create bid relationship
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Send message with task_id
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Message about this task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id
    assert data["content"] == "Message about this task"
    
    # Verify task_id persisted in database
    db = TestingSessionLocal()
    from database import Message
    message = db.query(Message).filter(Message.id == data["id"]).first()
    assert message is not None
    assert message.task_id == task.id
    db.close()


def test_message_without_task_id(client, test_users, auth_headers):
    """Test message creation without task_id (general message)."""
    db = TestingSessionLocal()
    
    # Create task and bid to establish relationship
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Send message without task_id
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "content": "General message not about specific task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] is None
    assert data["content"] == "General message not about specific task"


def test_message_with_invalid_task_id(client, test_users, auth_headers):
    """Test message creation with invalid task_id returns 404."""
    db = TestingSessionLocal()
    
    # Create task and bid to establish relationship
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Try to send message with non-existent task_id
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": 99999,  # Non-existent task
            "content": "Message about non-existent task"
        }
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_message_task_permission_customer_not_owner(client, test_users, auth_headers):
    """Test that customer cannot message about task they don't own."""
    db = TestingSessionLocal()
    
    # Create task owned by "other" user
    task = Task(
        customer_id=test_users["other"].id,
        title="Other's Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create bid from tasker to establish customer-tasker relationship
    other_task = Task(
        customer_id=test_users["customer"].id,
        title="Customer's Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(other_task)
    db.commit()
    db.refresh(other_task)
    
    bid = Bid(
        task_id=other_task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Customer tries to message about task they don't own
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker"].id,
            "task_id": task.id,  # Task owned by "other"
            "content": "Message about task I don't own"
        }
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "permission" in data["detail"].lower()


def test_message_task_permission_tasker_no_relationship(client, test_users, auth_headers):
    """Test that tasker cannot message about task they have no relationship with."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create a different task to establish customer-tasker relationship
    other_task = Task(
        customer_id=test_users["customer"].id,
        title="Other Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(other_task)
    db.commit()
    db.refresh(other_task)
    
    # Tasker has bid on other_task, not on task
    bid = Bid(
        task_id=other_task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    db.close()
    
    # Tasker tries to message about task they have no relationship with
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,  # No bid/offer/agreement on this task
            "content": "Message about task I'm not involved with"
        }
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "permission" in data["detail"].lower()


def test_message_task_permission_tasker_with_offer(client, test_users, auth_headers):
    """Test that tasker can message about task they have an offer for."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create offer (customer offers to tasker)
    offer = Offer(
        task_id=task.id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker"].id,
        amount=95.0
    )
    db.add(offer)
    db.commit()
    db.close()
    
    # Tasker should be able to message about task with offer
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Thanks for the offer on this task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id


def test_message_task_permission_tasker_with_agreement(client, test_users, auth_headers):
    """Test that tasker can message about task they have an agreement for."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test Task",
        description="Test Description",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.IN_PROGRESS
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=100.0
    )
    db.add(agreement)
    db.commit()
    db.close()
    
    # Tasker should be able to message about task with agreement
    response = client.post(
        "/messages",
        headers=auth_headers["tasker"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task.id,
            "content": "Update on our agreed task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task.id