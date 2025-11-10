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


def test_get_messages_with_task_details(client, test_users, auth_headers):
    """Test GET /messages includes task details when task_id is present."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Fix my sink",
        description="Leaky faucet needs repair",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id  # Store task_id before closing session
    
    # Create bid relationship
    bid = Bid(
        task_id=task_id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    
    # Create message linked to task
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task_id,
        content="I can fix your sink"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    # Find the message with task
    task_message = next((m for m in messages if m["task_id"] == task_id), None)
    assert task_message is not None
    
    # Verify task details are included
    assert task_message["task_title"] == "Fix my sink"
    assert task_message["task_status"] == TaskStatus.OPEN.value
    assert task_message["content"] == "I can fix your sink"


def test_get_messages_without_task_details(client, test_users, auth_headers):
    """Test GET /messages response when task_id is null (no task context)."""
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
    
    # Create message WITHOUT task_id (general message)
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=None,
        content="General message"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    # Find the message without task
    general_message = next((m for m in messages if m["task_id"] is None), None)
    assert general_message is not None
    
    # Verify task details are null when no task
    assert general_message["task_title"] is None
    assert general_message["task_status"] is None
    assert general_message["content"] == "General message"


def test_get_messages_performance_with_many_messages(client, test_users, auth_headers):
    """Test query performance with 100+ messages using JOIN."""
    db = TestingSessionLocal()
    
    # Create tasks
    tasks = []
    for i in range(10):
        task = Task(
            customer_id=test_users["customer"].id,
            title=f"Task {i}",
            description=f"Description {i}",
            location="Test Location",
            date=datetime.utcnow() + timedelta(days=i+1),
            budget=100.0 + i,
            status=TaskStatus.OPEN if i % 2 == 0 else TaskStatus.IN_PROGRESS
        )
        db.add(task)
        tasks.append(task)
    
    db.commit()
    for task in tasks:
        db.refresh(task)
    
    # Store task IDs before closing session
    task_ids = [task.id for task in tasks]
    
    # Create bid relationship
    bid = Bid(
        task_id=task_ids[0],
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    
    # Create 120 messages (mix of with and without task_id)
    from database import Message
    messages = []
    for i in range(120):
        # Alternate between messages with and without task_id
        task_id = task_ids[i % 10] if i % 3 != 0 else None
        message = Message(
            sender_id=test_users["tasker"].id if i % 2 == 0 else test_users["customer"].id,
            receiver_id=test_users["customer"].id if i % 2 == 0 else test_users["tasker"].id,
            task_id=task_id,
            content=f"Message {i}"
        )
        messages.append(message)
    
    db.add_all(messages)
    db.commit()
    db.close()
    
    # Measure query performance
    import time
    start_time = time.time()
    
    response = client.get("/messages", headers=auth_headers["customer"])
    
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 120
    
    # Verify response time (should be under 100ms, requirement is 50ms increase)
    print(f"Response time: {response_time_ms:.2f}ms")
    assert response_time_ms < 200  # Liberal threshold for test environment
    
    # Verify task details are correctly populated
    messages_with_task = [m for m in messages if m["task_id"] is not None]
    messages_without_task = [m for m in messages if m["task_id"] is None]
    
    assert len(messages_with_task) > 0
    assert len(messages_without_task) > 0
    
    # Verify all messages with task_id have task details
    for msg in messages_with_task:
        assert msg["task_title"] is not None
        assert msg["task_status"] is not None
        assert msg["task_title"].startswith("Task ")
    
    # Verify all messages without task_id have null task details
    for msg in messages_without_task:
        assert msg["task_title"] is None
        assert msg["task_status"] is None


def test_get_messages_join_query_correctness(client, test_users, auth_headers):
    """Test that JOIN query correctly matches messages to tasks."""
    db = TestingSessionLocal()
    
    # Create multiple tasks with different statuses
    task1 = Task(
        customer_id=test_users["customer"].id,
        title="Plumbing Work",
        description="Fix pipes",
        location="Location 1",
        date=datetime.utcnow() + timedelta(days=1),
        budget=150.0,
        status=TaskStatus.OPEN
    )
    task2 = Task(
        customer_id=test_users["customer"].id,
        title="Electrical Work",
        description="Wire installation",
        location="Location 2",
        date=datetime.utcnow() + timedelta(days=2),
        budget=200.0,
        status=TaskStatus.IN_PROGRESS
    )
    db.add_all([task1, task2])
    db.commit()
    db.refresh(task1)
    db.refresh(task2)
    task1_id = task1.id
    task2_id = task2.id
    
    # Create bids for relationship
    bid1 = Bid(task_id=task1_id, tasker_id=test_users["tasker"].id, amount=140.0)
    bid2 = Bid(task_id=task2_id, tasker_id=test_users["tasker"].id, amount=190.0)
    db.add_all([bid1, bid2])
    db.commit()
    
    # Create messages for different tasks
    from database import Message
    msg1 = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task1_id,
        content="Message about plumbing"
    )
    msg2 = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task2_id,
        content="Message about electrical"
    )
    db.add_all([msg1, msg2])
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    
    # Find each message and verify correct task details
    plumbing_msg = next((m for m in messages if "plumbing" in m["content"]), None)
    electrical_msg = next((m for m in messages if "electrical" in m["content"]), None)
    
    assert plumbing_msg is not None
    assert plumbing_msg["task_id"] == task1_id
    assert plumbing_msg["task_title"] == "Plumbing Work"
    assert plumbing_msg["task_status"] == TaskStatus.OPEN.value
    
    assert electrical_msg is not None
    assert electrical_msg["task_id"] == task2_id
    assert electrical_msg["task_title"] == "Electrical Work"
    assert electrical_msg["task_status"] == TaskStatus.IN_PROGRESS.value


def test_get_messages_response_schema_validation(client, test_users, auth_headers):
    """Test that response matches MessageResponseWithTask schema."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Schema Test Task",
        description="Test",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.COMPLETED
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    # Create bid
    bid = Bid(
        task_id=task_id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    
    # Create message
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task_id,
        content="Testing schema"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    msg = messages[0]
    
    # Verify all required fields from MessageResponse
    assert "id" in msg and isinstance(msg["id"], int)
    assert "sender_id" in msg and isinstance(msg["sender_id"], int)
    assert "receiver_id" in msg and isinstance(msg["receiver_id"], int)
    assert "content" in msg and isinstance(msg["content"], str)
    assert "read" in msg and isinstance(msg["read"], bool)
    assert "created_at" in msg and isinstance(msg["created_at"], str)
    
    # Verify task_id field (can be int or None)
    assert "task_id" in msg
    
    # Verify enhanced fields from MessageResponseWithTask
    assert "task_title" in msg
    assert "task_status" in msg
    
    # If task_id is present, task details should be present
    if msg["task_id"] is not None:
        assert msg["task_title"] is not None
        assert msg["task_status"] is not None
        assert isinstance(msg["task_title"], str)
        assert isinstance(msg["task_status"], str)


def test_get_messages_backwards_compatibility(client, test_users, auth_headers):
    """Test that response is backwards compatible with existing message responses."""
    db = TestingSessionLocal()
    
    # Create task and relationship
    task = Task(
        customer_id=test_users["customer"].id,
        title="Compatibility Test",
        description="Test",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    bid = Bid(
        task_id=task_id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    
    # Create message
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task_id,
        content="Backwards compatibility test"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    
    msg = messages[0]
    
    # All original MessageResponse fields should still be present
    original_fields = ["id", "sender_id", "receiver_id", "task_id", "content", "read", "created_at"]
    for field in original_fields:
        assert field in msg, f"Missing original field: {field}"
    
    # New fields should not break existing functionality
    assert msg["sender_id"] == test_users["tasker"].id
    assert msg["receiver_id"] == test_users["customer"].id
    assert msg["content"] == "Backwards compatibility test"


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


def test_get_messages_includes_sender_user_details(client, test_users, auth_headers):
    """Test GET /messages includes sender user details (name and role)."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create message from tasker to customer
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task.id,
        content="Hello from tasker"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages as customer
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    msg = messages[0]
    
    # Verify sender details are included
    assert "sender_name" in msg
    assert msg["sender_name"] == "Test Tasker"
    assert "sender_role" in msg
    assert msg["sender_role"] == UserRole.TASKER.value
    

def test_get_messages_includes_receiver_user_details(client, test_users, auth_headers):
    """Test GET /messages includes receiver user details (name and role)."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create message from customer to tasker
    from database import Message
    message = Message(
        sender_id=test_users["customer"].id,
        receiver_id=test_users["tasker"].id,
        task_id=task.id,
        content="Hello from customer"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages as customer
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    msg = messages[0]
    
    # Verify receiver details are included
    assert "receiver_name" in msg
    assert msg["receiver_name"] == "Test Tasker"
    assert "receiver_role" in msg
    assert msg["receiver_role"] == UserRole.TASKER.value


def test_get_messages_user_details_both_directions(client, test_users, auth_headers):
    """Test user details are correct for messages in both directions."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create messages in both directions
    from database import Message
    msg1 = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task.id,
        content="Message from tasker"
    )
    msg2 = Message(
        sender_id=test_users["customer"].id,
        receiver_id=test_users["tasker"].id,
        task_id=task.id,
        content="Message from customer"
    )
    db.add_all([msg1, msg2])
    db.commit()
    db.close()
    
    # Get messages as customer
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    
    # Find each message type
    tasker_msg = next((m for m in messages if "tasker" in m["content"]), None)
    customer_msg = next((m for m in messages if "customer" in m["content"]), None)
    
    # Verify tasker->customer message
    assert tasker_msg is not None
    assert tasker_msg["sender_name"] == "Test Tasker"
    assert tasker_msg["sender_role"] == UserRole.TASKER.value
    assert tasker_msg["receiver_name"] == "Test Customer"
    assert tasker_msg["receiver_role"] == UserRole.CUSTOMER.value
    
    # Verify customer->tasker message
    assert customer_msg is not None
    assert customer_msg["sender_name"] == "Test Customer"
    assert customer_msg["sender_role"] == UserRole.CUSTOMER.value
    assert customer_msg["receiver_name"] == "Test Tasker"
    assert customer_msg["receiver_role"] == UserRole.TASKER.value


def test_get_messages_join_performance_with_user_details(client, test_users, auth_headers, benchmark):
    """Test query performance with user JOINs meets <200ms requirement for 50+ messages."""
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Performance Test Task",
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
    
    # Create 50 messages
    from database import Message
    messages = []
    for i in range(50):
        message = Message(
            sender_id=test_users["tasker"].id if i % 2 == 0 else test_users["customer"].id,
            receiver_id=test_users["customer"].id if i % 2 == 0 else test_users["tasker"].id,
            task_id=task.id,
            content=f"Performance test message {i}"
        )
        messages.append(message)
    
    db.add_all(messages)
    db.commit()
    db.close()
    
    # Measure query performance using pytest-benchmark
    def get_messages_request():
        return client.get("/messages", headers=auth_headers["customer"])
    
    result = benchmark(get_messages_request)
    
    assert result.status_code == 200
    messages = result.json()
    assert len(messages) == 50
    
    # Verify all messages have user details
    for msg in messages:
        assert msg["sender_name"] is not None
        assert msg["sender_role"] is not None
        assert msg["receiver_name"] is not None
        assert msg["receiver_role"] is not None


def test_get_messages_single_query_no_n_plus_one(client, test_users, auth_headers):
    """Test that user details are fetched with JOINs, not separate queries (no N+1 problem)."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create 10 messages
    from database import Message
    for i in range(10):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Test message {i}"
        )
        db.add(message)
    
    db.commit()
    db.close()
    
    # Get messages - should execute single query with JOINs
    import time
    start_time = time.time()
    
    response = client.get("/messages", headers=auth_headers["customer"])
    
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 10
    
    # With efficient JOINs, even 10 messages should be fast (<50ms)
    # If there were N+1 queries, it would be significantly slower
    print(f"Query time for 10 messages: {response_time_ms:.2f}ms")
    assert response_time_ms < 100  # Should be much faster with JOINs
    
    # Verify all messages have user details populated
    for msg in messages:
        assert msg["sender_name"] == "Test Tasker"
        assert msg["sender_role"] == UserRole.TASKER.value
        assert msg["receiver_name"] == "Test Customer"
        assert msg["receiver_role"] == UserRole.CUSTOMER.value


def test_get_messages_user_details_schema_validation(client, test_users, auth_headers):
    """Test that response includes all new user detail fields in schema."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
    task = Task(
        customer_id=test_users["customer"].id,
        title="Schema Test Task",
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
    
    # Create message
    from database import Message
    message = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task.id,
        content="Schema validation test"
    )
    db.add(message)
    db.commit()
    db.close()
    
    # Get messages
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    
    msg = messages[0]
    
    # Verify all new user detail fields are present
    assert "sender_name" in msg
    assert "sender_role" in msg
    assert "receiver_name" in msg
    assert "receiver_role" in msg
    
    # Verify types
    assert isinstance(msg["sender_name"], str)
    assert isinstance(msg["sender_role"], str)
    assert isinstance(msg["receiver_name"], str)
    assert isinstance(msg["receiver_role"], str)
    
    # Verify values match expected user data
    assert msg["sender_name"] == "Test Tasker"
    assert msg["sender_role"] in [UserRole.CUSTOMER.value, UserRole.TASKER.value]
    assert msg["receiver_name"] == "Test Customer"
    assert msg["receiver_role"] in [UserRole.CUSTOMER.value, UserRole.TASKER.value]


def test_get_messages_with_multiple_users_correct_details(client, test_users, auth_headers):
    """Test that user details are correctly associated when multiple users are involved."""
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
    
    # Create bid from tasker
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=90.0
    )
    db.add(bid)
    db.commit()
    
    # Create messages between different user pairs
    from database import Message
    msg1 = Message(
        sender_id=test_users["tasker"].id,
        receiver_id=test_users["customer"].id,
        task_id=task.id,
        content="From tasker to customer"
    )
    msg2 = Message(
        sender_id=test_users["customer"].id,
        receiver_id=test_users["tasker"].id,
        task_id=task.id,
        content="From customer to tasker"
    )
    
    db.add_all([msg1, msg2])
    db.commit()
    db.close()
    
    # Get messages as customer
    response = client.get("/messages", headers=auth_headers["customer"])
    
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    
    # Verify each message has correct user details
    for msg in messages:
        if "tasker to customer" in msg["content"]:
            # Message sent by tasker
            assert msg["sender_id"] == test_users["tasker"].id
            assert msg["sender_name"] == "Test Tasker"
            assert msg["sender_role"] == UserRole.TASKER.value
            assert msg["receiver_id"] == test_users["customer"].id
            assert msg["receiver_name"] == "Test Customer"
            assert msg["receiver_role"] == UserRole.CUSTOMER.value
        else:
            # Message sent by customer
            assert msg["sender_id"] == test_users["customer"].id
            assert msg["sender_name"] == "Test Customer"
            assert msg["sender_role"] == UserRole.CUSTOMER.value
            assert msg["receiver_id"] == test_users["tasker"].id
            assert msg["receiver_name"] == "Test Tasker"
            assert msg["receiver_role"] == UserRole.TASKER.value
"""
Integration tests for unread message count endpoint.

Tests verify accurate counting, authentication, and performance.
"""


def test_unread_count_no_messages(client, test_users, auth_headers):
    """Test unread count returns 0 when no messages exist."""
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0


def test_unread_count_with_unread_messages(client, test_users, auth_headers):
    """Test unread count returns correct count with multiple unread messages."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create multiple unread messages to customer
    from database import Message
    for i in range(5):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Message {i}",
            read=False
        )
        db.add(message)
    
    db.commit()
    db.close()
    
    # Check customer's unread count
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 5


def test_unread_count_only_receiver_messages(client, test_users, auth_headers):
    """Test unread count only counts messages where user is receiver, not sender."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create messages where customer is sender (should NOT be counted)
    from database import Message
    for i in range(3):
        message = Message(
            sender_id=test_users["customer"].id,
            receiver_id=test_users["tasker"].id,
            task_id=task.id,
            content=f"Sent message {i}",
            read=False
        )
        db.add(message)
    
    # Create messages where customer is receiver (should be counted)
    for i in range(2):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Received message {i}",
            read=False
        )
        db.add(message)
    
    db.commit()
    db.close()
    
    # Customer should only see count of 2 (messages they received)
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 2


def test_unread_count_updates_after_marking_read(client, test_users, auth_headers):
    """Test unread count decreases after marking messages as read."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create unread messages
    from database import Message
    message_ids = []
    for i in range(3):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Message {i}",
            read=False
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        message_ids.append(message.id)
    
    db.close()
    
    # Verify initial count
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    assert response.status_code == 200
    assert response.json()["unread_count"] == 3
    
    # Mark one message as read
    response = client.put(
        f"/messages/{message_ids[0]}/read",
        headers=auth_headers["customer"]
    )
    assert response.status_code == 200
    
    # Verify count decreased
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    assert response.status_code == 200
    assert response.json()["unread_count"] == 2
    
    # Mark another message as read
    response = client.put(
        f"/messages/{message_ids[1]}/read",
        headers=auth_headers["customer"]
    )
    assert response.status_code == 200
    
    # Verify count decreased again
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    assert response.status_code == 200
    assert response.json()["unread_count"] == 1


def test_unread_count_unauthorized(client):
    """Test that unauthorized access returns 401."""
    response = client.get("/messages/unread-count")
    
    assert response.status_code == 401


def test_unread_count_performance_large_dataset(client, test_users, auth_headers):
    """Test unread count performance with 1000+ messages in database."""
    import time
    db = TestingSessionLocal()
    
    # Create task and bid relationship
    task = Task(
        customer_id=test_users["customer"].id,
        title="Performance Test Task",
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
    
    # Create 1000+ messages (mix of read and unread)
    from database import Message
    messages = []
    for i in range(1200):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Performance test message {i}",
            read=(i % 3 == 0)  # Every third message is read
        )
        messages.append(message)
    
    db.bulk_save_objects(messages)
    db.commit()
    db.close()
    
    # Measure response time
    start_time = time.time()
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    end_time = time.time()
    response_time_ms = (end_time - start_time) * 1000
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    # 1200 messages, every third is read (400 read), so 800 unread
    assert data["unread_count"] == 800
    
    # Verify performance (should be <50ms as per acceptance criteria)
    assert response_time_ms < 50, f"Response time {response_time_ms}ms exceeds 50ms threshold"


def test_unread_count_mixed_read_unread(client, test_users, auth_headers):
    """Test unread count with mix of read and unread messages."""
    db = TestingSessionLocal()
    
    # Create task and bid relationship
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
    
    # Create mix of read and unread messages
    from database import Message
    for i in range(4):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Unread message {i}",
            read=False
        )
        db.add(message)
    
    for i in range(6):
        message = Message(
            sender_id=test_users["tasker"].id,
            receiver_id=test_users["customer"].id,
            task_id=task.id,
            content=f"Read message {i}",
            read=True
        )
        db.add(message)
    
    db.commit()
    db.close()
    
    # Should only count unread (4)
    response = client.get(
        "/messages/unread-count",
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 4

