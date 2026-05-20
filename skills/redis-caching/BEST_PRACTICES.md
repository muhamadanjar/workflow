# Redis Best Practices

Production patterns, anti-patterns, performance tuning.

## Key Naming Conventions

### Hierarchical Keys

```python
# Good: Clear namespace separation
"user:123:profile"
"user:123:settings"
"post:456:comments"
"cache:products:trending"
"session:abc123def"
"queue:emails:pending"

# Bad: Vague or flat
"user_123_profile"
"data_ABC"
"tmp_key_1"
```

### Prefix by Feature

```python
# Sessions
session:{session_id}

# Caches
cache:user:{user_id}
cache:product:{product_id}

# Counters
counter:api_calls:{user_id}
counter:page_views:{page_id}

# Queues
queue:emails
queue:notifications

# Rates
rate_limit:{user_id}:{endpoint}

# Locks
lock:{resource}

# Leaderboards
leaderboard:daily
leaderboard:weekly
```

## Data Type Selection

### String (Simple Values)

```python
# ✅ Good: Atomic counters, configs, simple values
redis.set("config:api_timeout", "5000")
redis.incr("user:123:login_count")

# ❌ Bad: Large JSON, complex objects (slow)
large_json = json.dumps({"data": "..." * 10000})
redis.set("user:123", large_json)  # Inefficient
```

### Hash (Related Fields)

```python
# ✅ Good: User profile (multiple fields, often accessed together)
redis.hset("user:123", mapping={
    "name": "John",
    "email": "john@example.com",
    "created_at": "2026-01-01"
})

# ❌ Bad: Separate string keys for related data
redis.set("user:123:name", "John")
redis.set("user:123:email", "john@example.com")  # Multiple round-trips
```

### List (Ordered Sequences)

```python
# ✅ Good: Queues, timelines, leaderboards
redis.rpush("notifications:user:123", "msg1", "msg2")
notifications = redis.lrange("notifications:user:123", 0, -1)

# ❌ Bad: Using string with delimiters
redis.set("notifications", "msg1,msg2,msg3")  # Can't efficiently pop
```

### Set (Unique Collections)

```python
# ✅ Good: Tags, memberships, unique items
redis.sadd("user:123:tags", "python", "redis", "databases")
redis.sinter("user:1:friends", "user:2:friends")  # Common friends

# ❌ Bad: List with duplicates
redis.rpush("user:123:tags", "python", "python", "redis")  # Duplicates
```

### Sorted Set (Rankings)

```python
# ✅ Good: Leaderboards, scores, time-series
redis.zadd("leaderboard", {"player1": 1000, "player2": 950})
top_10 = redis.zrange("leaderboard", 0, 9, rev=True, withscores=True)

# ❌ Bad: Using hash or list for rankings
redis.hset("leaderboard", "player1", 1000)  # Can't efficiently rank
```

## TTL & Expiration

### Always Set TTL

```python
# ✅ Good: Prevent unbounded memory growth
redis.setex("session:abc123", 86400, session_data)  # 24h
redis.setex("cache:product:456", 3600, product_data)  # 1h

# ❌ Bad: No expiration (memory fills)
redis.set("session:abc123", session_data)

# ❌ Bad: Forget to renew
redis.get("session:abc123")  # TTL ticks down, eventually deleted
```

### Appropriate TTL by Type

```python
# Short-lived (5-30 min)
redis.setex("rate_limit:user:123", 300, "100")  # 5 min

# Moderate (1-24 hours)
redis.setex("cache:user:123", 3600, user_data)  # 1h
redis.setex("session:abc", 86400, session_data)  # 24h

# Long-lived (days-weeks)
redis.setex("leaderboard:monthly", 2592000, data)  # 30 days

# Permanent (no expiry, explicit reasons)
redis.set("config:app_version", "2.0.1")
redis.persist("important:data")
```

### Refresh TTL on Access

```python
# ✅ Extend expiry when accessed
def get_session(session_id):
    data = redis.get(f"session:{session_id}")
    if data:
        redis.expire(f"session:{session_id}", 86400)  # Reset to 24h
        return json.loads(data)
    return None

# ❌ Stale session expires too soon
def get_session_bad(session_id):
    return redis.get(f"session:{session_id}")
```

## Serialization

### Efficient Serialization

```python
import json

# ✅ Good: Compact JSON
data = {"name": "John", "age": 30}
redis.set("user:123", json.dumps(data))

# ❌ Bad: Verbose repr
redis.set("user:123", repr(data))  # b"{'name': 'John', ...}"

# ❌ Bad: Pickle security risk
import pickle
redis.set("user:123", pickle.dumps(data))  # Unsafe
```

### Handle Complex Types

```python
# ✅ Custom serializer for datetime
def serialize_user(user):
    return json.dumps({
        "name": user.name,
        "created_at": user.created_at.isoformat()  # String format
    })

# ✅ Or use json with default
json.dumps(data, default=str)  # Convert non-serializable to string
```

## Error Handling

### Fail Gracefully

```python
from redis.exceptions import RedisError, ConnectionError, TimeoutError

# ✅ Good: Fallback to database
def get_user(user_id):
    try:
        cached = redis.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)
    except (ConnectionError, TimeoutError):
        logger.warning(f"Redis unavailable, using database for user:{user_id}")
    except Exception as e:
        logger.error(f"Redis error: {e}")
    
    # Fallback to database
    return db.get_user(user_id)

# ❌ Bad: Crash on Redis error
def get_user_bad(user_id):
    cached = redis.get(f"user:{user_id}")  # Fails if Redis down
    return json.loads(cached)
```

### Connection Pool Resilience

```python
from redis import ConnectionPool, Redis

# ✅ Good: Retry, timeout, health check
pool = ConnectionPool(
    host='localhost',
    port=6379,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30,
    max_connections=50
)

redis = Redis(connection_pool=pool)

# ❌ Bad: No resilience
redis = Redis()  # Defaults may not be safe
```

## Memory Management

### Prevent Memory Bloat

```python
# ✅ Good: Aggressive TTL
redis.setex("temp:api:123", 300, data)  # 5 minutes

# ✅ Good: Eviction policy
# maxmemory 1gb
# maxmemory-policy allkeys-lru

# ❌ Bad: No TTL
redis.set("session:abc", data)  # Never expires

# ❌ Bad: Too-long TTL
redis.setex("cache:123", 31536000, data)  # 1 year (bloat)
```

### Monitor Large Values

```python
# ✅ Split large objects
# Instead of one 5MB JSON:
# "user:123:profile" (500KB)
# "user:123:settings" (100KB)
# "user:123:history" (4.4MB)

# ❌ Avoid:
redis.set("user:123", huge_json)  # 5MB in one key
```

### Use Compression

```python
import gzip
import json

# ✅ Compress large strings
large_data = json.dumps([...] * 1000)
compressed = gzip.compress(large_data.encode())
redis.set("archive:data", compressed)

# Decompress on read
compressed = redis.get("archive:data")
data = json.loads(gzip.decompress(compressed))

# ❌ Avoid uncompressed bulk data
redis.set("archive:data", large_data)  # Wastes memory
```

## Atomicity & Transactions

### Atomic Operations

```python
# ✅ Good: Atomic increment
redis.incr("page:views")  # Thread-safe

# ✅ Good: Atomic set/check
redis.set("lock:resource", lock_id, ex=10, nx=True)  # Only if not exists

# ❌ Bad: Non-atomic check-then-set
if redis.get("lock:resource") is None:  # Race condition
    redis.set("lock:resource", lock_id)
```

### Transactions (MULTI/EXEC)

```python
# ✅ Good: All-or-nothing updates
pipe = redis.pipeline()
pipe.incr("stats:views")
pipe.incr("stats:visits")
pipe.setex("last_update", 3600, time.time())
pipe.execute()

# ❌ Bad: Separate calls (inconsistent state)
redis.incr("stats:views")
redis.incr("stats:visits")
redis.setex("last_update", 3600, time.time())
```

## Cache Invalidation

### Invalidate on Update

```python
# ✅ Good: Clear cache on write
def update_user(user_id, data):
    db.update_user(user_id, data)
    redis.delete(f"user:{user_id}")  # Invalidate
    return data

# ❌ Bad: Update DB but forget cache
def update_user_bad(user_id, data):
    db.update_user(user_id, data)
    # Cache still has old data!
```

### Pattern Invalidation

```python
# ✅ Good: Invalidate related keys
def update_user_profile(user_id):
    db.update_user_profile(user_id)
    
    # Clear all user-related cache
    keys = redis.keys(f"user:{user_id}:*")
    if keys:
        redis.delete(*keys)

# ❌ Bad: Partial invalidation (orphaned cache)
redis.delete(f"user:{user_id}:profile")  # Forgets other related keys
```

### TTL Invalidation (Cache-Aside)

```python
# ✅ Good: Explicit TTL prevents stale data
def get_product(product_id):
    cached = redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    product = db.get_product(product_id)
    redis.setex(f"product:{product_id}", 300, json.dumps(product))  # 5 min
    return product

# ❌ Bad: Cache never expires
def get_product_bad(product_id):
    cached = redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    product = db.get_product(product_id)
    redis.set(f"product:{product_id}", json.dumps(product))  # Never expires
    return product
```

## Anti-Patterns

### Cache Stampede

```python
# ❌ Bad: All threads hit DB on miss
if not redis.get(key):
    value = expensive_query()  # 1000 threads do this
    redis.set(key, value)

# ✅ Good: Lock to prevent stampede
lock_acquired = redis.set(f"lock:{key}", "1", ex=5, nx=True)
if lock_acquired:
    value = expensive_query()
    redis.set(key, value)
    redis.delete(f"lock:{key}")
else:
    # Wait for lock release then try cache
    time.sleep(0.1)
    value = redis.get(key) or expensive_query()
```

### Cache Penetration

```python
# ❌ Bad: Non-existent key hits DB repeatedly
user = redis.get(f"user:{id}")
if not user:
    user = db.get_user(id)  # NULL queries hit DB every time

# ✅ Good: Cache miss for non-existent items
user = redis.get(f"user:{id}")
if user == "NULL":
    return None
elif not user:
    user = db.get_user(id)
    if not user:
        redis.setex(f"user:{id}", 300, "NULL")  # Cache the miss
    else:
        redis.setex(f"user:{id}", 3600, json.dumps(user))
```

### Stale Data

```python
# ❌ Bad: Update DB but forget cache
def update_price(product_id, new_price):
    db.update_price(product_id, new_price)
    # Cache has old price!

# ✅ Good: Invalidate on update
def update_price(product_id, new_price):
    db.update_price(product_id, new_price)
    redis.delete(f"product:{product_id}:price")
```

## Performance Tips

### Pipeline Batch Operations

```python
# ✅ Good: Reduce round-trips (N+1 → 1)
pipe = redis.pipeline()
for user_id in user_ids:
    pipe.get(f"user:{user_id}")
results = pipe.execute()

# ❌ Bad: N round-trips
for user_id in user_ids:
    redis.get(f"user:{user_id}")
```

### Appropriate Key Types

```python
# ✅ Fast: Use right data structure
redis.zadd("leaderboard", {player: score})  # O(log N)

# ❌ Slow: Wrong structure
redis.rpush("leaderboard", f"{player}:{score}")  # O(N) to rank
```

### Connection Pooling

```python
# ✅ Good: Reuse connections
pool = ConnectionPool(max_connections=50)
redis = Redis(connection_pool=pool)

# ❌ Bad: New connection per operation
for key in keys:
    redis = Redis()  # Connection handshake every time
    redis.get(key)
```

## Testing

### Use Fake Redis

```python
import pytest
from fakeredis import FakeRedis

@pytest.fixture
def redis_client():
    return FakeRedis(decode_responses=True)

def test_cache(redis_client):
    redis_client.set("test", "value")
    assert redis_client.get("test") == "value"

def test_cache_ttl(redis_client):
    redis_client.setex("temp", 1, "value")
    assert redis_client.exists("temp")
    redis_client.expire("temp", -1)
    assert not redis_client.exists("temp")
```

### Test Cache Behavior

```python
def test_cache_miss_fallback(redis_client):
    """Verify cache miss falls back to DB"""
    cache = RedisCache(redis_client)
    
    # Cache miss
    result = cache.get("missing_key")
    assert result is None
    
    # Set and hit
    cache.set("key", {"data": "value"})
    result = cache.get("key")
    assert result == {"data": "value"}

def test_cache_ttl_expiry(redis_client):
    """Verify TTL works"""
    cache = RedisCache(redis_client, default_ttl=1)
    cache.set("key", "value")
    
    assert redis_client.exists("key")
    redis_client.expire("key", -1)
    assert not redis_client.exists("key")
```

## Security

### Validate Input

```python
# ✅ Good: Validate before storing
def set_user_cache(user_id, data):
    if not isinstance(user_id, int):
        raise ValueError("Invalid user_id")
    if len(json.dumps(data)) > 1_000_000:  # 1MB limit
        raise ValueError("Data too large")
    
    redis.setex(f"user:{user_id}", 3600, json.dumps(data))

# ❌ Bad: Trust input
redis.set(request.args['key'], request.args['value'])
```

### Connection Security

```python
# ✅ Good: TLS for remote Redis
redis = Redis(
    host='redis.example.com',
    port=6380,
    ssl=True,
    ssl_certfile='/path/to/cert.pem',
    ssl_keyfile='/path/to/key.pem'
)

# ✅ Good: Authentication
redis = Redis(password='secure_password')

# ❌ Bad: Unencrypted over network
redis = Redis(host='redis.example.com')  # Plain HTTP
```

## Checklist

- [ ] Meaningful key names (namespace:entity:id:field)
- [ ] Right data type (String/Hash/List/Set/Zset)
- [ ] TTL on all keys
- [ ] Error handling + fallback
- [ ] Connection pool + health checks
- [ ] Invalidate on updates
- [ ] Monitor memory usage
- [ ] Batch operations with pipeline
- [ ] Test with FakeRedis
- [ ] Security: TLS, auth, input validation

---

See **MONITORING_GUIDE.md** for operational insights.
