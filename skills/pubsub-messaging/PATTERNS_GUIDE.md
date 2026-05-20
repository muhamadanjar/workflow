# Pub/Sub Patterns Guide

Complete guide to publish/subscribe patterns with RabbitMQ and Redis.

## Table of Contents

1. [Event-Driven Architecture](#event-driven-architecture)
2. [RabbitMQ Patterns](#rabbitmq-patterns)
3. [Redis Patterns](#redis-patterns)
4. [Hybrid Approaches](#hybrid-approaches)
5. [Error Handling](#error-handling)
6. [Testing](#testing)

---

## Event-Driven Architecture

### Domain Events
Events represent important business occurrences:

```python
# Domain event
class UserCreatedEvent:
    user_id: str
    email: str
    created_at: datetime
    
    def to_dict(self):
        return {
            "event_type": "user.created",
            "timestamp": self.created_at.isoformat(),
            "payload": {
                "user_id": self.user_id,
                "email": self.email
            }
        }

# In use case
async def register_user(email: str) -> User:
    user = User(email=email)
    user = await db.users.save(user)
    
    # Publish domain event
    event = UserCreatedEvent(user.id, user.email, datetime.now())
    await publisher.publish_event(
        event_type=event.type,
        payload=event.payload
    )
    
    return user
```

---

## RabbitMQ Patterns

### Pattern 1: Topic Exchange (Pub/Sub)

**Use:** Multiple subscribers listening to events

```python
# Publisher
publisher.publish_event(
    event_type="user.created",
    payload={"user_id": "123", "email": "test@example.com"},
    routing_key="user.events.created"
)

# Setup (in consumer startup)
exchange = "user_management_events"
queue = "email_service_queue"
routing_key = "user.events.created"

# Declare and bind
channel.exchange_declare(
    exchange=exchange,
    exchange_type="topic",
    durable=True
)
channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(
    exchange=exchange,
    queue=queue,
    routing_key=routing_key
)

# Consumer 1: Email Service
async def consume_user_created(message):
    user_id = message['payload']['user_id']
    send_welcome_email(user_id)

# Consumer 2: Analytics Service
async def consume_user_created_analytics(message):
    log_analytics_event(message['payload'])
```

### Pattern 2: Direct Exchange (Targeted)

**Use:** Send to specific queue, load-balanced

```python
# Publisher
publisher.publish_to_exchange(
    exchange="tasks",
    routing_key="tasks.email",
    message={
        "to": "user@example.com",
        "subject": "Welcome"
    },
    exchange_type="direct"
)

# Consumer setup
channel.exchange_declare(
    exchange="tasks",
    exchange_type="direct",
    durable=True
)
channel.queue_declare(queue="email_workers", durable=True)
channel.queue_bind(
    exchange="tasks",
    queue="email_workers",
    routing_key="tasks.email"
)

# Multiple workers (load balanced)
async def email_worker_1():
    async for message in consumer.listen_queue("email_workers"):
        await send_email(message)

async def email_worker_2():
    async for message in consumer.listen_queue("email_workers"):
        await send_email(message)

# Run both → messages distribute round-robin
```

### Pattern 3: Fanout Exchange (Broadcast)

**Use:** Send to all queues

```python
# Publisher
publisher.publish_to_exchange(
    exchange="broadcasts",
    message={
        "announcement": "System maintenance in 5 minutes"
    },
    exchange_type="fanout"
)

# Consumer setup (multiple independent queues)
exchange = "broadcasts"

# Queue 1: SMS Service
channel.queue_declare(queue="broadcast_sms", exclusive=True)
channel.queue_bind(exchange=exchange, queue="broadcast_sms")

# Queue 2: Email Service
channel.queue_declare(queue="broadcast_email", exclusive=True)
channel.queue_bind(exchange=exchange, queue="broadcast_email")

# Queue 3: WebSocket Service
channel.queue_declare(queue="broadcast_websocket", exclusive=True)
channel.queue_bind(exchange=exchange, queue="broadcast_websocket")

# Each consumer handles broadcast independently
```

### Pattern 4: Headers Exchange (Complex Routing)

**Use:** Route by message properties, not just routing key

```python
# Publisher with headers
publisher.publish_to_exchange(
    exchange="notifications",
    message={"alert": "System error"},
    headers={
        "priority": "high",
        "type": "system",
        "source": "monitoring"
    }
)

# Consumer binding by headers
channel.queue_bind(
    exchange="notifications",
    queue="urgent_alerts",
    arguments={
        "x-match": "all",  # Match ALL headers
        "priority": "high",
        "type": "system"
    }
)

# Or match ANY header
channel.queue_bind(
    exchange="notifications",
    queue="all_alerts",
    arguments={
        "x-match": "any",  # Match ANY header
        "priority": "high",
        "urgent": True
    }
)
```

### Pattern 5: Work Queue (Task Distribution)

**Use:** Distribute work across multiple workers

```python
# Publisher sends tasks
for task_data in tasks:
    publisher.publish_to_queue(
        queue="heavy_processing",
        message=task_data,
        persistent=True
    )

# Consumer
async def worker():
    async for message in consumer.listen_queue("heavy_processing"):
        try:
            # Heavy work
            result = await process_heavy_task(message)
            # Acknowledge after success
            message.ack()
        except Exception as e:
            # Nack to retry or deadletter
            message.nack(requeue=True)

# Run multiple workers
import asyncio
await asyncio.gather(
    worker(),
    worker(),
    worker(),
    worker()
)

# Work automatically distributes:
# Task 1 → Worker 1
# Task 2 → Worker 2
# Task 3 → Worker 3
# Task 4 → Worker 4
# Task 5 → Worker 1 (round-robin continues)
```

---

## Redis Patterns

### Pattern 1: Pub/Sub (Real-Time)

**Use:** Real-time updates, WebSockets, live notifications

```python
from redis import Redis

redis_client = Redis(host="localhost", port=6379)

# Publisher
def publish_notification(user_id: str, message: str):
    redis_client.publish(
        f"user:{user_id}:notifications",
        json.dumps({"message": message, "timestamp": datetime.now()})
    )

# Subscriber (blocking)
def subscribe_to_user_notifications(user_id: str):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"user:{user_id}:notifications")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            print(f"Notification: {data['message']}")

# Subscriber (with pattern)
def subscribe_to_all_user_notifications():
    pubsub = redis_client.pubsub()
    pubsub.psubscribe("user:*:notifications")
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            print(f"Broadcast: {message['data']}")
```

### Pattern 2: Channels + Rooms

**Use:** Chat, real-time collaboration, multi-tenant

```python
# Channel per room
class ChatRoom:
    def __init__(self, room_id: str):
        self.channel = f"chat:{room_id}"
        self.pubsub = redis_client.pubsub()
    
    async def broadcast(self, user_id: str, message: str):
        redis_client.publish(self.channel, json.dumps({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }))
    
    async def listen(self):
        self.pubsub.subscribe(self.channel)
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                yield json.loads(message['data'])

# WebSocket handler
async def websocket_chat(websocket, room_id: str, user_id: str):
    room = ChatRoom(room_id)
    await websocket.accept()
    
    # Listen task
    async def listen_task():
        async for msg in room.listen():
            await websocket.send_json(msg)
    
    # Send task
    async def send_task():
        while True:
            data = await websocket.receive_json()
            await room.broadcast(user_id, data['message'])
    
    await asyncio.gather(listen_task(), send_task())
```

### Pattern 3: Streams (Message Queue)

**Use:** Durable message queue, consumer groups

```python
# Producer
def publish_to_stream(stream_key: str, data: dict):
    message_id = redis_client.xadd(stream_key, data)
    return message_id

# Consumer group
def setup_consumer_group(stream_key: str, group_name: str):
    try:
        redis_client.xgroup_create(stream_key, group_name, id="0")
    except:
        pass  # Group might already exist

# Consumer
def consume_stream_group(stream_key: str, group_name: str, consumer_name: str):
    setup_consumer_group(stream_key, group_name)
    
    while True:
        # Read from consumer group
        messages = redis_client.xreadgroup(
            {stream_key: ">"},  # New messages only
            group_name,
            consumer_name,
            count=1,
            block=1000
        )
        
        for stream, message_list in messages or []:
            for message_id, data in message_list:
                try:
                    # Process message
                    process_message(data)
                    # Acknowledge
                    redis_client.xack(stream_key, group_name, message_id)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    # Message will retry
```

---

## Hybrid Approaches

### RabbitMQ for Durability + Redis for Real-Time

```python
# Publish to both
async def publish_order_event(order_id: str, event_data: dict):
    # Durable (RabbitMQ)
    rabbitmq_publisher.publish_event(
        event_type="order.created",
        payload=event_data
    )
    
    # Real-time (Redis)
    redis_client.publish(
        f"order:{order_id}:updates",
        json.dumps(event_data)
    )

# RabbitMQ → Persistent record, triggers microservices
# Redis → Real-time WebSocket updates
```

### Event Sourcing

```python
# All events persisted (RabbitMQ)
async def process_user_registration(user_data):
    user = await db.users.create(user_data)
    
    # Publish domain event (persisted)
    event = {
        "event_type": "user.registered",
        "user_id": str(user.id),
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    await rabbitmq_publisher.publish_event(
        event_type=event['event_type'],
        payload=event
    )
    
    # Store in event log for audit
    await db.event_log.create(event)
```

---

## Error Handling

### Dead Letter Queue (DLQ)

```python
# Setup DLQ
exchange = "main_exchange"
queue = "main_queue"
dlx = f"{exchange}_dlx"  # Dead letter exchange
dlq = f"{queue}_dlq"      # Dead letter queue

# Declare DLQ
channel.exchange_declare(exchange=dlx, exchange_type="direct", durable=True)
channel.queue_declare(queue=dlq, durable=True)
channel.queue_bind(exchange=dlx, queue=dlq, routing_key=queue)

# Declare main queue with DLQ
channel.queue_declare(
    queue=queue,
    durable=True,
    arguments={
        "x-dead-letter-exchange": dlx,
        "x-dead-letter-routing-key": queue,
        "x-max-length": 10000,
        "x-message-ttl": 3600000  # 1 hour
    }
)

# Consumer with error handling
async def consume_with_dlq(message):
    try:
        await process_message(message)
        message.ack()
    except Exception as e:
        logger.error(f"Error: {e}")
        # Nack → goes to DLQ
        message.nack(requeue=False)

# Monitor DLQ
async def monitor_dlq():
    async for message in consumer.listen_queue(dlq):
        logger.warning(f"Dead letter: {message}")
        # Handle manually or send alert
```

### Retry with Exponential Backoff

```python
# Publisher with retry
async def publish_with_retry(event, max_retries=3):
    for attempt in range(max_retries):
        try:
            await publisher.publish_event(**event)
            return True
        except PublishError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Retry {attempt + 1} in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
    
    # All retries failed
    logger.error(f"Failed to publish after {max_retries} attempts")
    return False
```

---

## Testing

### Unit Test: Publisher

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_publish_event():
    publisher = RabbitMQPublisher()
    
    with patch.object(publisher, '_ensure_exchange'):
        result = publisher.publish_event(
            event_type="test.event",
            payload={"data": "test"}
        )
    
    assert result is True

@pytest.mark.asyncio
async def test_publish_event_error():
    publisher = RabbitMQPublisher()
    
    with patch.object(publisher, 'connection_manager') as mock_conn:
        mock_conn.get_channel.side_effect = Exception("Connection failed")
        
        with pytest.raises(PublishError):
            publisher.publish_event(
                event_type="test.event",
                payload={"data": "test"}
            )
```

### Integration Test: Pub/Sub

```python
@pytest.mark.asyncio
async def test_event_flow():
    publisher = RabbitMQPublisher()
    consumer = RabbitMQConsumer()
    
    received_messages = []
    
    async def handler(message):
        received_messages.append(message)
    
    # Setup consumer
    consumer.subscribe(
        exchange="test",
        routing_key="test.*",
        queue="test_queue",
        callback=handler
    )
    
    # Publish event
    publisher.publish_event(
        event_type="test.event",
        payload={"data": "test"},
        routing_key="test.event"
    )
    
    # Wait for delivery
    await asyncio.sleep(0.5)
    
    # Verify
    assert len(received_messages) == 1
    assert received_messages[0]['payload']['data'] == 'test'
```

---

## Performance Considerations

### Message Size
- Keep messages small (< 1MB)
- Use compression for large payloads

### Throughput
- RabbitMQ: ~50K msg/sec (persistent)
- Redis: ~100K msg/sec (in-memory)

### Latency
- RabbitMQ: 1-10ms
- Redis: 0.1-1ms

### Tuning
```python
# RabbitMQ: Batch publishing
messages = [...]
for msg in messages:
    publisher.publish_event(**msg)

# Redis: Pipeline
pipe = redis_client.pipeline()
for msg in messages:
    pipe.publish(channel, msg)
pipe.execute()
```

---

## Best Practices Summary

1. **Use idempotent consumers** — handle duplicate messages
2. **Persist critical events** — RabbitMQ for important data
3. **Set message TTL** — prevent stale messages
4. **Monitor queues** — alert on depth/age
5. **Test error paths** — DLQ, retry, failures
6. **Document routing** — clear patterns and bindings
7. **Version events** — handle schema evolution
8. **Log comprehensively** — trace event flow
