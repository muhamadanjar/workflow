# Redis Caching — Advanced Patterns

Complex caching strategies, optimization techniques, and production patterns.

## Distributed Locking

Ensure only one process executes critical section.

### Simple Lock

```python
import redis
import uuid
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def acquire_lock(key, timeout=10):
    """Try to acquire lock, return lock_id if successful"""
    lock_id = str(uuid.uuid4())
    acquired = r.set(f'lock:{key}', lock_id, nx=True, ex=timeout)
    return lock_id if acquired else None

def release_lock(key, lock_id):
    """Release lock if we still own it"""
    # Lua script ensures atomic check-and-delete
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return r.eval(script, 1, f'lock:{key}', lock_id)

# Usage
lock_id = acquire_lock('process:123')
if lock_id:
    try:
        # Do critical work
        process_order('order:123')
    finally:
        release_lock('process:123', lock_id)
else:
    print('Lock not acquired, skip')
```

### Redlock (Distributed Systems)

```python
from redlock import Redlock

# Setup with multiple Redis instances
dlm = Redlock(
    [
        {'host': 'localhost', 'port': 6379},
        {'host': 'localhost', 'port': 6380},
        {'host': 'localhost', 'port': 6381},
    ],
    auto_renewal=True,
    auto_renewal_max_count=10
)

# Acquire lock
lock = dlm.lock('critical_resource', 1000)  # 1 second timeout

if lock:
    try:
        # Critical section
        process_payment()
    finally:
        dlm.unlock(lock)
```

## Bloom Filters

Efficient membership testing.

```python
from pybloom import BloomFilter

# Create filter
bf = BloomFilter(capacity=100000, error_rate=0.001)

# Add items
for user_id in range(1000):
    bf.add(user_id)

# Check membership (may have false positives, no false negatives)
is_in_filter = 123 in bf  # True if added, might be true if not added

# Store in Redis
import pickle
r.set('user_ids:filter', pickle.dumps(bf))

# Load from Redis
bf = pickle.loads(r.get('user_ids:filter'))
```

## HyperLogLog

Approximate cardinality counting for huge datasets.

```python
# Add to HyperLogLog
r.pfadd('unique_visitors', 'user1', 'user2', 'user3')
r.pfadd('unique_visitors', 'user2', 'user4')  # user2 already counted once

# Get approximate count
count = r.pfcount('unique_visitors')  # ~4

# Merge multiple HyperLogLogs
r.pfadd('visitors:day1', 'user1', 'user2')
r.pfadd('visitors:day2', 'user3', 'user4')

# Union of counts
total = r.pfcount('visitors:day1', 'visitors:day2')  # ~4

# Use case: unique user counts per hour
for hour in range(24):
    r.pfadd(f'unique_users:hour:{hour}', ...user_ids...)

# Get total unique users across all hours
daily_unique = r.pfcount(*[f'unique_users:hour:{h}' for h in range(24)])
```

## Geospatial Indexes

Store and query locations.

```python
# Add locations (longitude, latitude, member)
r.geoadd('cities', 13.361389, 38.115556, 'Palermo')
r.geoadd('cities', 15.087269, 37.502669, 'Catania')

# Distance between two locations
distance = r.geodist('cities', 'Palermo', 'Catania', unit='km')

# Find nearby locations
nearby = r.georadius('cities', 15, 37, 200, unit='km')

# Get all positions
positions = r.geopos('cities', 'Palermo', 'Catania')

# Find closest N items
closest = r.georadius(
    'cities',
    15.087269, 37.502669,
    200,
    unit='km',
    count=5,
    sort='ASC'
)

# Use case: find restaurants near user
r.geoadd('restaurants', -73.9857, 40.7482, 'restaurant:1')
r.geoadd('restaurants', -73.9760, 40.7614, 'restaurant:2')

nearby_restaurants = r.georadius(
    'restaurants',
    user_longitude, user_latitude,
    5,  # 5km radius
    unit='km',
    count=10,
    sort='ASC'
)
```

## Streams (Redis 5.0+)

Persistent append-only logs with consumer groups.

```python
# Add to stream
message_id = r.xadd('events', {
    'user_id': '123',
    'action': 'login',
    'timestamp': time.time()
})

# Read from stream
messages = r.xrange('events', count=10)  # All messages
messages = r.xrevrange('events', count=10)  # Latest messages

# Read by ID range
messages = r.xrange('events', '-', '+', count=100)

# Blocking read (wait for new messages)
messages = r.xread({'events': '0'}, count=1, block=1000)

# Consumer groups
r.xgroup_create('events', 'mygroup', id='0', mkstream=True)

# Consumer reads from group
messages = r.xreadgroup('mygroup', 'consumer1', {'events': '>'})

# Process and acknowledge
for msg_id, msg_data in messages:
    # Process message
    process_event(msg_data)
    # Acknowledge
    r.xack('events', 'mygroup', msg_id)

# Pending messages
pending = r.xpending('events', 'mygroup')

# Claim message from other consumer
r.xclaim('events', 'mygroup', 'consumer2', 0, [msg_id])

# Use case: event sourcing
def emit_event(aggregate_id, event_type, data):
    r.xadd(
        f'events:{aggregate_id}',
        {
            'type': event_type,
            'data': json.dumps(data),
            'timestamp': time.time()
        }
    )

def get_event_history(aggregate_id):
    messages = r.xrange(f'events:{aggregate_id}')
    return [msg_data for _, msg_data in messages]
```

## BitMap Operations

Efficient boolean operations on large datasets.

```python
# Set bit
r.setbit('online_users', 0, 1)  # User 0 is online
r.setbit('online_users', 1, 1)  # User 1 is online
r.setbit('online_users', 5, 0)  # User 5 is offline

# Get bit
is_online = r.getbit('online_users', 0)

# Count set bits
online_count = r.bitcount('online_users')

# Bitwise operations
r.bitop('AND', 'premium_online', 'premium_users', 'online_users')
r.bitop('OR', 'all_active', 'online_users', 'logged_in_today')

# Find first set bit
first_online = r.bitpos('online_users', 1)  # First 1

# Use case: user activity tracking
today = datetime.now().date()
# Mark user 123 as active today
r.setbit(f'active_users:{today}', 123, 1)

# Count active users
active_count = r.bitcount(f'active_users:{today}')

# Find inactive users
r.bitop('NOT', f'inactive_users:{today}', f'active_users:{today}')
```

## Lua Scripts

Run complex operations atomically.

```python
# Simple script: increment if exists
script = """
local value = redis.call('GET', KEYS[1])
if not value then
    return nil
end
return redis.call('INCR', KEYS[1])
"""

result = r.eval(script, 1, 'counter')

# Complex script: sliding window rate limiter
rate_limit_script = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = redis.call('GET', key)
if not current then
    redis.call('SET', key, 1)
    redis.call('EXPIRE', key, window)
    return 1
elseif tonumber(current) < limit then
    redis.call('INCR', key)
    return tonumber(current) + 1
else
    return 0
end
"""

# Use rate limit
allowed = r.eval(rate_limit_script, 1, f'rate:{user_id}', 10, 60)
if allowed:
    # Process request
else:
    # Reject request

# Register script for reuse
sha = r.script_load(rate_limit_script)
result = r.evalsha(sha, 1, f'rate:{user_id}', 10, 60)
```

## Caching Invalidation Strategies

### Tag-Based Invalidation

```python
# Store with tags
def cache_with_tags(key, value, tags, ttl=3600):
    r.setex(key, ttl, json.dumps(value))
    for tag in tags:
        r.sadd(f'tag:{tag}', key)

# Invalidate by tag
def invalidate_tag(tag):
    keys = r.smembers(f'tag:{tag}')
    if keys:
        r.delete(*keys)
    r.delete(f'tag:{tag}')

# Usage
cache_with_tags('user:123:profile', user_data, ['user:123', 'users', 'profiles'])
invalidate_tag('user:123')  # Invalidate all user 123 caches
```

### Time-Based Versioning

```python
# Store with version
def cache_versioned(resource, version, value, ttl=3600):
    key = f'{resource}:v{version}'
    r.setex(key, ttl, json.dumps(value))
    r.set(f'{resource}:latest', version)

# Get latest
def get_latest(resource):
    version = r.get(f'{resource}:latest')
    if version:
        return r.get(f'{resource}:v{version}')

# Bump version to invalidate
def bump_version(resource):
    current = r.get(f'{resource}:latest') or '0'
    new_version = str(int(current) + 1)
    r.set(f'{resource}:latest', new_version)
```

## Monitoring & Debugging

```python
# Monitor commands in real-time
def monitor_redis():
    pubsub = r.pubsub()
    # Send MONITOR to see all commands
    for message in pubsub.listen():
        print(message)

# Get memory usage
memory_info = r.info('memory')
print(f"Used memory: {memory_info['used_memory_human']}")
print(f"Peak memory: {memory_info['used_memory_peak_human']}")

# Key space stats
keyspace = r.info('keyspace')
for db, info in keyspace.items():
    if isinstance(info, dict):
        print(f"{db}: {info['keys']} keys")

# Slowlog
slow_queries = r.slowlog_get(10)
for query in slow_queries:
    print(f"ID: {query[0]}, Duration: {query[2]}µs, Command: {query[3]}")

# Client stats
clients = r.client_list()
print(f"Connected clients: {len(clients)}")
```

---

Last Updated: 2026-06-25
