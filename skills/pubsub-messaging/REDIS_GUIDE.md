# Redis Pub/Sub Guide

Lightweight publish-subscribe for real-time messaging.

## Setup

```bash
pip install redis
```

## Basic Pub/Sub

### Publisher

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Publish message
redis_client.publish('notifications', 'User logged in')
redis_client.publish('notifications', 'New order created')
```

### Subscriber

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
pubsub = redis_client.pubsub()

# Subscribe to channel
pubsub.subscribe('notifications')

print('Listening for messages...')
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data']}")
```

## Pattern Subscription

Subscribe to multiple channels with wildcards.

```python
pubsub = redis_client.pubsub()

# Subscribe to pattern
pubsub.psubscribe('user:*:notifications')
pubsub.psubscribe('order:*:updates')

for message in pubsub.listen():
    if message['type'] == 'pmessage':
        pattern = message['pattern']
        channel = message['channel']
        data = message['data']
        print(f"[{pattern}] {channel}: {data}")
```

## Message Structure

```python
{
    'type': 'message',      # or 'subscribe', 'unsubscribe', 'pmessage'
    'pattern': None,        # Pattern if psubscribe
    'channel': b'notifications',
    'data': b'message content'
}
```

## Production Setup

### FastAPI Integration

```python
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import redis
import asyncio

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(pubsub_listener())
    yield
    # Shutdown

async def pubsub_listener():
    """Listen for Redis pub/sub messages"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('notifications')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            # Broadcast to connected WebSocket clients
            await broadcast_to_clients(message['data'])

app = FastAPI(lifespan=lifespan)

# WebSocket clients storage
connected_clients = set()

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        connected_clients.remove(websocket)

async def broadcast_to_clients(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            pass
```

### Celery + Redis Broker

```python
from celery import Celery

app = Celery(
    'myapp',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@app.task
def send_notification(user_id, message):
    redis_client = redis.Redis(host='localhost', port=6379)
    redis_client.publish(f'user:{user_id}:notifications', message)

@app.task
def listen_user_notifications():
    redis_client = redis.Redis(host='localhost', port=6379)
    pubsub = redis_client.pubsub()
    pubsub.psubscribe('user:*:notifications')
    
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            # Process notification
            print(f"Notification: {message['data']}")
```

## Common Patterns

### 1. User Notifications

```python
def notify_user(user_id, event_type, data):
    """Send notification to specific user"""
    channel = f"user:{user_id}:notifications"
    redis_client.publish(channel, json.dumps({
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }))

def listen_user_notifications(user_id):
    """Listen for user's notifications"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"user:{user_id}:notifications")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            notification = json.loads(message['data'])
            handle_notification(notification)
```

### 2. Broadcast Events

```python
def broadcast_event(event_type, data):
    """Broadcast to all listeners"""
    redis_client.publish('events', json.dumps({
        'type': event_type,
        'data': data
    }))

def listen_all_events():
    """Listen to all events"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('events')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            route_event(event)
```

### 3. Room-Based Messaging

```python
def join_room(user_id, room_id):
    """Add user to room"""
    channel = f"room:{room_id}:messages"
    # Subscribe logic handled in listener

def send_room_message(room_id, user_id, message):
    """Send message to room"""
    channel = f"room:{room_id}:messages"
    redis_client.publish(channel, json.dumps({
        'user_id': user_id,
        'message': message,
        'timestamp': time.time()
    }))

def listen_room_messages(room_id):
    """Listen to room messages"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe(f"room:{room_id}:messages")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            msg = json.loads(message['data'])
            process_room_message(msg)
```

### 4. Status Updates

```python
def publish_status(resource_type, resource_id, status):
    """Publish status change"""
    channel = f"{resource_type}:{resource_id}:status"
    redis_client.publish(channel, json.dumps({
        'status': status,
        'timestamp': datetime.now().isoformat()
    }))

def watch_status(resource_type, resource_id, callback):
    """Watch for status changes"""
    pubsub = redis_client.pubsub()
    channel = f"{resource_type}:{resource_id}:status"
    pubsub.subscribe(channel)
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            status = json.loads(message['data'])
            callback(status)
```

## Limitations & Workarounds

### No Message Persistence

Redis Pub/Sub doesn't store messages. Late subscribers miss messages.

**Workaround:** Use Redis Streams instead.

```python
# Publish to stream
redis_client.xadd('notifications', {'message': 'New order'})

# Read from stream
messages = redis_client.xrange('notifications', count=10)
for msg_id, msg_data in messages:
    print(msg_data)

# Subscribe to new messages in stream
last_id = '0'
while True:
    messages = redis_client.xread({'notifications': last_id}, count=1, block=0)
    for stream, msg_list in messages:
        for msg_id, msg_data in msg_list:
            print(msg_data)
            last_id = msg_id
```

### No Acknowledgment

Messages aren't acknowledged. Subscribers might miss messages if they disconnect.

**Workaround:** Implement message queue with Celery + Redis.

## Monitoring

```python
def get_pubsub_stats():
    """Get Redis pub/sub statistics"""
    info = redis_client.info('stats')
    return {
        'pubsub_channels': info.get('pubsub_channels'),
        'pubsub_patterns': info.get('pubsub_patterns'),
        'connected_clients': info.get('connected_clients')
    }

def list_active_channels():
    """List all active channels"""
    channels = redis_client.pubsub_channels()
    return {
        'channels': channels,
        'count': len(channels)
    }
```

## Best Practices

1. **Use patterns** — Subscribe to `user:*:notifications` instead of individual channels
2. **JSON encode** — Always encode complex data as JSON
3. **Error handling** — Wrap listeners in try-catch
4. **Timeouts** — Set socket timeouts
5. **Cleanup** — Unsubscribe when done
6. **Monitoring** — Track active channels and subscribers
7. **Alternative for persistence** — Use Redis Streams or message queues
8. **Connection pooling** — Reuse Redis connections

---

Last Updated: 2026-06-25
