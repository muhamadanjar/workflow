# Redis Caching — Basics

Data structures, commands, and foundational patterns.

## Data Structures

### Strings

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Set & Get
r.set('key', 'value')
value = r.get('key')

# Set with expiry
r.setex('temporary', 3600, 'value')  # Expires in 1 hour

# Set if not exists
r.setnx('key', 'value')  # Returns 1 if set, 0 if exists

# Increment
r.set('counter', 0)
r.incr('counter')    # 1
r.incrby('counter', 5)  # 6

# String append
r.append('key', ' more text')
length = r.strlen('key')
```

### Hashes

```python
# Set hash fields
r.hset('user:1', 'name', 'John')
r.hset('user:1', 'email', 'john@example.com')

# Or set multiple at once
r.hset('user:1', mapping={
    'name': 'John',
    'email': 'john@example.com',
    'age': 30
})

# Get hash field
name = r.hget('user:1', 'name')

# Get all fields
user = r.hgetall('user:1')  # {'name': 'John', 'email': '...'}

# Delete field
r.hdel('user:1', 'age')

# Check if field exists
exists = r.hexists('user:1', 'name')

# Get all keys
keys = r.hkeys('user:1')

# Get all values
values = r.hvals('user:1')

# Count fields
count = r.hlen('user:1')
```

### Lists

```python
# Push to list
r.rpush('queue', 'item1', 'item2', 'item3')  # Right push
r.lpush('queue', 'item0')                     # Left push

# Pop from list
item = r.rpop('queue')  # Remove from right
item = r.lpop('queue')  # Remove from left

# Get range
items = r.lrange('queue', 0, -1)  # All items

# Get length
length = r.llen('queue')

# Trim list
r.ltrim('queue', 0, 99)  # Keep first 100 items

# Index access
item = r.lindex('queue', 0)

# Set by index
r.lset('queue', 0, 'new_value')
```

### Sets

```python
# Add to set
r.sadd('tags', 'python', 'redis', 'caching')

# Get all members
tags = r.smembers('tags')

# Check membership
is_member = r.sismember('tags', 'python')

# Remove from set
r.srem('tags', 'python')

# Set operations
r.sadd('user:1:tags', 'python', 'redis')
r.sadd('user:2:tags', 'python', 'javascript')

# Union
all_tags = r.sunion('user:1:tags', 'user:2:tags')

# Intersection
common = r.sinter('user:1:tags', 'user:2:tags')

# Difference
unique = r.sdiff('user:1:tags', 'user:2:tags')

# Count
count = r.scard('tags')
```

### Sorted Sets

```python
# Add with score
r.zadd('leaderboard', {'player1': 100, 'player2': 95, 'player3': 105})

# Get by rank
top = r.zrevrange('leaderboard', 0, 9)  # Top 10

# Get with scores
top_with_scores = r.zrevrange('leaderboard', 0, 9, withscores=True)

# Get by score range
high_scorers = r.zrangebyscore('leaderboard', 100, 200)

# Count in range
count = r.zcount('leaderboard', 100, 200)

# Increment score
r.zincrby('leaderboard', 5, 'player1')

# Get rank
rank = r.zrevrank('leaderboard', 'player1')  # 0-indexed from top

# Get score
score = r.zscore('leaderboard', 'player1')

# Remove
r.zrem('leaderboard', 'player1')
```

## Key Management

```python
# Check if key exists
exists = r.exists('key')

# Delete key
r.delete('key1', 'key2', 'key3')

# Get all keys (avoid in production!)
all_keys = r.keys('*')

# Find keys by pattern
user_keys = r.keys('user:*')

# Rename key
r.rename('old_key', 'new_key')

# Get type of key
key_type = r.type('key')

# Set expiry
r.expire('key', 3600)  # 1 hour

# Set expiry at timestamp
r.expireat('key', 1609459200)

# Get TTL
ttl = r.ttl('key')  # -1 if no expiry, -2 if doesn't exist

# Persist key (remove expiry)
r.persist('key')

# Get remaining time in milliseconds
pttl = r.pttl('key')
```

## Transactions

```python
# Pipeline: batch multiple commands
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.incr('counter')
results = pipe.execute()

# Watch for changes
r.watch('key')
pipe = r.pipeline(transaction=True)
try:
    pipe.multi()
    pipe.set('key', 'new_value')
    pipe.execute()
except redis.WatchError:
    print('Key was modified, retry')
finally:
    r.unwatch()
```

## Connection Management

```python
# Single connection
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 3,   # TCP_KEEPIDLE
        2: 3,   # TCP_KEEPINTVL
        3: 3,   # TCP_KEEPCNT
    }
)

# Connection pool
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50
)
r = redis.Redis(connection_pool=pool)

# Sentinel for HA
from redis.sentinel import Sentinel

sentinels = [('localhost', 26379)]
sentinel = Sentinel(sentinels)
r = sentinel.master_for('mymaster', socket_connect_timeout=0.1)

# Cluster
from rediscluster import RedisCluster

startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]
r = RedisCluster(startup_nodes=startup_nodes)
```

## Performance Tips

1. **Pipeline commands** — Send multiple at once
   ```python
   pipe = r.pipeline()
   for i in range(1000):
       pipe.set(f'key:{i}', f'value:{i}')
   pipe.execute()
   ```

2. **Use appropriate types** — Hash instead of string for objects
   ```python
   # Bad: store JSON
   r.set('user:1', json.dumps(user))
   
   # Good: use hash
   r.hset('user:1', mapping=user)
   ```

3. **Connection pooling** — Reuse connections
4. **Pipelining** — Reduce round-trips
5. **Monitor memory** — Track key sizes
6. **Eviction policy** — Set maxmemory-policy
7. **Persistence** — Configure AOF/RDB appropriately

## Best Practices

1. **Key naming** — Use `namespace:id:field` pattern
   - `user:123:profile`
   - `post:456:comments`
   - `cache:product:789`

2. **Expiry** — Always set TTL for cache entries
   ```python
   r.setex(f'user:{user_id}:profile', 3600, json.dumps(profile))
   ```

3. **Avoid keys() in production** — Use SCAN instead
   ```python
   cursor = 0
   while True:
       cursor, keys = r.scan(cursor, match='user:*', count=100)
       # Process keys
       if cursor == 0:
           break
   ```

4. **Handle failures** — Implement fallbacks
   ```python
   try:
       value = r.get('key')
   except redis.ConnectionError:
       value = fetch_from_database()
   ```

5. **Monitor connections** — Track active connections and pool usage

---

Last Updated: 2026-06-25
