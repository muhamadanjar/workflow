# Redis & Caching Skill

Complete guide: Redis data structures, caching patterns, invalidation strategies, Python implementation.

## Table of Contents

1. [Overview](#overview)
2. [Redis Data Structures](#redis-data-structures)
3. [Caching Patterns](#caching-patterns)
4. [Python Implementation](#python-implementation)
5. [Best Practices](#best-practices)

---

## Overview

**Redis:** In-memory data store. Fast, versatile, durable.

**Use Cases:**
- Caching (sessions, database queries)
- Real-time features (leaderboards, counters)
- Message queue (pub/sub, streams)
- Job queue (background tasks)
- Rate limiting
- Full-text search

**Why Redis?**
- **Fast:** Sub-millisecond latency
- **Versatile:** 5+ data structures
- **Durable:** Persistence (RDB, AOF)
- **Scalable:** Clustering, replication
- **Memory efficient:** Compression, eviction policies

## Redis Data Structures

### 1. String

Simplest. Store text, numbers, serialized objects.

```python
redis = Redis()

# Set/Get
redis.set("user:123:name", "John")
redis.get("user:123:name")  # b"John"

# With expiry
redis.setex("session:abc", 3600, "user_123")

# Increment
redis.incr("page_views")  # 1
redis.incr("page_views")  # 2

# Append
redis.append("log", "entry")
```

### 2. Hash

Key-value pairs within key. Like dict of dicts.

```python
# Set/Get hash fields
redis.hset("user:123", "name", "John")
redis.hset("user:123", "email", "john@example.com")

# Get one field
redis.hget("user:123", "name")  # b"John"

# Get all fields
redis.hgetall("user:123")  # {b"name": b"John", b"email": b"john@example.com"}

# Increment field
redis.hincrby("user:123", "age", 1)

# Check field exists
redis.hexists("user:123", "name")  # True

# Delete field
redis.hdel("user:123", "age")
```

### 3. List

Ordered collection. Queue, stack, timeline.

```python
# Push items
redis.rpush("queue:emails", "email1@test.com", "email2@test.com")  # Right push
redis.lpush("stack", "item1", "item2")  # Left push

# Pop items
redis.rpop("queue:emails")  # b"email2@test.com"
redis.lpop("stack")  # b"item2"

# Get range
redis.lrange("queue:emails", 0, -1)  # All items

# Length
redis.llen("queue:emails")

# Blocking pop (wait for item)
redis.blpop("queue:emails", timeout=10)  # Wait up to 10 seconds
```

### 4. Set

Unordered unique collection. Members, tags, friendships.

```python
# Add members
redis.sadd("user:123:friends", "user456", "user789")

# Check member
redis.sismember("user:123:friends", "user456")  # True

# Get all members
redis.smembers("user:123:friends")  # {b"user456", b"user789"}

# Count
redis.scard("user:123:friends")  # 2

# Remove member
redis.srem("user:123:friends", "user456")

# Set operations
redis.sunion("user:123:friends", "user:456:friends")  # Union
redis.sinter("user:123:friends", "user:456:friends")  # Intersection
redis.sdiff("user:123:friends", "user:456:blocked")   # Difference
```

### 5. Sorted Set (Zset)

Ordered by score. Leaderboards, rankings, timeseries.

```python
# Add members with score
redis.zadd("leaderboard", {"player1": 100, "player2": 95, "player3": 110})

# Get score
redis.zscore("leaderboard", "player1")  # 100

# Get members by rank (highest first)
redis.zrange("leaderboard", 0, -1, rev=True)  # Reverse order
# Result: [b"player3", b"player1", b"player2"]

# Get with scores
redis.zrange("leaderboard", 0, -1, withscores=True)
# [(b"player3", 110), (b"player1", 100), (b"player2", 95)]

# Increment score
redis.zincrby("leaderboard", 5, "player1")  # 105

# Count in range
redis.zcount("leaderboard", 100, 110)  # 2

# Remove member
redis.zrem("leaderboard", "player1")
```

### 6. HyperLogLog

Estimate cardinality (unique counts).

```python
# Add to HLL (unique visitors)
redis.pfadd("page:123:visitors", "user1", "user2", "user3", "user1")

# Count unique (approximate)
redis.pfcount("page:123:visitors")  # 3 (user1 counted once)

# Merge multiple HLLs
redis.pfmerge("visitors:total", "page:1:visitors", "page:2:visitors")
```

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)

**When:** Most common. General purpose.

```python
def get_user(user_id):
    # Try cache first
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss → fetch from database
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    
    # Store in cache (1 hour TTL)
    redis.setex(
        f"user:{user_id}",
        3600,
        json.dumps(user)
    )
    
    return user
```

**Pros:** Simple, flexible, no stale data issues
**Cons:** Cache miss → slow response

### 2. Write-Through

**When:** Consistency critical (payments, inventory).

```python
def update_user(user_id, data):
    # Update database first
    db.query(f"UPDATE users SET ... WHERE id = {user_id}")
    
    # Update cache (cache always in sync)
    redis.setex(
        f"user:{user_id}",
        3600,
        json.dumps(data)
    )
    
    return data
```

**Pros:** Cache always up-to-date, consistent
**Cons:** Slower writes (wait for both)

### 3. Write-Behind (Write-Back)

**When:** High throughput, eventual consistency OK.

```python
def update_user(user_id, data):
    # Update cache immediately (fast)
    redis.setex(
        f"user:{user_id}",
        3600,
        json.dumps(data)
    )
    
    # Queue database update (async)
    queue.push({
        "type": "update_user",
        "user_id": user_id,
        "data": data
    })
    
    return data

# Background worker
def process_updates():
    while True:
        item = queue.pop()
        if item["type"] == "update_user":
            db.update(item["user_id"], item["data"])
```

**Pros:** Fast writes, high throughput
**Cons:** Risk of data loss, complexity

### 4. Refresh-Ahead

**When:** Predictable access patterns (trending items).

```python
def refresh_trending_cache():
    # Periodically refresh popular items
    trending = db.query("SELECT * FROM posts ORDER BY views DESC LIMIT 10")
    
    for post in trending:
        redis.setex(
            f"post:{post.id}",
            300,  # 5 minutes
            json.dumps(post)
        )

# Run periodically (e.g., every 1 minute)
scheduler.every(1).minutes.do(refresh_trending_cache)
```

**Pros:** Never cache miss for popular items
**Cons:** Requires predictability

### 5. Sibling Cache

**When:** Related data (user + profile + settings).

```python
def get_user_with_profile(user_id):
    # Get all related data at once
    user = redis.get(f"user:{user_id}")
    profile = redis.get(f"profile:{user_id}")
    settings = redis.get(f"settings:{user_id}")
    
    if not all([user, profile, settings]):
        # Fetch all from database
        user_data = db.fetch_user_with_profile(user_id)
        
        # Cache all together
        pipeline = redis.pipeline()
        pipeline.setex(f"user:{user_id}", 3600, json.dumps(user_data.user))
        pipeline.setex(f"profile:{user_id}", 3600, json.dumps(user_data.profile))
        pipeline.setex(f"settings:{user_id}", 3600, json.dumps(user_data.settings))
        pipeline.execute()
    
    return {user, profile, settings}
```

## Cache Invalidation Strategies

### 1. TTL (Time-To-Live)

Automatic expiration.

```python
# Expire after 1 hour
redis.setex("user:123", 3600, data)

# Set expiry on existing key
redis.expire("user:123", 1800)  # 30 minutes

# Check TTL
redis.ttl("user:123")  # Seconds remaining

# Remove expiry (persist)
redis.persist("user:123")
```

### 2. Manual Invalidation

On update, delete from cache.

```python
def update_user(user_id, data):
    db.update_user(user_id, data)
    redis.delete(f"user:{user_id}")  # Invalidate
```

### 3. Tag-Based Invalidation

Invalidate related items.

```python
def update_post(post_id, data):
    db.update_post(post_id, data)
    
    # Invalidate post and related
    redis.delete(f"post:{post_id}")
    redis.delete(f"post:{post_id}:comments")
    redis.delete(f"user:{data.author_id}:posts")

# Or tag-based
def invalidate_user_data(user_id):
    keys = redis.keys(f"user:{user_id}:*")
    if keys:
        redis.delete(*keys)
```

### 4. Event-Driven Invalidation

Via message queue.

```python
# On database change
def on_user_updated(event):
    user_id = event.user_id
    redis.delete(f"user:{user_id}")
    redis.delete(f"user:{user_id}:profile")

# Publish event
def update_user(user_id, data):
    db.update_user(user_id, data)
    pubsub.publish("user:updated", {"user_id": user_id})
```

## Python Implementation

### Basic Client

```python
from redis import Redis
import json

class Cache:
    def __init__(self, host="localhost", port=6379):
        self.redis = Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
    
    def get(self, key, default=None):
        value = self.redis.get(key)
        return json.loads(value) if value else default
    
    def set(self, key, value, ttl=3600):
        self.redis.setex(key, ttl, json.dumps(value))
    
    def delete(self, key):
        self.redis.delete(key)
    
    def clear(self):
        self.redis.flushdb()

# Usage
cache = Cache()
cache.set("user:123", {"name": "John"}, ttl=3600)
user = cache.get("user:123")
```

### Decorator Pattern

```python
from functools import wraps
import json

def cached(ttl=3600, key_prefix=""):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            
            # Try cache
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            redis.setex(cache_key, ttl, json.dumps(result))
            
            return result
        
        return wrapper
    return decorator

# Usage
@cached(ttl=3600, key_prefix="user")
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

### Pipeline (Batch Operations)

```python
# Multiple operations at once (atomic)
pipe = redis.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.incr("counter")
pipe.execute()
```

### Connection Pool

```python
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host="localhost",
    port=6379,
    max_connections=50
)

redis = Redis(connection_pool=pool)
```

## Best Practices

✅ **Set TTL on all keys** — Prevent memory bloat
✅ **Use naming conventions** — `namespace:entity:id:field`
✅ **Handle cache misses** — Fallback to database
✅ **Pipeline operations** — Batch writes
✅ **Monitor memory** — Watch for eviction
✅ **Use appropriate structure** — String vs Hash vs List
✅ **Invalidate strategically** — TTL or event-driven
✅ **Test cache behavior** — Hit/miss rates

## Common Mistakes

❌ **No TTL** → Memory fills, keys never expire
❌ **Cache stampede** → All requests hit DB on miss
❌ **Stale data** → Update DB but forget to invalidate cache
❌ **Large values** → Serialization overhead
❌ **Synchronous invalidation** → Slow updates

## Monitoring

```bash
# Redis CLI
redis-cli

# Check memory
INFO memory

# Check eviction stats
INFO stats

# Monitor in real-time
MONITOR

# Check key space
DBSIZE

# See key patterns
KEYS user:*
```

## File Structure

```
redis-caching/
├── README.md                 # This file
├── DATA_STRUCTURES.md       # Detailed structure docs
├── PATTERNS_GUIDE.md        # Caching patterns (10+)
├── INVALIDATION_GUIDE.md    # Cache invalidation strategies
├── IMPLEMENTATION.md        # Python redis-py guide
├── MONITORING_GUIDE.md      # Performance monitoring
├── BEST_PRACTICES.md        # Production patterns
├── examples/
│   ├── basic_cache.py
│   ├── cache_decorator.py
│   ├── session_store.py
│   ├── rate_limiting.py
│   └── leaderboard.py
└── requirements.txt
```

## Quick Start

```bash
# Install
pip install redis

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:latest

# Use
from redis import Redis
redis = Redis()
redis.set("key", "value")
redis.get("key")
```

## Resources

- [Redis Official Docs](https://redis.io/documentation)
- [redis-py Docs](https://redis-py.readthedocs.io/)
- [Redis Commands](https://redis.io/commands/)
- See **DATA_STRUCTURES.md** for details
- See **PATTERNS_GUIDE.md** for caching strategies

---

**Start with DATA_STRUCTURES.md** for comprehensive examples.
