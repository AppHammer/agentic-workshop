"""
Integration tests for bid-based messaging workflow (v0.0.1-3-1-1).

These tests verify the complete end-to-end flow of bid-based messaging,
from bid placement through message exchange between customers and taskers.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database import Base, get_db, User, Task, Bid, Message, UserRole, TaskStatus
from auth import get_password_hash, create_access_token

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_bid_messages.db"
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
    """Create test users (customer and multiple taskers)."""
    db = TestingSessionLocal()
    
    customer = User(
        email="customer@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Customer",
        role=UserRole.CUSTOMER,
        location="Test City"
    )
    
    tasker1 = User(
        email="tasker1@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Tasker One",
        role=UserRole.TASKER,
        location="Test City",
        skills="Plumbing",
        hourly_rate=50.0
    )
    
    tasker2 = User(
        email="tasker2@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Tasker Two",
        role=UserRole.TASKER,
        location="Test City",
        skills="Electrical",
        hourly_rate=60.0
    )
    
    other_tasker = User(
        email="other_tasker@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Other Tasker",
        role=UserRole.TASKER,
        location="Test City",
        skills="Carpentry",
        hourly_rate=45.0
    )
    
    db.add_all([customer, tasker1, tasker2, other_tasker])
    db.commit()
    db.refresh(customer)
    db.refresh(tasker1)
    db.refresh(tasker2)
    db.refresh(other_tasker)
    
    users = {
        "customer": customer,
        "tasker1": tasker1,
        "tasker2": tasker2,
        "other_tasker": other_tasker
    }
    
    db.close()
    return users


@pytest.fixture
def auth_headers(test_users):
    """Generate authentication headers for test users."""
    headers = {}
    for role, user in test_users.items():
        token = create_access_token(data={"sub": user.email})
        headers[role] = {"Authorization": f"Bearer {token}"}
    return headers


def test_customer_messages_tasker_with_bid(client, test_users, auth_headers):
    """
    Test: Customer can click "Message Tasker" on bid card and initiate conversation
    
    Verifies that:
    - Customer can message tasker who placed a bid
    - Task context is automatically associated
    - Message is created successfully
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Fix leaky faucet",
        description="Need plumber",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Tasker places bid
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker1"].id,
        amount=90.0,
        message="I can fix this for you",
        withdrawn=False
    )
    db.add(bid)
    db.commit()
    
    task_id = task.id
    db.close()
    
    # Customer sends message to tasker (from bid card)
    message_data = {
        "receiver_id": test_users["tasker1"].id,
        "task_id": task_id,
        "content": "Your bid looks good. Can you start tomorrow?"
    }
    
    response = client.post(
        "/messages",
        json=message_data,
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Your bid looks good. Can you start tomorrow?"
    assert data["sender_id"] == test_users["customer"].id
    assert data["receiver_id"] == test_users["tasker1"].id
    assert data["task_id"] == task_id
    
    # Verify tasker can retrieve the message
    response = client.get("/messages", headers=auth_headers["tasker1"])
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    assert any(m["content"] == "Your bid looks good. Can you start tomorrow?" for m in messages)


def test_tasker_messages_customer_about_bid(client, test_users, auth_headers):
    """
    Test: Tasker who placed bid can message customer about that task
    
    Verifies that:
    - Tasker can initiate message to customer
    - Bidirectional messaging works
    - Task context is maintained
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Paint bedroom",
        description="Need painter",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=2),
        budget=200.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Tasker places bid
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker1"].id,
        amount=180.0,
        message="Professional painting service",
        withdrawn=False
    )
    db.add(bid)
    db.commit()
    
    task_id = task.id
    db.close()
    
    # Tasker sends message to customer
    message_data = {
        "receiver_id": test_users["customer"].id,
        "task_id": task_id,
        "content": "I have some questions about the project scope"
    }
    
    response = client.post(
        "/messages",
        json=message_data,
        headers=auth_headers["tasker1"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "I have some questions about the project scope"
    assert data["sender_id"] == test_users["tasker1"].id
    assert data["receiver_id"] == test_users["customer"].id
    assert data["task_id"] == task_id


def test_permission_validation_without_bid(client, test_users, auth_headers):
    """
    Test: Permission validation prevents messaging without valid bid
    
    Verifies that:
    - Users cannot message without a bid relationship
    - Proper error messages are returned
    - Security is enforced
    """
    db = TestingSessionLocal()
    
    # Create task (no bid placed)
    task = Task(
        customer_id=test_users["customer"].id,
        title="Random task",
        description="No bid exists",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    task_id = task.id
    db.close()
    
    # Attempt to send message without bid
    message_data = {
        "receiver_id": test_users["other_tasker"].id,
        "task_id": task_id,
        "content": "Can we discuss this task?"
    }
    
    response = client.post(
        "/messages",
        json=message_data,
        headers=auth_headers["customer"]
    )
    
    # Should be forbidden without bid
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_message_history_preserved_after_bid_withdrawal(client, test_users, auth_headers):
    """
    Test: Message history preserved even if bid is withdrawn
    
    Verifies that:
    - Messages remain accessible after bid withdrawal
    - Conversation history is maintained
    - Users can still view past messages
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Lawn mowing",
        description="Weekly service",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=3),
        budget=50.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Tasker places bid
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker1"].id,
        amount=45.0,
        message="Weekly lawn care service",
        withdrawn=False
    )
    db.add(bid)
    db.commit()
    
    task_id = task.id
    bid_id = bid.id
    db.close()
    
    # Exchange messages before withdrawal
    messages_to_send = [
        ("customer", "tasker1", "When can you start?"),
        ("tasker1", "customer", "I can start next Monday"),
        ("customer", "tasker1", "That works for me")
    ]
    
    for sender_role, receiver_role, content in messages_to_send:
        message_data = {
            "receiver_id": test_users[receiver_role].id,
            "task_id": task_id,
            "content": content
        }
        response = client.post("/messages", json=message_data, headers=auth_headers[sender_role])
        assert response.status_code == 200
    
    # Withdraw the bid
    db = TestingSessionLocal()
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    bid.withdrawn = True
    db.commit()
    db.close()
    
    # Verify messages are still accessible
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    customer_messages = response.json()
    
    conversation_messages = [m for m in customer_messages if m["task_id"] == task_id]
    assert len(conversation_messages) >= 3
    
    # Verify tasker can also access
    response = client.get("/messages", headers=auth_headers["tasker1"])
    assert response.status_code == 200
    tasker_messages = response.json()
    
    conversation_messages = [m for m in tasker_messages if m["task_id"] == task_id]
    assert len(conversation_messages) >= 3


def test_complete_bid_workflow_with_messaging(client, test_users, auth_headers):
    """
    Test: Complete workflow - Place bid → Message customer → Customer responds
    
    Verifies the entire end-to-end flow:
    - Bid placement enables messaging
    - Both parties can communicate
    - Full conversation history is maintained
    """
    db = TestingSessionLocal()
    
    # Step 1: Customer creates task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Bathroom renovation",
        description="Complete remodel",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=7),
        budget=5000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Step 2: Tasker places bid
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker1"].id,
        amount=4800.0,
        message="Experienced in bathroom renovations",
        withdrawn=False
    )
    db.add(bid)
    db.commit()
    
    task_id = task.id
    db.close()
    
    # Step 3: Exchange messages about the bid
    workflow_messages = [
        ("tasker1", "customer", "I'd like to discuss the project scope"),
        ("customer", "tasker1", "Sure, what questions do you have?"),
        ("tasker1", "customer", "Are you providing the materials or should I source them?"),
        ("customer", "tasker1", "I'll provide materials. Can you start next week?"),
        ("tasker1", "customer", "Yes, I can start Monday")
    ]
    
    for sender_role, receiver_role, content in workflow_messages:
        message_data = {
            "receiver_id": test_users[receiver_role].id,
            "task_id": task_id,
            "content": content
        }
        response = client.post("/messages", json=message_data, headers=auth_headers[sender_role])
        assert response.status_code == 200, f"Failed to send: {content}"
    
    # Step 4: Verify complete conversation exists
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    customer_messages = response.json()
    
    task_conversation = [m for m in customer_messages if m["task_id"] == task_id]
    assert len(task_conversation) == 5, "All workflow messages should be present"
    
    # Verify both parties see the same conversation
    response = client.get("/messages", headers=auth_headers["tasker1"])
    assert response.status_code == 200
    tasker_messages = response.json()
    
    tasker_conversation = [m for m in tasker_messages if m["task_id"] == task_id]
    assert len(tasker_conversation) == 5, "Tasker should see same conversation"
    
    # Verify specific messages are present
    message_contents = [m["content"] for m in task_conversation]
    assert "I'd like to discuss the project scope" in message_contents
    assert "Yes, I can start Monday" in message_contents


def test_multiple_bids_separate_conversations(client, test_users, auth_headers):
    """
    Test: Works for multiple bids from same tasker on different tasks
    
    Verifies that:
    - Same tasker can bid on multiple tasks
    - Each bid creates separate conversation context
    - Messages don't mix between different tasks
    """
    db = TestingSessionLocal()
    
    # Create two separate tasks
    task1 = Task(
        customer_id=test_users["customer"].id,
        title="Task One - Plumbing",
        description="Fix pipes",
        location="Location 1",
        date=datetime.utcnow() + timedelta(days=1),
        budget=150.0,
        status=TaskStatus.OPEN
    )
    
    task2 = Task(
        customer_id=test_users["customer"].id,
        title="Task Two - Electrical",
        description="Install outlets",
        location="Location 2",
        date=datetime.utcnow() + timedelta(days=2),
        budget=200.0,
        status=TaskStatus.OPEN
    )
    
    db.add_all([task1, task2])
    db.commit()
    db.refresh(task1)
    db.refresh(task2)
    
    # Same tasker bids on both tasks
    bid1 = Bid(
        task_id=task1.id,
        tasker_id=test_users["tasker1"].id,
        amount=140.0,
        message="Can handle plumbing",
        withdrawn=False
    )
    
    bid2 = Bid(
        task_id=task2.id,
        tasker_id=test_users["tasker1"].id,
        amount=190.0,
        message="Licensed electrician",
        withdrawn=False
    )
    
    db.add_all([bid1, bid2])
    db.commit()
    
    task1_id = task1.id
    task2_id = task2.id
    db.close()
    
    # Send messages for task 1
    message_data = {
        "receiver_id": test_users["tasker1"].id,
        "task_id": task1_id,
        "content": "Message about plumbing task"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Send messages for task 2
    message_data = {
        "receiver_id": test_users["tasker1"].id,
        "task_id": task2_id,
        "content": "Message about electrical task"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Verify messages are properly separated by task context
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    all_messages = response.json()
    
    task1_messages = [m for m in all_messages if m["task_id"] == task1_id]
    task2_messages = [m for m in all_messages if m["task_id"] == task2_id]
    
    assert len(task1_messages) >= 1
    assert len(task2_messages) >= 1
    assert task1_messages[0]["content"] == "Message about plumbing task"
    assert task2_messages[0]["content"] == "Message about electrical task"


def test_task_context_automatically_associated(client, test_users, auth_headers):
    """
    Test: Task context automatically associated with messages from bid cards
    
    Verifies that:
    - Task ID is automatically associated with messages
    - Context is preserved throughout conversation
    - Task information is queryable
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Deck building",
        description="Build outdoor deck",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=10),
        budget=3000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Tasker places bid
    bid = Bid(
        task_id=task.id,
        tasker_id=test_users["tasker1"].id,
        amount=2800.0,
        message="Deck specialist",
        withdrawn=False
    )
    db.add(bid)
    db.commit()
    
    task_id = task.id
    db.close()
    
    # Send message with task context
    message_data = {
        "receiver_id": test_users["tasker1"].id,
        "task_id": task_id,
        "content": "What type of wood do you recommend?"
    }
    
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    message = response.json()
    assert message["task_id"] == task_id
    assert message["content"] == "What type of wood do you recommend?"
    
    # Verify task association persists when retrieving messages
    response = client.get("/messages", headers=auth_headers["tasker1"])
    assert response.status_code == 200
    messages = response.json()
    
    relevant_message = next(
        (m for m in messages if m["content"] == "What type of wood do you recommend?"),
        None
    )
    assert relevant_message is not None
    assert relevant_message["task_id"] == task_id


def test_error_messages_guide_users(client, test_users, auth_headers):
    """
    Test: Error messages guide users when messaging not allowed
    
    Verifies that:
    - Clear error messages are provided
    - Users understand why messaging is blocked
    - Error responses are helpful and actionable
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Test task",
        description="For error testing",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    task_id = task.id
    db.close()
    
    # Attempt to message without bid (should fail with helpful error)
    message_data = {
        "receiver_id": test_users["tasker1"].id,
        "task_id": task_id,
        "content": "Can we discuss?"
    }
    
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    
    assert response.status_code == 403
    error_detail = response.json()["detail"].lower()
    
    # Error should mention permission or authorization
    assert any(keyword in error_detail for keyword in ["permission", "not allowed", "forbidden", "authorized"])
    
    # Error should be actionable and clear
    assert len(error_detail) > 10  # Not just a generic "Forbidden"