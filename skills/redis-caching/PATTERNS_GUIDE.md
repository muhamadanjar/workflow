# Caching Patterns Guide

10+ proven patterns. Choose based on use case.

## 1. Cache-Aside (Lazy Loading)

**Best for:** General caching, unpredictable access

```python
def get_product(product_id):
    # Check cache
    cached = redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss → fetch from database
    product = db.get_product(product_id)
    
    # Cache for 1 hour
    redis.setex(f"product:{product_id}", 3600, json.dumps(product))
    
    return product
```

**Flow:** Request → Cache? → Database → Cache → Response
**Pros:** Simple, flexible
**Cons:** Cache miss latency

---

## 2. Write-Through

**Best for:** Consistency critical (orders, payments)

```python
def update_product(product_id, data):
    # Update database first
    db.update_product(product_id, data)
    
    # Then update cache (guaranteed in sync)
    redis.setex(f"product:{product_id}", 3600, json.dumps(data))
    
    return data
```

**Flow:** Write → Database → Cache → Response
**Pros:** Cache always consistent
**Cons:** Slower writes

---

## 3. Write-Behind (Write-Back)

**Best for:** High throughput, eventual consistency OK

```python
# Async task queue
from rq import Queue

q = Queue(connection=redis)

def update_product(product_id, data):
    # Update cache immediately (fast)
    redis.setex(f"product:{product_id}", 3600, json.dumps(data))
    
    # Queue database update
    q.enqueue(db.update_product, product_id, data)
    
    return {"status": "accepted"}

# Background worker
def process_updates():
    while True:
        job = q.dequeue()
        if job:
            job.func(*job.args)
```

**Flow:** Write → Cache → Queue → Response (Database updates async)
**Pros:** Fast, high throughput
**Cons:** Data loss risk, eventual consistency

---

## 4. Refresh-Ahead (Proactive Refresh)

**Best for:** Popular items, predictable patterns

```python
def refresh_cache():
    # Periodically refresh trending items
    trending = db.get_trending_products(limit=100)
    
    for product in trending:
        redis.setex(
            f"product:{product.id}",
            300,  # 5 min
            json.dumps(product)
        )

# Run every minute
scheduler.every(1).minutes.do(refresh_cache)
```

**Flow:** Scheduled → Cache refresh → Always hot
**Pros:** No cache misses for popular items
**Cons:** Needs predictability

---

## 5. Sibling Cache

**Best for:** Related entities (user + profile + settings)

```python
def get_user_complete(user_id):
    # Try get all siblings
    user = redis.get(f"user:{user_id}")
    profile = redis.get(f"profile:{user_id}")
    settings = redis.get(f"settings:{user_id}")
    
    if not all([user, profile, settings]):
        # Fetch all from DB
        data = db.fetch_user_complete(user_id)
        
        # Cache all together with same TTL
        pipe = redis.pipeline()
        pipe.setex(f"user:{user_id}", 3600, json.dumps(data['user']))
        pipe.setex(f"profile:{user_id}", 3600, json.dumps(data['profile']))
        pipe.setex(f"settings:{user_id}", 3600, json.dumps(data['settings']))
        pipe.execute()
    
    return {
        'user': json.loads(user),
        'profile': json.loads(profile),
        'settings': json.loads(settings)
    }
```

**Pros:** Fetch all related data together
**Cons:** Complex invalidation

---

## 6. Cache Invalidation Patterns

### Time-Based (TTL)

```python
# Auto-expire after 1 hour
redis.setex("product:123", 3600, data)

# Update expiry
redis.expire("product:123", 1800)
```

### Manual Invalidation

```python
def update_product(product_id, data):
    db.update_product(product_id, data)
    redis.delete(f"product:{product_id}")  # Manual delete
```

### Pattern Invalidation

```python
def invalidate_user_cache(user_id):
    keys = redis.keys(f"user:{user_id}:*")
    if keys:
        redis.delete(*keys)
```

### Event-Driven Invalidation

```python
# Subscribe to database changes
def on_product_updated(event):
    redis.delete(f"product:{event.product_id}")

# Publish from database trigger
pubsub.subscribe('product:updated')
```

---

## 7. Session Caching

**Best for:** Web sessions, user state

```python
import uuid

def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "ip": request.remote_addr
    }
    
    # Session expires in 24 hours
    redis.setex(f"session:{session_id}", 86400, json.dumps(session_data))
    
    return session_id

def get_session(session_id):
    data = redis.get(f"session:{session_id}")
    if data:
        # Refresh TTL on access
        redis.expire(f"session:{session_id}", 86400)
        return json.loads(data)
    return None
```

---

## 8. Rate Limiting

**Best for:** API rate limiting, brute force protection

```python
def check_rate_limit(user_id, limit=100, window=3600):
    key = f"rate_limit:{user_id}"
    count = redis.incr(key)
    
    if count == 1:
        redis.expire(key, window)
    
    if count > limit:
        return False  # Exceeded limit
    
    return True  # OK

# Usage
@app.route("/api/data")
def api_endpoint():
    if not check_rate_limit(current_user.id):
        return {"error": "Rate limit exceeded"}, 429
    
    return get_data()
```

---

## 9. Leaderboard

**Best for:** Rankings, scores, competitions

```python
# Add scores
redis.zadd("leaderboard", {
    "player1": 1000,
    "player2": 950,
    "player3": 1100
})

# Update score
redis.zincrby("leaderboard", 10, "player1")  # Now 1010

# Get top 10
top10 = redis.zrange("leaderboard", 0, 9, rev=True, withscores=True)
# [(player3, 1100), (player1, 1010), (player2, 950)]

# Get player rank
rank = redis.zrevrank("leaderboard", "player1")  # 1 (0-indexed)

# Get players in score range
high_scorers = redis.zrangebyscore("leaderboard", 1000, 10000)
```

---

## 10. Counter/Analytics

**Best for:** Page views, metrics, aggregations

```python
# Increment counter
redis.incr("posts:total_count")
redis.incr(f"post:{post_id}:views")

# Atomic operations
redis.hincrby(f"user:{user_id}:stats", "post_count", 1)
redis.hincrby(f"user:{user_id}:stats", "comment_count", 1)

# Get stats
stats = redis.hgetall(f"user:{user_id}:stats")
```

---

## 11. Publish/Subscribe

**Best for:** Real-time notifications, live updates

```python
# Publish
redis.publish("user:123:notifications", json.dumps({
    "type": "new_message",
    "from": "user456"
}))

# Subscribe
def listen_notifications(user_id):
    pubsub = redis.pubsub()
    pubsub.subscribe(f"user:{user_id}:notifications")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            print(f"Notification: {data}")
```

---

## 12. Distributed Lock

**Best for:** Concurrent access control

```python
import uuid
import time

def acquire_lock(resource, timeout=10):
    lock_id = str(uuid.uuid4())
    
    # Acquire lock (only if not exists)
    acquired = redis.set(
        f"lock:{resource}",
        lock_id,
        ex=timeout,
        nx=True  # Only if not exists
    )
    
    return lock_id if acquired else None

def release_lock(resource, lock_id):
    # Only release if we own the lock
    if redis.get(f"lock:{resource}") == lock_id:
        redis.delete(f"lock:{resource}")

# Usage
lock_id = acquire_lock("critical_resource")
if lock_id:
    try:
        # Do critical work
        do_critical_work()
    finally:
        release_lock("critical_resource", lock_id)
else:
    print("Could not acquire lock")
```

---

## Pattern Selection Guide

| Requirement | Pattern |
|-------------|---------|
| Simple caching | Cache-Aside |
| Consistency critical | Write-Through |
| High throughput | Write-Behind |
| Popular items | Refresh-Ahead |
| Related data | Sibling |
| Web sessions | Session Cache |
| API protection | Rate Limiting |
| Rankings | Leaderboard |
| Live updates | Pub/Sub |
| Concurrency | Distributed Lock |

---

## Anti-Patterns (Avoid)

❌ **Cache Stampede** — All threads hit DB on miss
```python
# Bad: No locking
if not redis.get(key):
    value = expensive_query()  # 1000 threads do this!
    redis.set(key, value)
```

❌ **Cache Penetration** — Request for non-existent key
```python
# Good: Cache None for missing items
result = redis.get(f"user:{id}")
if result is None:
    user = db.get_user(id)
    if not user:
        redis.setex(f"user:{id}", 300, "NONE")  # Cache miss too
        return None
```

❌ **Stale Data** — Forget to invalidate on update
```python
# Always invalidate on write
def update_user(user_id, data):
    db.update(user_id, data)
    redis.delete(f"user:{user_id}")  # Don't forget!
```

---

See **INVALIDATION_GUIDE.md** for detailed cache invalidation strategies.
