# Feature Request: Messaging System for Tasker-Customer Communication

**Date:** 2025-11-05
**Status:** Draft

---

## 1. Summary

The Messaging System enables bidirectional communication between customers and taskers throughout the task lifecycle. Customers can message any tasker who has bid on or received an offer for their task to ask questions before making an agreement, and both parties can continue messaging after an agreement is reached to coordinate task details and share information.

## 2. The Why (Problem Statement)

Currently, users face the following challenges:

* **Communication Barrier Before Agreement:** Customers cannot ask questions to clarify tasker capabilities, availability, or approach before accepting a bid or making an offer, leading to potential mismatches and unsatisfactory agreements.
* **No Coordination Channel After Agreement:** Once an agreement is made, customers and taskers lack a direct communication channel within the platform to coordinate logistics, share updates, or resolve issues, forcing them to use external communication methods.
* **Lack of Context in Messages:** The existing basic messaging implementation doesn't provide adequate context about which task the conversation relates to, making it difficult to track multiple ongoing conversations.
* **Poor Message Discovery:** Customers cannot easily identify which taskers are available to message (those who bid or received offers) for a specific task, requiring manual tracking outside the system.

This leads to decreased platform engagement, increased external communication (emails, phone calls), reduced agreement success rates, and lower user satisfaction as the platform fails to provide a complete end-to-end experience for task coordination.

## 3. Proposed Solution

We propose enhancing the existing Messaging System to provide comprehensive communication capabilities throughout the task lifecycle. This feature will allow users to:

* **User Story 1:** As a customer, I want to message any tasker who has bid on my task, so that I can ask clarifying questions before making a hiring decision.

* **User Story 2:** As a customer, I want to message any tasker I've sent an offer to, so that I can communicate expectations and answer their questions.

* **User Story 3:** As a tasker, I want to message customers whose tasks I've bid on, so that I can provide additional information about my qualifications or approach.

* **User Story 4:** As a customer with an active agreement, I want to message the assigned tasker, so that I can coordinate logistics, share details, and answer questions during task execution.

* **User Story 5:** As a tasker with an active agreement, I want to message the customer, so that I can ask clarifying questions, provide updates, and coordinate task completion details.

* **User Story 6:** As a user, I want to see all my message conversations organized by task context, so that I can easily track communications across multiple tasks and agreements.

**Functional Details:**

* **Pre-Agreement Messaging:** Customers can initiate messages with any tasker who has placed a bid on their task or received an offer from them. Taskers can reply to these messages and initiate conversations with customers whose tasks they've bid on.

* **Post-Agreement Messaging:** Once an agreement is established, both the customer and tasker can freely message each other with enhanced context about the specific task.

* **Message Threading:** Messages are organized by conversation partner and optionally grouped by task, allowing users to view message history in a chronological thread.

* **Unread Indicators:** Display unread message counts per conversation to help users prioritize their responses.

* **Message Read Status:** Automatically mark messages as read when viewed, with visual indicators for message status.

* **Task Context Integration:** Link messages to specific tasks where applicable, allowing users to navigate from task details to relevant conversations.

* **User Identification:** Display user names (and roles) in conversation lists to clearly identify conversation partners.

* **Polling-Based Updates:** Messages refresh periodically through polling (no real-time WebSocket required for MVP).

## 4. User Value

This feature will provide value to our users by:

* **Saving Time:** Users can communicate directly within the platform without switching to external communication channels (email, phone), reducing friction and context-switching overhead.

* **Reducing Errors:** Clear task context prevents miscommunication about which task or agreement is being discussed, especially when users manage multiple simultaneous tasks.

* **Providing New Capabilities:** 
  - Customers can make more informed hiring decisions by asking questions before committing to an agreement
  - Taskers can better showcase their expertise and approach through pre-agreement conversations
  - Both parties can efficiently coordinate task details without leaving the platform

* **Improving Usability:** 
  - Organized conversation threads make it easy to track multiple ongoing discussions
  - Unread indicators help users prioritize which conversations need attention
  - Task-linked messages provide context for conversations when managing multiple tasks

## 5. Business Value

This feature supports our business goals in the following ways:

* **Customer Retention:** By providing seamless communication throughout the task lifecycle, users are more likely to remain active on the platform rather than conducting business externally. Expected 15-20% reduction in churn for active users by improving platform stickiness.

* **Increased Revenue:** Better pre-agreement communication leads to higher agreement conversion rates (estimated 10-15% increase) as customers gain confidence in their selection. Additionally, keeping all communication on-platform reduces agreement abandonment.

* **Operational Efficiency:** 
  - Reduces support ticket volume related to "how do I contact this tasker" questions (estimated 25% reduction in contact-related support tickets)
  - Provides audit trail for dispute resolution, reducing investigation time
  - Enables platform monitoring of communication quality for safety and trust

* **Competitive Advantage:** Most task marketplace platforms only offer post-agreement messaging. Pre-agreement Q&A capability differentiates the Tasker Platform and improves marketplace efficiency, providing a competitive edge over platforms like TaskRabbit.

## 6. Impact on Existing Features

### Enhances:

* **Task Detail View:** Add a "Message Tasker" button for customers viewing details of tasks with bids or offers, enabling quick access to communication with interested taskers.

* **Bid/Offer Management:** Integrate messaging CTAs directly into bid and offer cards, allowing customers to ask questions without leaving the bidding interface.

* **Agreement Management:** Enhanced with direct messaging links to facilitate ongoing coordination between customers and taskers during task execution.

* **User Dashboard:** Display unread message counts and recent message previews to increase engagement and response rates.

### Changes:

* **Messages Component:** Requires significant updates to support task-specific message filtering, improved conversation organization, and better user identification (displaying names and roles instead of just user IDs).

* **Backend API:** Existing message endpoints need enhancement to:
  - Filter messages by task context
  - Validate messaging permissions based on bid/offer/agreement relationships
  - Return enriched message data including user details and task context
  - Support task-specific message queries

* **Navigation:** Add "Messages" entry to main navigation with unread badge indicator for better discoverability.

* **Task List View:** Optionally display message indicators for tasks with active conversations.

### Deprecates:

* None - This feature enhances existing messaging rather than replacing any current functionality.

## 7. Metrics for Success

We will measure the success of this messaging feature through the following metrics:

**Adoption Metrics:**
* **Messaging Adoption Rate:** Percentage of tasks with at least one message exchanged → Target: 40% within first month
* **Pre-Agreement Messages per Task:** Average number of messages exchanged before agreement → Target: 2-3 messages
* **Post-Agreement Messages per Task:** Average number of messages exchanged after agreement → Target: 3-5 messages

**Engagement Metrics:**
* **Message Response Rate:** Percentage of messages that receive a response within 24 hours → Target: 70%
* **Average Response Time:** Time between message sent and first response → Target: <4 hours
* **Messages per User per Week:** Average messaging activity per active user → Target: 5-10 messages

**Business Impact Metrics:**
* **Agreement Conversion Rate:** Percentage of tasks with pre-agreement messages that result in agreements → Track for 20% improvement vs. no-message baseline
* **Agreement Completion Rate:** Percentage of agreements with messaging that reach completion → Target: 85%+
* **Support Ticket Reduction:** Decrease in "how do I contact" support tickets → Target: 25% reduction

**User Satisfaction Metrics:**
* **Feature Satisfaction Score:** User rating of messaging feature usefulness → Target: 4.0+ out of 5.0
* **Net Promoter Score Impact:** Correlation between messaging usage and NPS → Track for positive correlation

**Technical Metrics:**
* **Message Delivery Success Rate:** Percentage of messages successfully delivered → Target: 99.5%+
* **Page Load Time Impact:** Messaging feature shouldn't increase dashboard load time by more than 200ms

## 8. Mockups / Design Links (Optional)

To be created - recommend wireframes showing:
1. Task detail page with "Message Tasker" CTA for bidders/offer recipients
2. Enhanced Messages component with task context filtering
3. Message thread view with task information header
4. Unread message indicators in navigation and dashboard