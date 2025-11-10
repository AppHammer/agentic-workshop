"""
Integration tests for offer-based messaging workflow (v0.0.1-3-2-1).

These tests verify the complete end-to-end flow of offer-based messaging,
from offer creation through message exchange between customers and taskers.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database import Base, get_db, User, Task, Offer, Message, UserRole, TaskStatus
from auth import get_password_hash, create_access_token

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_offer_messages.db"
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
    """Create authentication headers for test users."""
    headers = {}
    for role, user in test_users.items():
        token = create_access_token(data={"sub": user.email})
        headers[role] = {"Authorization": f"Bearer {token}"}
    return headers


def test_complete_offer_workflow_customer_initiates(client, test_users, auth_headers):
    """
    Test complete workflow: Customer creates offer → sends message → tasker responds.
    
    Acceptance Criteria:
    - Customer can click "Message Tasker" on offer card and initiate conversation
    - Task context automatically associated with messages from offer cards
    """
    db = TestingSessionLocal()
    
    # Step 1: Customer creates a task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Fix Kitchen Sink",
        description="Leaky faucet needs repair",
        location="123 Main St",
        date=datetime.utcnow() + timedelta(days=2),
        budget=150.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    # Step 2: Customer creates an offer to tasker1
    offer = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker1"].id,
        amount=140.0,
        message="Are you available to fix my sink?"
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    db.close()
    
    # Step 3: Customer initiates message to tasker (simulating "Message Tasker" button click)
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker1"].id,
            "task_id": task_id,
            "content": "Hi, I sent you an offer for the sink repair. Can you start this week?"
        }
    )
    
    assert response.status_code == 200
    customer_message = response.json()
    assert customer_message["sender_id"] == test_users["customer"].id
    assert customer_message["receiver_id"] == test_users["tasker1"].id
    assert customer_message["task_id"] == task_id
    assert customer_message["content"] == "Hi, I sent you an offer for the sink repair. Can you start this week?"
    
    # Step 4: Tasker receives and responds to message
    response = client.post(
        "/messages",
        headers=auth_headers["tasker1"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Yes, I can start on Tuesday. The offer looks good!"
        }
    )
    
    assert response.status_code == 200
    tasker_message = response.json()
    assert tasker_message["sender_id"] == test_users["tasker1"].id
    assert tasker_message["receiver_id"] == test_users["customer"].id
    assert tasker_message["task_id"] == task_id
    
    # Step 5: Verify message history is maintained
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    messages = response.json()
    
    # Should have both messages
    task_messages = [m for m in messages if m["task_id"] == task_id]
    assert len(task_messages) >= 2
    
    # Verify task context is present
    for msg in task_messages:
        assert msg["task_title"] == "Fix Kitchen Sink"
        assert msg["task_status"] == TaskStatus.OPEN.value


def test_complete_offer_workflow_tasker_initiates(client, test_users, auth_headers):
    """
    Test complete workflow: Customer creates offer → tasker receives → tasker initiates message.
    
    Acceptance Criteria:
    - Tasker who received offer can message customer about that offer
    """
    db = TestingSessionLocal()
    
    # Create task and offer
    task = Task(
        customer_id=test_users["customer"].id,
        title="Install Light Fixture",
        description="Need new ceiling light installed",
        location="456 Oak Ave",
        date=datetime.utcnow() + timedelta(days=3),
        budget=200.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    offer = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker2"].id,
        amount=180.0,
        message="Can you install this light fixture?"
    )
    db.add(offer)
    db.commit()
    db.close()
    
    # Tasker initiates conversation after receiving offer
    response = client.post(
        "/messages",
        headers=auth_headers["tasker2"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Thanks for the offer! I have a few questions about the fixture type."
        }
    )
    
    assert response.status_code == 200
    message_data = response.json()
    assert message_data["sender_id"] == test_users["tasker2"].id
    assert message_data["receiver_id"] == test_users["customer"].id
    assert message_data["task_id"] == task_id
    
    # Customer responds
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker2"].id,
            "task_id": task_id,
            "content": "It's a standard LED ceiling fixture. I'll send you the model number."
        }
    )
    
    assert response.status_code == 200


def test_permission_validation_prevents_messaging_without_offer(client, test_users, auth_headers):
    """
    Test that permission validation prevents messaging without valid offer.
    
    Acceptance Criteria:
    - Permission validation prevents messaging without valid offer
    - Error messages guide users when messaging not allowed
    """
    db = TestingSessionLocal()
    
    # Create task but NO offer to other_tasker
    task = Task(
        customer_id=test_users["customer"].id,
        title="Paint Room",
        description="Need bedroom painted",
        location="789 Elm St",
        date=datetime.utcnow() + timedelta(days=4),
        budget=300.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()
    
    # Attempt to message tasker without offer relationship
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["other_tasker"].id,
            "task_id": task_id,
            "content": "Can you help with this?"
        }
    )
    
    # Should be forbidden
    assert response.status_code == 403
    error_data = response.json()
    assert "detail" in error_data
    assert "permission" in error_data["detail"].lower()
    assert "bid, offer, or agreement" in error_data["detail"]
    
    # Verify error message is user-friendly
    assert len(error_data["detail"]) > 20  # Should be descriptive


def test_multiple_offers_create_separate_conversations(client, test_users, auth_headers):
    """
    Test that multiple offers to different taskers on same task create separate conversations.
    
    Acceptance Criteria:
    - Works for multiple offers to different taskers on same task
    """
    db = TestingSessionLocal()
    
    # Create task
    task = Task(
        customer_id=test_users["customer"].id,
        title="Bathroom Renovation",
        description="Complete bathroom remodel",
        location="321 Pine St",
        date=datetime.utcnow() + timedelta(days=7),
        budget=5000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    # Create offers to multiple taskers
    offer1 = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker1"].id,
        amount=4800.0,
        message="Interested in your plumbing expertise"
    )
    
    offer2 = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker2"].id,
        amount=4900.0,
        message="Need electrical work done"
    )
    
    db.add_all([offer1, offer2])
    db.commit()
    db.close()
    
    # Message first tasker
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker1"].id,
            "task_id": task_id,
            "content": "Can you handle the plumbing portion?"
        }
    )
    assert response.status_code == 200
    
    # Message second tasker
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker2"].id,
            "task_id": task_id,
            "content": "Can you handle the electrical work?"
        }
    )
    assert response.status_code == 200
    
    # Both taskers respond
    response = client.post(
        "/messages",
        headers=auth_headers["tasker1"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Yes, I can handle all plumbing"
        }
    )
    assert response.status_code == 200
    
    response = client.post(
        "/messages",
        headers=auth_headers["tasker2"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Yes, I specialize in bathroom electrical"
        }
    )
    assert response.status_code == 200
    
    # Verify customer can see all messages
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    messages = response.json()
    
    # Filter messages for this task
    task_messages = [m for m in messages if m["task_id"] == task_id]
    assert len(task_messages) >= 4
    
    # Verify distinct conversations with each tasker
    tasker1_messages = [m for m in task_messages if 
                       m["sender_id"] == test_users["tasker1"].id or 
                       m["receiver_id"] == test_users["tasker1"].id]
    tasker2_messages = [m for m in task_messages if 
                       m["sender_id"] == test_users["tasker2"].id or 
                       m["receiver_id"] == test_users["tasker2"].id]
    
    assert len(tasker1_messages) >= 2
    assert len(tasker2_messages) >= 2


def test_offer_decline_messages_remain_accessible(client, test_users, auth_headers):
    """
    Test that message history is preserved even if offer is declined.
    
    Acceptance Criteria:
    - Message history preserved even if offer is declined
    """
    db = TestingSessionLocal()
    
    # Create task and offer
    task = Task(
        customer_id=test_users["customer"].id,
        title="Garden Landscaping",
        description="Backyard landscaping project",
        location="555 Maple Dr",
        date=datetime.utcnow() + timedelta(days=5),
        budget=1000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    offer = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker1"].id,
        amount=950.0,
        message="Can you do the landscaping?",
        accepted=False  # Explicitly not accepted
    )
    db.add(offer)
    db.commit()
    offer_id = offer.id
    db.close()
    
    # Exchange messages while offer is pending
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker1"].id,
            "task_id": task_id,
            "content": "Let me know if the offer works for you"
        }
    )
    assert response.status_code == 200
    message1_id = response.json()["id"]
    
    response = client.post(
        "/messages",
        headers=auth_headers["tasker1"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "I need to check my schedule first"
        }
    )
    assert response.status_code == 200
    message2_id = response.json()["id"]
    
    # Simulate offer decline (tasker doesn't accept)
    # The offer remains in database but not accepted
    
    # Verify messages are still accessible
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    messages = response.json()
    
    # Find our messages
    our_messages = [m for m in messages if m["id"] in [message1_id, message2_id]]
    assert len(our_messages) == 2
    
    # Both messages should still be retrievable
    assert all(m["task_id"] == task_id for m in our_messages)
    
    # Verify both can still message (offer still exists, even if not accepted)
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker1"].id,
            "task_id": task_id,
            "content": "Thanks anyway, maybe next time"
        }
    )
    assert response.status_code == 200


def test_task_context_automatically_associated(client, test_users, auth_headers):
    """
    Test that task context is automatically associated with messages from offer cards.
    
    Acceptance Criteria:
    - Task context automatically associated with messages from offer cards
    """
    db = TestingSessionLocal()
    
    # Create task and offer
    task = Task(
        customer_id=test_users["customer"].id,
        title="Roof Repair",
        description="Fix leaking roof",
        location="999 Cedar Ln",
        date=datetime.utcnow() + timedelta(days=1),
        budget=2000.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    offer = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker1"].id,
        amount=1800.0,
        message="Can you fix the roof?"
    )
    db.add(offer)
    db.commit()
    db.close()
    
    # Send message with task_id (as would happen from "Message Tasker" button)
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker1"].id,
            "task_id": task_id,  # Task ID from offer card
            "content": "When can you inspect the roof?"
        }
    )
    
    assert response.status_code == 200
    message_data = response.json()
    
    # Verify task context is associated
    assert message_data["task_id"] == task_id
    
    # Retrieve messages and verify task details are included
    response = client.get("/messages", headers=auth_headers["customer"])
    assert response.status_code == 200
    messages = response.json()
    
    message = next(m for m in messages if m["id"] == message_data["id"])
    assert message["task_id"] == task_id
    assert message["task_title"] == "Roof Repair"
    assert message["task_status"] == TaskStatus.OPEN.value


def test_bidirectional_messaging_with_offer(client, test_users, auth_headers):
    """
    Test that both customer and tasker can initiate and respond to messages when offer exists.
    """
    db = TestingSessionLocal()
    
    # Create task and offer
    task = Task(
        customer_id=test_users["customer"].id,
        title="Appliance Repair",
        description="Fix washing machine",
        location="111 Birch Ct",
        date=datetime.utcnow() + timedelta(days=2),
        budget=250.0,
        status=TaskStatus.OPEN
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    
    offer = Offer(
        task_id=task_id,
        customer_id=test_users["customer"].id,
        tasker_id=test_users["tasker2"].id,
        amount=230.0,
        message="Can you fix it?"
    )
    db.add(offer)
    db.commit()
    db.close()
    
    # Customer initiates
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker2"].id,
            "task_id": task_id,
            "content": "Customer message 1"
        }
    )
    assert response.status_code == 200
    
    # Tasker responds
    response = client.post(
        "/messages",
        headers=auth_headers["tasker2"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Tasker response 1"
        }
    )
    assert response.status_code == 200
    
    # Tasker initiates new thread
    response = client.post(
        "/messages",
        headers=auth_headers["tasker2"],
        json={
            "receiver_id": test_users["customer"].id,
            "task_id": task_id,
            "content": "Tasker message 2"
        }
    )
    assert response.status_code == 200
    
    # Customer responds again
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["tasker2"].id,
            "task_id": task_id,
            "content": "Customer response 2"
        }
    )
    assert response.status_code == 200


def test_error_message_quality_without_offer(client, test_users, auth_headers):
    """
    Test that error messages properly guide users when messaging is not allowed.
    
    Acceptance Criteria:
    - Error messages guide users when messaging not allowed
    """
    # Try to message without any relationship
    response = client.post(
        "/messages",
        headers=auth_headers["customer"],
        json={
            "receiver_id": test_users["other_tasker"].id,
            "content": "Hello there"
        }
    )
    
    assert response.status_code == 403
    error = response.json()
    
    # Verify error message contains helpful information
    assert "detail" in error
    error_msg = error["detail"].lower()
    
    # Should mention what's needed
    assert "bid" in error_msg or "offer" in error_msg or "agreement" in error_msg
    assert "permission" in error_msg
    
    # Should be descriptive (not just "Forbidden")
    assert len(error["detail"]) > 30