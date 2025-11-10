"""
Permission validation module for messaging authorization.

This module provides permission checks to determine if users can message
each other based on their relationships through bids, offers, or agreements.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database import User, Task, Bid, Offer, Agreement
from typing import Optional


def can_message_user(
    db: Session, 
    sender_id: int, 
    receiver_id: int
) -> bool:
    """
    Checks if sender has permission to message receiver based on task relationships.
    
    Users can message each other if they have any of the following relationships:
    1. Active agreement (tasker working on customer's task)
    2. Bid (tasker bid on customer's task)
    3. Offer (customer sent offer to tasker or vice versa)
    
    Args:
        db: Database session
        sender_id: User ID of message sender
        receiver_id: User ID of message receiver
        
    Returns:
        True if messaging is allowed, False otherwise
        
    Examples:
        >>> can_message_user(db, customer_id=1, tasker_id=2)
        True  # if tasker 2 has bid on customer 1's task
        
    Performance:
        - Uses optimized queries with JOINs
        - Short-circuits on first match (returns immediately)
        - Expected execution time < 100ms
    """
    
    # Prevent messaging yourself
    if sender_id == receiver_id:
        return False
    
    # Check for active agreements (both directions)
    # Agreement connects a tasker to a customer's task
    agreement = db.query(Agreement).join(Task).filter(
        or_(
            # Sender is tasker, receiver is customer
            and_(
                Agreement.tasker_id == sender_id,
                Task.customer_id == receiver_id
            ),
            # Sender is customer, receiver is tasker
            and_(
                Agreement.tasker_id == receiver_id,
                Task.customer_id == sender_id
            )
        )
    ).first()
    
    if agreement:
        return True
    
    # Check for bids (tasker bid on customer's task, bidirectional)
    # Bid connects a tasker to a customer's task
    # Only active (non-withdrawn) bids count
    bid = db.query(Bid).join(Task).filter(
        Bid.withdrawn == False,
        or_(
            # Sender is tasker who bid, receiver is task owner (customer)
            and_(
                Bid.tasker_id == sender_id,
                Task.customer_id == receiver_id
            ),
            # Sender is task owner (customer), receiver is tasker who bid
            and_(
                Bid.tasker_id == receiver_id,
                Task.customer_id == sender_id
            )
        )
    ).first()
    
    if bid:
        return True
    
    # Check for offers (customer sent offer to tasker, bidirectional)
    # Offer connects a customer to a tasker for a specific task
    offer = db.query(Offer).filter(
        or_(
            # Sender is customer who made offer, receiver is tasker
            and_(
                Offer.customer_id == sender_id,
                Offer.tasker_id == receiver_id
            ),
            # Sender is tasker, receiver is customer who made offer
            and_(
                Offer.customer_id == receiver_id,
                Offer.tasker_id == sender_id
            )
        )
    ).first()
    
    if offer:
        return True
    
    # No relationship found - messaging not allowed
    return False


def get_messageable_users(db: Session, user_id: int) -> list[int]:
    """
    Get list of user IDs that the specified user can message.
    
    This is useful for populating message recipient dropdowns or
    validating bulk messaging operations.
    
    Args:
        db: Database session
        user_id: User ID to find messageable users for
        
    Returns:
        List of user IDs that can be messaged
    """
    messageable_ids = set()
    
    # Get users from agreements (as tasker or customer)
    agreements_as_tasker = db.query(Task.customer_id).join(
        Agreement, Agreement.task_id == Task.id
    ).filter(Agreement.tasker_id == user_id).all()
    
    agreements_as_customer = db.query(Agreement.tasker_id).join(
        Task, Agreement.task_id == Task.id
    ).filter(Task.customer_id == user_id).all()
    
    messageable_ids.update(uid[0] for uid in agreements_as_tasker)
    messageable_ids.update(uid[0] for uid in agreements_as_customer)
    
    # Get users from bids (as tasker or task owner)
    # Only include non-withdrawn bids
    bids_as_tasker = db.query(Task.customer_id).join(
        Bid, Bid.task_id == Task.id
    ).filter(Bid.tasker_id == user_id, Bid.withdrawn == False).all()
    
    bids_as_customer = db.query(Bid.tasker_id).join(
        Task, Bid.task_id == Task.id
    ).filter(Task.customer_id == user_id, Bid.withdrawn == False).all()
    
    messageable_ids.update(uid[0] for uid in bids_as_tasker)
    messageable_ids.update(uid[0] for uid in bids_as_customer)
    
    # Get users from offers (as customer or tasker)
    offers_as_customer = db.query(Offer.tasker_id).filter(
        Offer.customer_id == user_id
    ).all()
    
    offers_as_tasker = db.query(Offer.customer_id).filter(
        Offer.tasker_id == user_id
    ).all()
    
    messageable_ids.update(uid[0] for uid in offers_as_customer)
    messageable_ids.update(uid[0] for uid in offers_as_tasker)
    
    # Remove self if present
    messageable_ids.discard(user_id)
    
    return list(messageable_ids)