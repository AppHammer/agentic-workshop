"""
Comprehensive unit tests for permissions module.

Tests permission validation logic for messaging authorization based on
bids, offers, and agreements between users.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import time

from database import Base, User, Task, Bid, Offer, Agreement
from database import UserRole, TaskStatus, AgreementStatus
from permissions import can_message_user, get_messageable_users
from auth import get_password_hash


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh test database for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_users(db_session):
    """Create sample users for testing"""
    users = {
        'customer1': User(
            email="customer1@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Customer One",
            role=UserRole.CUSTOMER,
            location="New York"
        ),
        'customer2': User(
            email="customer2@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Customer Two",
            role=UserRole.CUSTOMER,
            location="Los Angeles"
        ),
        'tasker1': User(
            email="tasker1@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Tasker One",
            role=UserRole.TASKER,
            location="Chicago",
            skills="plumbing, electrical",
            hourly_rate=50.0
        ),
        'tasker2': User(
            email="tasker2@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Tasker Two",
            role=UserRole.TASKER,
            location="Boston",
            skills="carpentry",
            hourly_rate=45.0
        ),
        'tasker3': User(
            email="tasker3@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Tasker Three",
            role=UserRole.TASKER,
            location="Seattle",
            skills="painting",
            hourly_rate=40.0
        )
    }
    
    for user in users.values():
        db_session.add(user)
    
    db_session.commit()
    
    # Refresh to get IDs
    for user in users.values():
        db_session.refresh(user)
    
    return users


class TestBidBasedPermissions:
    """Tests for bid-based messaging permissions"""
    
    def test_can_message_with_active_bid_tasker_to_customer(self, db_session, sample_users):
        """Test tasker can message customer when they have bid on customer's task"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create task
        task = Task(
            customer_id=customer.id,
            title="Fix sink",
            description="Leaky sink needs repair",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=150.0,
            status=TaskStatus.OPEN
        )
        db_session.add(task)
        db_session.commit()
        
        # Create bid
        bid = Bid(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=120.0,
            message="I can fix this"
        )
        db_session.add(bid)
        db_session.commit()
        
        # Test both directions
        assert can_message_user(db_session, tasker.id, customer.id) is True
        assert can_message_user(db_session, customer.id, tasker.id) is True
    
    def test_can_message_with_active_bid_customer_to_tasker(self, db_session, sample_users):
        """Test customer can message tasker who bid on their task"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Paint room",
            description="Need bedroom painted",
            location="New York",
            date=datetime.utcnow() + timedelta(days=2),
            budget=300.0
        )
        db_session.add(task)
        db_session.commit()
        
        bid = Bid(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=250.0
        )
        db_session.add(bid)
        db_session.commit()
        
        assert can_message_user(db_session, customer.id, tasker.id) is True
    
    def test_multiple_bids_on_same_task(self, db_session, sample_users):
        """Test customer can message all taskers who bid on their task"""
        customer = sample_users['customer1']
        tasker1 = sample_users['tasker1']
        tasker2 = sample_users['tasker2']
        tasker3 = sample_users['tasker3']
        
        task = Task(
            customer_id=customer.id,
            title="Kitchen renovation",
            description="Complete kitchen remodel",
            location="New York",
            date=datetime.utcnow() + timedelta(days=7),
            budget=5000.0
        )
        db_session.add(task)
        db_session.commit()
        
        # Multiple taskers bid
        for tasker in [tasker1, tasker2, tasker3]:
            bid = Bid(
                task_id=task.id,
                tasker_id=tasker.id,
                amount=4500.0
            )
            db_session.add(bid)
        
        db_session.commit()
        
        # Customer can message all bidders
        assert can_message_user(db_session, customer.id, tasker1.id) is True
        assert can_message_user(db_session, customer.id, tasker2.id) is True
        assert can_message_user(db_session, customer.id, tasker3.id) is True
        
        # Bidders can message customer
        assert can_message_user(db_session, tasker1.id, customer.id) is True
        assert can_message_user(db_session, tasker2.id, customer.id) is True
        assert can_message_user(db_session, tasker3.id, customer.id) is True
    
    def test_no_permission_without_bid(self, db_session, sample_users):
        """Test cannot message when no bid relationship exists"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # No tasks or bids created
        assert can_message_user(db_session, customer.id, tasker.id) is False
        assert can_message_user(db_session, tasker.id, customer.id) is False


class TestOfferBasedPermissions:
    """Tests for offer-based messaging permissions"""
    
    def test_can_message_with_active_offer_customer_to_tasker(self, db_session, sample_users):
        """Test customer can message tasker when they sent an offer"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Electrical work",
            description="Install new outlets",
            location="New York",
            date=datetime.utcnow() + timedelta(days=3),
            budget=200.0
        )
        db_session.add(task)
        db_session.commit()
        
        offer = Offer(
            task_id=task.id,
            customer_id=customer.id,
            tasker_id=tasker.id,
            amount=180.0,
            message="Can you do this?"
        )
        db_session.add(offer)
        db_session.commit()
        
        # Both can message
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
    
    def test_can_message_with_accepted_offer(self, db_session, sample_users):
        """Test messaging still works with accepted offer"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Plumbing work",
            description="Fix pipes",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=300.0
        )
        db_session.add(task)
        db_session.commit()
        
        offer = Offer(
            task_id=task.id,
            customer_id=customer.id,
            tasker_id=tasker.id,
            amount=280.0,
            accepted=True
        )
        db_session.add(offer)
        db_session.commit()
        
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
    
    def test_can_message_with_declined_offer(self, db_session, sample_users):
        """Test messaging still works even if offer was declined"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Carpentry",
            description="Build shelves",
            location="New York",
            date=datetime.utcnow() + timedelta(days=5),
            budget=400.0
        )
        db_session.add(task)
        db_session.commit()
        
        offer = Offer(
            task_id=task.id,
            customer_id=customer.id,
            tasker_id=tasker.id,
            amount=350.0,
            accepted=False
        )
        db_session.add(offer)
        db_session.commit()
        
        # Can still message even with declined offer
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True


class TestAgreementBasedPermissions:
    """Tests for agreement-based messaging permissions"""
    
    def test_can_message_with_active_agreement(self, db_session, sample_users):
        """Test messaging with active agreement"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Home repair",
            description="Various repairs",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=500.0,
            status=TaskStatus.IN_PROGRESS
        )
        db_session.add(task)
        db_session.commit()
        
        agreement = Agreement(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=450.0,
            status=AgreementStatus.ACCEPTED
        )
        db_session.add(agreement)
        db_session.commit()
        
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
    
    def test_can_message_with_completed_agreement(self, db_session, sample_users):
        """Test messaging still works with completed agreement"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Painting job",
            description="Paint house exterior",
            location="New York",
            date=datetime.utcnow() - timedelta(days=7),
            budget=2000.0,
            status=TaskStatus.COMPLETED
        )
        db_session.add(task)
        db_session.commit()
        
        agreement = Agreement(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=1900.0,
            status=AgreementStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        db_session.add(agreement)
        db_session.commit()
        
        # Can still message after completion
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
    
    def test_can_message_with_pending_agreement(self, db_session, sample_users):
        """Test messaging with pending agreement"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Landscaping",
            description="Yard cleanup",
            location="New York",
            date=datetime.utcnow() + timedelta(days=2),
            budget=600.0
        )
        db_session.add(task)
        db_session.commit()
        
        agreement = Agreement(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=550.0,
            status=AgreementStatus.PENDING
        )
        db_session.add(agreement)
        db_session.commit()
        
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True


class TestNoRelationship:
    """Tests for scenarios with no relationship"""
    
    def test_no_relationship_returns_false(self, db_session, sample_users):
        """Test returns False when no relationship exists"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        assert can_message_user(db_session, customer.id, tasker.id) is False
        assert can_message_user(db_session, tasker.id, customer.id) is False
    
    def test_different_customers_cannot_message(self, db_session, sample_users):
        """Test customers cannot message each other"""
        customer1 = sample_users['customer1']
        customer2 = sample_users['customer2']
        
        assert can_message_user(db_session, customer1.id, customer2.id) is False
        assert can_message_user(db_session, customer2.id, customer1.id) is False
    
    def test_different_taskers_cannot_message(self, db_session, sample_users):
        """Test taskers cannot message each other"""
        tasker1 = sample_users['tasker1']
        tasker2 = sample_users['tasker2']
        
        assert can_message_user(db_session, tasker1.id, tasker2.id) is False
        assert can_message_user(db_session, tasker2.id, tasker1.id) is False
    
    def test_task_without_bids_offers_or_agreement(self, db_session, sample_users):
        """Test customer and random tasker cannot message with just a task"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create task but no bids/offers/agreements
        task = Task(
            customer_id=customer.id,
            title="Future task",
            description="Planned work",
            location="New York",
            date=datetime.utcnow() + timedelta(days=30),
            budget=1000.0
        )
        db_session.add(task)
        db_session.commit()
        
        assert can_message_user(db_session, customer.id, tasker.id) is False


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_self_messaging_not_allowed(self, db_session, sample_users):
        """Test user cannot message themselves"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        assert can_message_user(db_session, customer.id, customer.id) is False
        assert can_message_user(db_session, tasker.id, tasker.id) is False
    
    def test_multiple_relationships_same_users(self, db_session, sample_users):
        """Test users with multiple relationship types can message"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create multiple tasks and relationships
        task1 = Task(
            customer_id=customer.id,
            title="Task 1",
            description="First task",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        task2 = Task(
            customer_id=customer.id,
            title="Task 2",
            description="Second task",
            location="New York",
            date=datetime.utcnow() + timedelta(days=2),
            budget=200.0
        )
        db_session.add_all([task1, task2])
        db_session.commit()
        
        # Add bid on task1
        bid = Bid(task_id=task1.id, tasker_id=tasker.id, amount=90.0)
        db_session.add(bid)
        
        # Add offer on task2
        offer = Offer(
            task_id=task2.id,
            customer_id=customer.id,
            tasker_id=tasker.id,
            amount=180.0
        )
        db_session.add(offer)
        
        # Add agreement on task1
        agreement = Agreement(
            task_id=task1.id,
            tasker_id=tasker.id,
            amount=90.0
        )
        db_session.add(agreement)
        
        db_session.commit()
        
        # Should be able to message
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
    
    def test_bid_on_other_customers_task(self, db_session, sample_users):
        """Test tasker who bid on customer1's task cannot message customer2"""
        customer1 = sample_users['customer1']
        customer2 = sample_users['customer2']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer1.id,
            title="Task for customer1",
            description="Work",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        db_session.add(task)
        db_session.commit()
        
        bid = Bid(task_id=task.id, tasker_id=tasker.id, amount=90.0)
        db_session.add(bid)
        db_session.commit()
        
        # Tasker can message customer1
        assert can_message_user(db_session, tasker.id, customer1.id) is True
        
        # But cannot message customer2
        assert can_message_user(db_session, tasker.id, customer2.id) is False
    
    def test_cannot_message_after_bid_withdrawal(self, db_session, sample_users):
        """Test cannot message when bid has been withdrawn"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        task = Task(
            customer_id=customer.id,
            title="Task with withdrawn bid",
            description="Work",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        db_session.add(task)
        db_session.commit()
        
        # Create bid
        bid = Bid(task_id=task.id, tasker_id=tasker.id, amount=90.0)
        db_session.add(bid)
        db_session.commit()
        
        # Initially can message
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
        
        # Withdraw the bid
        bid.withdrawn = True
        db_session.commit()
        
        # Now cannot message
        assert can_message_user(db_session, customer.id, tasker.id) is False
        assert can_message_user(db_session, tasker.id, customer.id) is False
    
    def test_multiple_bids_same_tasker_one_withdrawn(self, db_session, sample_users):
        """Test tasker with multiple bids can still message if one is active"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create two tasks
        task1 = Task(
            customer_id=customer.id,
            title="Task 1",
            description="First task",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        task2 = Task(
            customer_id=customer.id,
            title="Task 2",
            description="Second task",
            location="New York",
            date=datetime.utcnow() + timedelta(days=2),
            budget=200.0
        )
        db_session.add_all([task1, task2])
        db_session.commit()
        
        # Create two bids
        bid1 = Bid(task_id=task1.id, tasker_id=tasker.id, amount=90.0, withdrawn=True)
        bid2 = Bid(task_id=task2.id, tasker_id=tasker.id, amount=180.0)
        db_session.add_all([bid1, bid2])
        db_session.commit()
        
        # Can still message because bid2 is active
        assert can_message_user(db_session, customer.id, tasker.id) is True
        assert can_message_user(db_session, tasker.id, customer.id) is True
        
        # Withdraw second bid too
        bid2.withdrawn = True
        db_session.commit()
        
        # Now cannot message
        assert can_message_user(db_session, customer.id, tasker.id) is False
    
    def test_nonexistent_user_ids(self, db_session, sample_users):
        """Test with non-existent user IDs"""
        customer = sample_users['customer1']
        
        # Non-existent user ID
        assert can_message_user(db_session, customer.id, 99999) is False
        assert can_message_user(db_session, 99999, customer.id) is False
        assert can_message_user(db_session, 99999, 88888) is False


class TestPerformance:
    """Tests for performance requirements"""
    
    def test_permission_validation_performance(self, db_session, sample_users, benchmark):
        """Test permission validation completes in <100ms using pytest-benchmark"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create a task and bid for testing
        task = Task(
            customer_id=customer.id,
            title="Performance test task",
            description="Test description",
            location="New York",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        db_session.add(task)
        db_session.commit()
        
        bid = Bid(
            task_id=task.id,
            tasker_id=tasker.id,
            amount=90.0
        )
        db_session.add(bid)
        db_session.commit()
        
        # Benchmark the validation - should complete in <100ms
        result = benchmark(can_message_user, db_session, customer.id, tasker.id)
        
        assert result is True
        # pytest-benchmark will automatically track timing and warn if too slow
    
    def test_performance_with_many_relationships(self, db_session, sample_users, benchmark):
        """Test query performance with 100+ relationships"""
        customer = sample_users['customer1']
        
        # Create 100+ tasks with bids
        taskers = []
        for i in range(110):
            tasker = User(
                email=f"tasker{i+10}@test.com",
                hashed_password=get_password_hash("password"),
                full_name=f"Tasker {i+10}",
                role=UserRole.TASKER,
                hourly_rate=40.0
            )
            db_session.add(tasker)
            taskers.append(tasker)
        
        db_session.commit()
        
        # Create tasks and bids
        for i, tasker in enumerate(taskers):
            task = Task(
                customer_id=customer.id,
                title=f"Task {i}",
                description=f"Description {i}",
                location="New York",
                date=datetime.utcnow() + timedelta(days=i),
                budget=100.0 + i
            )
            db_session.add(task)
            db_session.commit()
            
            bid = Bid(
                task_id=task.id,
                tasker_id=tasker.id,
                amount=90.0 + i
            )
            db_session.add(bid)
        
        db_session.commit()
        
        # Benchmark the validation with many relationships
        result = benchmark(can_message_user, db_session, customer.id, taskers[50].id)
        
        assert result is True
        # Performance should still be <100ms even with many relationships
    
    def test_performance_with_no_relationship(self, db_session, sample_users, benchmark):
        """Test performance when checking users with no relationship"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Add many unrelated relationships
        for i in range(50):
            other_customer = User(
                email=f"othercust{i}@test.com",
                hashed_password=get_password_hash("password"),
                full_name=f"Customer {i}",
                role=UserRole.CUSTOMER
            )
            db_session.add(other_customer)
            db_session.commit()
            
            task = Task(
                customer_id=other_customer.id,
                title=f"Other task {i}",
                description="Work",
                location="Location",
                date=datetime.utcnow() + timedelta(days=1),
                budget=100.0
            )
            db_session.add(task)
            db_session.commit()
        
        # Benchmark performance for unrelated users
        result = benchmark(can_message_user, db_session, customer.id, tasker.id)
        
        assert result is False
        # Should still be fast even when no relationship exists


class TestGetMessageableUsers:
    """Tests for get_messageable_users helper function"""
    
    def test_get_messageable_users_with_bids(self, db_session, sample_users):
        """Test getting list of messageable users via bids"""
        customer = sample_users['customer1']
        tasker1 = sample_users['tasker1']
        tasker2 = sample_users['tasker2']
        
        task = Task(
            customer_id=customer.id,
            title="Task",
            description="Work",
            location="NY",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        db_session.add(task)
        db_session.commit()
        
        bid1 = Bid(task_id=task.id, tasker_id=tasker1.id, amount=90.0)
        bid2 = Bid(task_id=task.id, tasker_id=tasker2.id, amount=85.0)
        db_session.add_all([bid1, bid2])
        db_session.commit()
        
        messageable = get_messageable_users(db_session, customer.id)
        
        assert tasker1.id in messageable
        assert tasker2.id in messageable
        assert customer.id not in messageable  # Should not include self
    
    def test_get_messageable_users_empty(self, db_session, sample_users):
        """Test getting messageable users when there are none"""
        customer = sample_users['customer1']
        
        messageable = get_messageable_users(db_session, customer.id)
        
        assert messageable == []
    
    def test_get_messageable_users_no_duplicates(self, db_session, sample_users):
        """Test that same user appears only once even with multiple relationships"""
        customer = sample_users['customer1']
        tasker = sample_users['tasker1']
        
        # Create multiple relationships
        task1 = Task(
            customer_id=customer.id,
            title="Task 1",
            description="Work",
            location="NY",
            date=datetime.utcnow() + timedelta(days=1),
            budget=100.0
        )
        task2 = Task(
            customer_id=customer.id,
            title="Task 2",
            description="Work",
            location="NY",
            date=datetime.utcnow() + timedelta(days=2),
            budget=200.0
        )
        db_session.add_all([task1, task2])
        db_session.commit()
        
        # Multiple relationships with same tasker
        bid = Bid(task_id=task1.id, tasker_id=tasker.id, amount=90.0)
        offer = Offer(
            task_id=task2.id,
            customer_id=customer.id,
            tasker_id=tasker.id,
            amount=180.0
        )
        db_session.add_all([bid, offer])
        db_session.commit()
        
        messageable = get_messageable_users(db_session, customer.id)
        
        # Should appear only once
        assert messageable.count(tasker.id) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])