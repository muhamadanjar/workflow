# RabbitMQ Implementation Guide

## Core Concepts

### Exchanges
Route messages to queues.

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare exchange
channel.exchange_declare(
    exchange='my-exchange',
    exchange_type='topic',  # topic, direct, fanout, headers
    durable=True
)
```

### Queues
Hold messages until consumed.

```python
# Declare queue
channel.queue_declare(queue='my-queue', durable=True)

# Bind queue to exchange
channel.queue_bind(
    exchange='my-exchange',
    queue='my-queue',
    routing_key='user.#'  # Match routing keys like user.created, user.updated
)
```

### Publishing

```python
def publish_message(channel, exchange, routing_key, message):
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message.encode(),
        properties=pika.BasicProperties(
            delivery_mode=2  # Make message persistent
        )
    )
    print(f"Published: {message}")

# Usage
publish_message(channel, 'my-exchange', 'user.created', '{"id": "123"}')
```

### Consuming

```python
def on_message(channel, method, properties, body):
    print(f"Received: {body.decode()}")
    
    try:
        # Process message
        process_event(body)
        
        # Acknowledge
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error: {e}")
        # Nack and requeue
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Set up consumer
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='my-queue', on_message_callback=on_message)

print('Waiting for messages...')
channel.start_consuming()
```

## Exchange Types

### Direct
Exact routing key match.

```python
# Publish to specific queue
channel.basic_publish(
    exchange='direct-exchange',
    routing_key='error',  # Must match exactly
    body=b'Error message'
)

# Consumer listens to 'error'
channel.queue_bind(exchange='direct-exchange', queue='error-queue', routing_key='error')
```

### Topic
Pattern-based routing.

```python
# Publish events
channel.basic_publish(exchange='topic-exchange', routing_key='user.created', body=b'...')
channel.basic_publish(exchange='topic-exchange', routing_key='user.updated', body=b'...')
channel.basic_publish(exchange='topic-exchange', routing_key='order.created', body=b'...')

# Consumer subscribes to patterns
channel.queue_bind(exchange='topic-exchange', queue='user-queue', routing_key='user.#')     # All user events
channel.queue_bind(exchange='topic-exchange', queue='all-queue', routing_key='#')           # All events
channel.queue_bind(exchange='topic-exchange', queue='created-queue', routing_key='*.created')  # Any .created event
```

### Fanout
Broadcast to all queues.

```python
channel.exchange_declare(exchange='fanout-exchange', exchange_type='fanout')

# Publish once, all queues receive
channel.basic_publish(exchange='fanout-exchange', routing_key='', body=b'Broadcast')

# Multiple consumers
channel.queue_bind(exchange='fanout-exchange', queue='queue1')
channel.queue_bind(exchange='fanout-exchange', queue='queue2')
channel.queue_bind(exchange='fanout-exchange', queue='queue3')
```

## Dead Letter Queues (DLQ)

Handle failed messages:

```python
# Main queue with DLQ
channel.queue_declare(
    queue='main-queue',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx-exchange',
        'x-dead-letter-routing-key': 'dlq',
        'x-message-ttl': 60000  # 60 second expiration
    }
)

# DLQ exchange and queue
channel.exchange_declare(exchange='dlx-exchange', exchange_type='direct')
channel.queue_declare(queue='dead-letter-queue', durable=True)
channel.queue_bind(exchange='dlx-exchange', queue='dead-letter-queue', routing_key='dlq')

# Consumer with nack on error
def on_message(channel, method, properties, body):
    try:
        process_message(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Nack and let DLQ handle
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

## Work Queues (Load Balancing)

```python
# Multiple workers
for i in range(3):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task-queue', on_message_callback=worker)

# Tasks added to queue, distributed to workers
for task in tasks:
    channel.basic_publish(
        exchange='',
        routing_key='task-queue',
        body=json.dumps(task),
        properties=pika.BasicProperties(delivery_mode=2)
    )
```

## Delayed Messages

```python
# Queue with TTL and redirection
channel.queue_declare(
    queue='delayed-queue',
    arguments={
        'x-dead-letter-exchange': 'main-exchange',
        'x-message-ttl': 5000  # 5 second delay
    }
)

# Send to delayed queue
channel.basic_publish(
    exchange='',
    routing_key='delayed-queue',
    body=b'Delayed message'
)

# After TTL, message moves to main-exchange
```

## RPC Pattern (Request-Reply)

```python
import uuid

class RpcClient:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
        
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_reply
        )
    
    def on_reply(self, channel, method, properties, body):
        self.response = body
    
    def call(self, request):
        self.response = None
        
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc-queue',
            body=request,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=str(uuid.uuid4())
            )
        )
        
        while self.response is None:
            self.connection.process_data_events()
        
        return self.response

# Server
def on_request(channel, method, properties, body):
    result = do_calculation(body)
    
    channel.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=result,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        )
    )
```

## Connection Pooling

```python
from pika import BlockingConnection, ConnectionParameters

class RabbitMQPool:
    def __init__(self, host='localhost', size=5):
        self.host = host
        self.pool = []
        self.size = size
        self._create_connections()
    
    def _create_connections(self):
        for _ in range(self.size):
            conn = BlockingConnection(ConnectionParameters(self.host))
            self.pool.append(conn)
    
    def get_connection(self):
        if self.pool:
            return self.pool.pop()
        return BlockingConnection(ConnectionParameters(self.host))
    
    def return_connection(self, conn):
        if len(self.pool) < self.size:
            self.pool.append(conn)
        else:
            conn.close()
    
    def close_all(self):
        for conn in self.pool:
            conn.close()

# Usage
pool = RabbitMQPool()
conn = pool.get_connection()
try:
    channel = conn.channel()
    # Use channel
finally:
    pool.return_connection(conn)
```

## Monitoring & Management

```python
import requests

# RabbitMQ Management API
def get_queue_stats(username='guest', password='guest', host='localhost'):
    url = f'http://{host}:15672/api/queues'
    response = requests.get(url, auth=(username, password))
    
    for queue in response.json():
        print(f"Queue: {queue['name']}")
        print(f"  Messages: {queue['messages']}")
        print(f"  Consumers: {queue['consumers']}")

# Health check
def is_rabbitmq_healthy(host='localhost'):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        connection.close()
        return True
    except:
        return False
```

## Best Practices

- ✅ Set delivery_mode=2 for persistent messages
- ✅ Use prefetch_count for load balancing
- ✅ Implement DLQ for failed messages
- ✅ ACK messages after processing
- ✅ Use durable queues/exchanges
- ✅ Monitor queue depth
- ✅ Implement retry logic
- ✅ Use connection pooling
- ✅ Set TTL on messages
- ✅ Log all failures
