# Pub/Sub Messaging Skill - RabbitMQ + Redis

Production-grade publish/subscribe patterns. RabbitMQ (pika) + Redis (redis-py). Based on usermanagement_api battle-tested implementation.

## Table of Contents

1. [Overview](#overview)
2. [Technologies](#technologies)
3. [Three Publish Patterns](#three-publish-patterns)
4. [RabbitMQ vs Redis](#rabbitmq-vs-redis)
5. [Quick Start](#quick-start)
6. [Examples](#examples)

---

## Overview

**Three distinct publish patterns** for different use cases:

1. **`publish_event`** — Event-driven (pub/sub, many consumers)
2. **`publish_to_queue`** — Work queue (point-to-point, load balanced)
3. **`publish_to_exchange`** — Advanced routing (topic, fanout, headers)

## Technologies

### RabbitMQ (Message Queue)
- **Library:** `pika==1.3.2`
- **Protocol:** AMQP 0.9.1
- **Use For:** Guaranteed delivery, durability, complex routing
- **Exchange Types:** topic, direct, fanout, headers

### Redis (Cache & Pub/Sub)
- **Library:** `redis==5.0.1`
- **Use For:** Real-time messaging, caching, fast operations
- **Patterns:** pub/sub, channels, key-value

## Three Publish Patterns

### 1. `publish_event()` — Event-Driven Pattern

**When:** Domain events (user.created, order.placed, payment.completed)

**Characteristics:**
- Standard event format with metadata
- Topic exchange (pattern matching)
- Multiple consumers listening
- Persistent messages

```python
from pubsub import get_publisher

publisher = get_publisher("rabbitmq")

# Publish domain event
publisher.publish_event(
    event_type="user.created",
    payload={
        "user_id": "123",
        "email": "user@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    },
    routing_key="users.signup"
)
```

**Message Format:**
```json
{
  "event_type": "user.created",
  "timestamp": "2024-01-01T00:00:00Z",
  "payload": {
    "user_id": "123",
    "email": "user@example.com"
  }
}
```

### 2. `publish_to_queue()` — Work Queue Pattern

**When:** Background jobs (send email, resize image, generate PDF)

**Characteristics:**
- Direct queue, no exchange routing
- Single consumer processes task
- Load balancing across workers
- One-time processing

```python
publisher = get_publisher("rabbitmq")

# Send task to worker queue
publisher.publish_to_queue(
    queue="email_tasks",
    message={
        "to": "user@example.com",
        "subject": "Welcome",
        "body": "Welcome to our platform"
    },
    persistent=True
)
```

**Message Format:**
```json
{
  "to": "user@example.com",
  "subject": "Welcome",
  "body": "Welcome to our platform"
}
```

### 3. `publish_to_exchange()` — Advanced Routing Pattern

**When:** Complex routing (topic patterns, fanout, priority)

**Characteristics:**
- Full routing control
- Multiple binding patterns
- Supports all exchange types
- Custom headers

```python
publisher = get_publisher("rabbitmq")

# Topic exchange with pattern routing
publisher.publish_to_exchange(
    exchange="notifications",
    routing_key="notifications.user.123.sms",
    message={
        "user_id": "123",
        "message": "Your order shipped",
        "channel": "sms"
    },
    headers={"priority": "high"}
)

# Fanout broadcast
publisher.publish_to_exchange(
    exchange="announcements",
    message={"announcement": "Maintenance in 5 min"},
    exchange_type="fanout"
)
```

## RabbitMQ vs Redis

| Feature | RabbitMQ | Redis |
|---------|----------|-------|
| **Persistence** | ✅ Durable (survives restart) | ❌ In-memory (requires RDB/AOF) |
| **Guarantee** | ✅ At-least-once delivery | ⚠️ Best-effort |
| **Routing** | ✅ Complex (exchanges, patterns) | ⚠️ Simple (channels) |
| **Speed** | ⚠️ Slower (persistent) | ✅ Faster (in-memory) |
| **Scalability** | ✅ Clusters | ✅ Clusters |
| **Use Case** | Critical tasks, orders, payments | Real-time, notifications, caching |

**Choose RabbitMQ for:**
- Critical business events
- Must-never-lose messages
- Complex routing needed
- Task distribution

**Choose Redis for:**
- Real-time updates
- High throughput
- Notifications
- Cache alongside pub/sub

## Quick Start

### Install Dependencies

```bash
pip install pika redis
```

### RabbitMQ Connection

```python
from pubsub.rabbitmq import RabbitMQConnection

# Connection manager with auto-reconnect
conn = RabbitMQConnection(
    url="amqp://guest:guest@localhost:5672//"
)

# Check connection
if conn.is_connected():
    print("✅ Connected to RabbitMQ")
else:
    conn.connect()
```

### Publish Events

```python
from pubsub import get_publisher

publisher = get_publisher("rabbitmq")

# Event pattern
publisher.publish_event(
    event_type="user.registered",
    payload={"user_id": "123", "email": "test@example.com"}
)

# Queue pattern
publisher.publish_to_queue(
    queue="emails",
    message={"to": "test@example.com", "subject": "Welcome"}
)

# Exchange routing
publisher.publish_to_exchange(
    exchange="events",
    routing_key="user.events.new",
    message={"user_id": "123"}
)
```

### Subscribe to Events

```python
from pubsub.rabbitmq import RabbitMQConsumer

consumer = RabbitMQConsumer(connection_url="amqp://...")

# Define callback
def handle_user_created(message):
    print(f"New user: {message['payload']['email']}")

# Subscribe to pattern
consumer.subscribe(
    exchange="user_management_events",
    routing_key="user.created",
    queue="user_service_queue",
    callback=handle_user_created
)

# Start listening
consumer.start()
```

## Examples

### Scenario 1: New User Registration

```python
# Publisher (API Service)
from pubsub import get_publisher

publisher = get_publisher("rabbitmq")

@app.post("/auth/register")
async def register(data: RegisterRequest):
    # Create user
    user = await db.users.create(data)
    
    # Publish event (triggers multiple services)
    publisher.publish_event(
        event_type="user.registered",
        payload={
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    )
    
    return {"status": "registered", "user_id": user.id}

# Subscriber 1: Email Service
def on_user_registered(message):
    send_welcome_email(message['payload']['email'])

consumer1.subscribe(
    exchange="user_management_events",
    routing_key="user.registered",
    callback=on_user_registered,
    queue="email_service_queue"
)

# Subscriber 2: Analytics Service
def on_user_registered_analytics(message):
    log_registration_event(message['payload']['user_id'])

consumer2.subscribe(
    exchange="user_management_events",
    routing_key="user.registered",
    callback=on_user_registered_analytics,
    queue="analytics_service_queue"
)
```

### Scenario 2: Background Task Processing

```python
# Publisher (Main Service)
publisher = get_publisher("rabbitmq")

@app.post("/orders/{order_id}/invoice")
async def generate_invoice(order_id: str):
    # Send to worker queue
    publisher.publish_to_queue(
        queue="pdf_generation",
        message={
            "type": "invoice",
            "order_id": order_id,
            "priority": "normal"
        },
        persistent=True
    )
    
    return {"status": "processing"}

# Subscriber: PDF Worker
consumer = RabbitMQConsumer()

def generate_pdf_task(message):
    order_id = message['order_id']
    pdf_data = create_invoice_pdf(order_id)
    save_to_s3(f"invoices/{order_id}.pdf", pdf_data)
    print(f"Invoice generated: {order_id}")

consumer.subscribe_queue(
    queue="pdf_generation",
    callback=generate_pdf_task,
    workers=3  # 3 parallel workers
)

consumer.start()
```

### Scenario 3: Real-Time Notifications (Redis)

```python
from pubsub.redis import RedisPublisher, RedisSubscriber

# Publisher
redis_pub = RedisPublisher(redis_client)

@app.post("/notifications/send")
async def send_notification(user_id: str, message: str):
    redis_pub.publish(
        channel=f"user:{user_id}:notifications",
        message={"text": message, "timestamp": datetime.now()}
    )
    return {"status": "sent"}

# Subscriber (WebSocket)
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    redis_sub = RedisSubscriber(redis_client)
    
    async def listen_for_notifications():
        async for message in redis_sub.subscribe(f"user:{user_id}:notifications"):
            await websocket.send_json(message)
    
    await listen_for_notifications()
```

## Best Practices

### 1. Message Persistence
```python
# Critical data - always persistent
publisher.publish_to_queue(
    queue="critical_tasks",
    message={"data": "important"},
    persistent=True
)

# Non-critical - can be transient
publisher.publish_to_queue(
    queue="notifications",
    message={"alert": "info"},
    persistent=False
)
```

### 2. Error Handling
```python
from pubsub.exceptions import PublishError

try:
    publisher.publish_event(
        event_type="payment.completed",
        payload={"payment_id": "123"}
    )
except PublishError as e:
    logger.error(f"Failed to publish: {e}")
    # Fallback: save to database, retry later
    await db.failed_events.create(e.payload)
```

### 3. Naming Conventions
```python
# Events (past tense, domain.entity.action)
user.created
user.updated
user.deleted
order.placed
payment.completed

# Queues (task type)
email_tasks
pdf_generation
image_processing
notification_tasks

# Routing Keys (hierarchical)
users.signup
users.account.deleted
orders.status.confirmed
payments.method.stripe
```

### 4. Message Structure
```python
# ✅ Good - Structured, versioned
{
  "event_type": "user.created",
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "payload": {
    "user_id": "123",
    "email": "test@example.com"
  },
  "metadata": {
    "source": "api",
    "correlation_id": "abc-123"
  }
}

# ❌ Bad - Unstructured
{
  "type": "new_user",
  "id": "123",
  "email": "test@example.com"
}
```

### 5. Idempotent Consumers
```python
async def handle_payment_event(message):
    payment_id = message['payload']['payment_id']
    
    # Check if already processed
    if await db.payments.get(payment_id):
        logger.info(f"Payment {payment_id} already processed")
        return  # Idempotent!
    
    # Process only once
    await db.payments.create({
        "id": payment_id,
        "status": "completed"
    })
```

## File Structure

```
pubsub/
├── README.md                      # This file
├── PATTERNS_GUIDE.md             # Detailed patterns & examples
├── requirements.txt
├── __init__.py
├── exceptions.py
├── rabbitmq/
│   ├── __init__.py
│   ├── connection.py             # Connection manager
│   ├── publisher.py              # Event/queue/exchange publisher
│   ├── consumer.py               # Event/queue subscriber
│   └── health.py                 # Health check
├── redis/
│   ├── __init__.py
│   ├── connection.py             # Redis connection
│   ├── publisher.py              # Pub/Sub publisher
│   ├── subscriber.py             # Pub/Sub subscriber
│   └── cache.py                  # Cache helper
├── examples/
│   ├── rabbitmq_example.py       # Full RabbitMQ example
│   ├── redis_example.py          # Full Redis example
│   └── mixed_example.py          # Using both
└── tests/
    ├── test_rabbitmq_publisher.py
    ├── test_redis_publisher.py
    └── test_integration.py
```

## Common Patterns

### Fan-Out (One event → Many consumers)
```
Publisher
  ↓
Topic Exchange (user.events.*)
  ├→ Queue: email_service
  ├→ Queue: analytics_service
  └→ Queue: logging_service
```

### Work Queue (Many tasks → Load balanced workers)
```
Publishers → Queue → Worker 1
         ↘        ↗ Worker 2
          → Worker 3
```

### Request-Reply (Sync over async)
```
Service A → RPC Queue → Service B
        ↖ Reply Queue ↗
```

## Monitoring

### RabbitMQ Management UI
```bash
# Access at http://localhost:15672
# Default: guest/guest
```

Check:
- Queue depth
- Consumer count
- Message rates
- Connection status

### Redis CLI
```bash
redis-cli
PUBSUB CHANNELS        # Active channels
PUBSUB NUMSUB channel  # Subscribers per channel
INFO stats             # Performance stats
```

## Troubleshooting

**Messages not delivered:**
1. Check queue/exchange declarations
2. Verify routing key bindings
3. Ensure consumer is running
4. Check dead letter queue

**Connection refused:**
1. Verify broker is running
2. Check credentials
3. Verify network connectivity
4. Check firewall rules

**Message loss:**
1. Use `persistent=True` for critical messages
2. Implement consumer acknowledgment
3. Setup dead letter exchange
4. Monitor for unacked messages

## Resources

- [RabbitMQ Docs](https://www.rabbitmq.com/documentation.html)
- [Pika Documentation](https://pika.readthedocs.io/)
- [Redis Pub/Sub](https://redis.io/topics/pubsub)
- [Redis-py Docs](https://redis-py.readthedocs.io/)
- See `PATTERNS_GUIDE.md` for more examples
