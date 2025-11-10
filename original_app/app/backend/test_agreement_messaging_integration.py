"""
Integration tests for agreement-based messaging workflow (v0.0.1-3-3-1).

These tests verify the complete end-to-end flow of agreement-based messaging,
from agreement creation through task completion, ensuring messages persist
throughout the entire lifecycle.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database import Base, get_db, User, Task, Agreement, Message, UserRole, TaskStatus, AgreementStatus
from auth import get_password_hash, create_access_token

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_agreement_messages.db"
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
    """Create test users (customer and taskers)."""
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
        skills="Plumbing",
        hourly_rate=50.0
    )
    
    other_customer = User(
        email="other_customer@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Other Customer",
        role=UserRole.CUSTOMER,
        location="Test City"
    )
    
    other_tasker = User(
        email="other_tasker@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Other Tasker",
        role=UserRole.TASKER,
        location="Test City",
        skills="Electrical",
        hourly_rate=60.0
    )
    
    db.add_all([customer, tasker, other_customer, other_tasker])
    db.commit()
    db.refresh(customer)
    db.refresh(tasker)
    db.refresh(other_customer)
    db.refresh(other_tasker)
    
    users = {
        "customer": customer,
        "tasker": tasker,
        "other_customer": other_customer,
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


def test_customer_messages_tasker_after_agreement_creation(client, test_users, auth_headers):
    """
    Test: Customer can message tasker once agreement is created
    
    Verifies that:
    - Customer can send messages to tasker after agreement exists
    - Task context is automatically associated
    - Messages are properly stored and retrievable
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Fix leaky pipe",
        description="Need urgent repair",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=150.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement (pending status)
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=150.0,
        status=AgreementStatus.PENDING
    )
    db.add(agreement)
    db.commit()
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Customer sends message to tasker
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task_id,
        "content": "When can you start the repair work?"
    }
    
    response = client.post(
        "/messages",
        json=message_data,
        headers=auth_headers["customer"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "When can you start the repair work?"
    assert data["sender_id"] == test_users["customer"].id
    assert data["receiver_id"] == test_users["tasker"].id
    assert data["task_id"] == task_id
    
    # Verify tasker can retrieve the message
    response = client.get("/messages", headers=auth_headers["tasker"])
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    assert any(m["content"] == "When can you start the repair work?" for m in messages)


def test_tasker_messages_customer_after_agreement_accepted(client, test_users, auth_headers):
    """
    Test: Tasker can message customer once agreement is accepted
    
    Verifies that:
    - Tasker can send messages after accepting agreement
    - Bidirectional messaging works
    - Task context is maintained
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Install ceiling fan",
        description="Need installation",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=2),
        budget=200.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create accepted agreement
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=200.0,
        status=AgreementStatus.ACCEPTED
    )
    db.add(agreement)
    db.commit()
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Tasker sends message to customer
    message_data = {
        "receiver_id": test_users["customer"].id,
        "task_id": task_id,
        "content": "I can start tomorrow morning at 9 AM"
    }
    
    response = client.post(
        "/messages",
        json=message_data,
        headers=auth_headers["tasker"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "I can start tomorrow morning at 9 AM"
    assert data["sender_id"] == test_users["tasker"].id
    assert data["receiver_id"] == test_users["customer"].id
    assert data["task_id"] == task_id


def test_messaging_works_across_all_agreement_statuses(client, test_users, auth_headers):
    """
    Test: Messaging works for all agreement statuses (pending, accepted, completed)
    
    Verifies that:
    - Messages can be sent during pending status
    - Messages can be sent during accepted status
    - Messages can be sent even after completion
    - Message history persists across status changes
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Paint living room",
        description="Need painting service",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=3),
        budget=300.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement with PENDING status
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=300.0,
        status=AgreementStatus.PENDING
    )
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    
    # Store IDs before any session changes
    task_id = task.id
    agreement_id = agreement.id
    
    # Message during PENDING status
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task_id,
        "content": "Please confirm you can complete by Friday"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Change to ACCEPTED status
    agreement.status = AgreementStatus.ACCEPTED
    db.commit()
    db.close()
    db = TestingSessionLocal()
    
    # Message during ACCEPTED status
    message_data = {
        "receiver_id": test_users["customer"].id,
        "task_id": task_id,
        "content": "Yes, I'll finish by Friday afternoon"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["tasker"])
    assert response.status_code == 200
    
    # Change to COMPLETED status
    agreement = db.query(Agreement).filter(Agreement.task_id == task_id).first()
    agreement.status = AgreementStatus.COMPLETED
    agreement.completed_at = datetime.utcnow()
    db.commit()
    db.close()
    
    # Message after COMPLETED status
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task_id,
        "content": "Great work! Thank you!"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Verify all messages are retrievable
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    messages = response.json()
    
    # Should have at least 2 messages from customer
    customer_messages = [m for m in messages if m["sender_id"] == test_users["customer"].id]
    assert len(customer_messages) >= 2


def test_task_context_automatically_associated(client, test_users, auth_headers):
    """
    Test: Task context automatically associated with agreement messages
    
    Verifies that:
    - Messages include task_id when sent in agreement context
    - Task information is retrievable through message
    - Context is maintained throughout conversation
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Garden landscaping",
        description="Need landscaping work",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=5),
        budget=500.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=500.0,
        status=AgreementStatus.ACCEPTED
    )
    db.add(agreement)
    db.commit()
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Send message with task context
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task_id,
        "content": "What plants do you recommend?"
    }
    
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    message = response.json()
    assert message["task_id"] == task_id
    assert message["content"] == "What plants do you recommend?"
    
    # Verify task association persists when retrieving messages
    response = client.get("/messages", headers=auth_headers["tasker"])
    assert response.status_code == 200
    messages = response.json()
    
    relevant_message = next(
        (m for m in messages if m["content"] == "What plants do you recommend?"),
        None
    )
    assert relevant_message is not None
    assert relevant_message["task_id"] == task_id


def test_message_history_persists_after_completion(client, test_users, auth_headers):
    """
    Test: Message history persists after agreement completion
    
    Verifies that:
    - Messages remain accessible after task is completed
    - Complete conversation history is maintained
    - Both parties can still access old messages
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="House cleaning",
        description="Deep cleaning needed",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=250.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create agreement
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=250.0,
        status=AgreementStatus.ACCEPTED
    )
    db.add(agreement)
    db.commit()
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Exchange messages before completion
    messages_to_send = [
        ("customer", "tasker", "What time will you arrive?"),
        ("tasker", "customer", "I'll be there at 10 AM"),
        ("customer", "tasker", "Perfect, see you then")
    ]
    
    for sender_role, receiver_role, content in messages_to_send:
        message_data = {
            "receiver_id": test_users[receiver_role].id,
            "task_id": task_id,
            "content": content
        }
        response = client.post("/messages", json=message_data, headers=auth_headers[sender_role])
        assert response.status_code == 200
    
    # Mark agreement as completed
    db = TestingSessionLocal()
    agreement = db.query(Agreement).filter(Agreement.task_id == task_id).first()
    agreement.status = AgreementStatus.COMPLETED
    agreement.completed_at = datetime.utcnow()
    task_obj = db.query(Task).filter(Task.id == task_id).first()
    task_obj.status = TaskStatus.COMPLETED
    db.commit()
    db.close()
    
    # Send post-completion message
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task_id,
        "content": "Excellent work, everything looks great!"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Verify all messages are still accessible
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    customer_messages = response.json()
    
    # Should have all 4 messages in conversation
    conversation_messages = [
        m for m in customer_messages
        if m["task_id"] == task_id
    ]
    assert len(conversation_messages) >= 4
    
    # Verify tasker can also access
    response = client.get("/messages", headers=auth_headers["tasker"])
    assert response.status_code == 200
    tasker_messages = response.json()
    
    conversation_messages = [
        m for m in tasker_messages
        if m["task_id"] == task_id
    ]
    assert len(conversation_messages) >= 4


def test_complete_agreement_workflow_with_messaging(client, test_users, auth_headers):
    """
    Test: Complete workflow - Create agreement → Exchange messages → Complete task → Messages still accessible
    
    Verifies the entire end-to-end flow:
    - Agreement creation enables messaging
    - Messages exchanged during active work
    - Task completion doesn't affect message access
    - Both parties retain full conversation history
    """
    db = TestingSessionLocal()
    
    # Step 1: Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Roof repair",
        description="Fix leaking roof",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=7),
        budget=1000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Step 2: Create agreement (simulating acceptance of work)
    agreement = Agreement(
        task_id=task.id,
        tasker_id=test_users["tasker"].id,
        amount=1000.0,
        status=AgreementStatus.ACCEPTED
    )
    db.add(agreement)
    db.commit()
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Step 3: Exchange messages during work
    workflow_messages = [
        ("customer", "tasker", "When can you inspect the roof?"),
        ("tasker", "customer", "I can come today at 2 PM"),
        ("customer", "tasker", "That works for me"),
        ("tasker", "customer", "Inspection complete, found the leak source"),
        ("customer", "tasker", "Great! How long will the repair take?"),
        ("tasker", "customer", "Should be done in 3 days"),
        ("tasker", "customer", "Work is complete, roof is fixed")
    ]
    
    for sender_role, receiver_role, content in workflow_messages:
        message_data = {
            "receiver_id": test_users[receiver_role].id,
            "task_id": task_id,
            "content": content
        }
        response = client.post("/messages", json=message_data, headers=auth_headers[sender_role])
        assert response.status_code == 200, f"Failed to send: {content}"
    
    # Step 4: Complete the task
    db = TestingSessionLocal()
    agreement = db.query(Agreement).filter(Agreement.task_id == task_id).first()
    agreement.status = AgreementStatus.COMPLETED
    agreement.completed_at = datetime.utcnow()
    task_obj = db.query(Task).filter(Task.id == task_id).first()
    task_obj.status = TaskStatus.COMPLETED
    db.commit()
    db.close()
    
    # Step 5: Verify messages still accessible after completion
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    customer_messages = response.json()
    
    task_conversation = [m for m in customer_messages if m["task_id"] == task_id]
    assert len(task_conversation) == 7, "All workflow messages should be accessible"
    
    # Step 6: Verify both parties see the same conversation
    response = client.get("/messages", headers=auth_headers["tasker"])
    assert response.status_code == 200
    tasker_messages = response.json()
    
    tasker_conversation = [m for m in tasker_messages if m["task_id"] == task_id]
    assert len(tasker_conversation) == 7, "Tasker should see same conversation"
    
    # Verify specific messages are present
    message_contents = [m["content"] for m in task_conversation]
    assert "When can you inspect the roof?" in message_contents
    assert "Work is complete, roof is fixed" in message_contents


def test_permission_validation_without_agreement(client, test_users, auth_headers):
    """
    Test: Permission validation prevents messaging without agreement
    
    Verifies that:
    - Users cannot message without an agreement
    - Proper error messages are returned
    - Unauthorized messaging attempts are rejected
    """
    db = TestingSessionLocal()
    
    # Create task WITHOUT creating an agreement
    task = Task(
        customer_id=test_users["customer"].id,
        title="Random task",
        description="No agreement exists",
        location="Test Location",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Store IDs before closing session
    task_id = task.id
    db.close()
    
    # Attempt to send message without agreement
    message_data = {
        "receiver_id": test_users["other_tasker"].id,
        "task_id": task_id,
        "content": "Can we discuss this task?"
    }
    
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    
    # Should be forbidden without agreement
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_multiple_agreements_separate_conversations(client, test_users, auth_headers):
    """
    Test: Multiple agreements create separate message contexts
    
    Verifies that:
    - Different agreements maintain separate conversations
    - Task context properly distinguishes between agreements
    - Messages don't mix between different tasks
    """
    db = TestingSessionLocal()
    
    # Create two separate tasks
    task1 = Task(
        customer_id=test_users["customer"].id,
        title="Task One",
        description="First task",
        location="Location 1",
        date=datetime.utcnow() + timedelta(days=1),
        budget=100.0,
        status=TaskStatus.OPEN
    )
    
    task2 = Task(
        customer_id=test_users["customer"].id,
        title="Task Two",
        description="Second task",
        location="Location 2",
        date=datetime.utcnow() + timedelta(days=2),
        budget=200.0,
        status=TaskStatus.OPEN
    )
    
    db.add_all([task1, task2])
    db.commit()
    db.refresh(task1)
    db.refresh(task2)
    
    # Create agreements for both tasks with same tasker
    agreement1 = Agreement(
        task_id=task1.id,
        tasker_id=test_users["tasker"].id,
        amount=100.0,
        status=AgreementStatus.ACCEPTED
    )
    
    agreement2 = Agreement(
        task_id=task2.id,
        tasker_id=test_users["tasker"].id,
        amount=200.0,
        status=AgreementStatus.ACCEPTED
    )
    
    db.add_all([agreement1, agreement2])
    db.commit()
    
    # Store IDs before closing session
    task1_id = task1.id
    task2_id = task2.id
    db.close()
    
    # Send messages for task 1
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task1_id,
        "content": "Message about task one"
    }
    response = client.post("/messages", json=message_data, headers=auth_headers["customer"])
    assert response.status_code == 200
    
    # Send messages for task 2
    message_data = {
        "receiver_id": test_users["tasker"].id,
        "task_id": task2_id,
        "content": "Message about task two"
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
    assert task1_messages[0]["content"] == "Message about task one"
    assert task2_messages[0]["content"] == "Message about task two"