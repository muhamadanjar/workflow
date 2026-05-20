# Cache Invalidation Strategies

Detailed patterns for keeping cache consistent with source of truth.

## 1. Time-Based (TTL)

Simplest: let cache expire after fixed duration.

```python
from redis import Redis
import json

redis = Redis(decode_responses=True)

# ✅ Set expiry at write
def cache_user(user_id, user_data):
    redis.setex(
        f"user:{user_id}",
        3600,  # 1 hour
        json.dumps(user_data)
    )

# ✅ Or set expiry later
redis.set(f"user:{user_id}", json.dumps(user_data))
redis.expire(f"user:{user_id}", 3600)

# ✅ Check remaining TTL
ttl = redis.ttl(f"user:{user_id}")  # Seconds remaining
if ttl < 0:
    print("Key expired or has no expiry")
```

### Pros/Cons

| | |
|---|---|
| ✅ Simple, no dependency tracking | ❌ Stale data until TTL expires |
| ✅ Memory safe (auto-cleanup) | ❌ Wrong TTL = miss or waste |
| ✅ Fault tolerant | ❌ Can't invalidate early |

### When to Use

- Read-heavy, infrequent updates (product listings)
- Tolerate brief staleness (seconds-minutes)
- Simple data (no dependencies)

---

## 2. Manual Invalidation

Delete from cache when data changes.

```python
# ✅ Delete on update
def update_user(user_id, new_data):
    db.update_user(user_id, new_data)
    redis.delete(f"user:{user_id}")  # Immediately stale

# ✅ Delete on delete
def delete_user(user_id):
    db.delete_user(user_id)
    redis.delete(f"user:{user_id}")

# ✅ Or invalidate before write (preemptive)
def create_user(user_data):
    user = db.create_user(user_data)
    redis.delete("users:list")  # Invalidate list cache
    return user
```

### Pattern Invalidation

```python
# ✅ Delete all related keys
def update_user_profile(user_id):
    db.update_user_profile(user_id)
    
    # Delete all user-related cache
    keys_to_delete = redis.keys(f"user:{user_id}:*")
    if keys_to_delete:
        redis.delete(*keys_to_delete)

# ✅ Or use tag-based delete
def delete_by_pattern(pattern):
    """Delete all keys matching pattern"""
    for key in redis.scan_iter(match=pattern, count=1000):
        redis.delete(key)

delete_by_pattern("user:123:*")
delete_by_pattern("cache:product:*")
```

### Pros/Cons

| | |
|---|---|
| ✅ Always fresh (no stale data) | ❌ Manual: easy to forget |
| ✅ No staleness period | ❌ Complex invalidation logic |
| ✅ Fine-grained control | ❌ Might invalidate too much |

### When to Use

- Critical data (orders, payments, inventory)
- Frequent updates (prices, stock levels)
- Consistent behavior required

---

## 3. Event-Driven Invalidation

React to data change events.

```python
import json
from redis import Redis

redis = Redis(decode_responses=True)

# Publish event after update
def update_product(product_id, new_data):
    db.update_product(product_id, new_data)
    
    # Publish event
    redis.publish("product:updated", json.dumps({
        "product_id": product_id,
        "timestamp": time.time()
    }))

# Subscribe and invalidate
def listen_for_updates():
    pubsub = redis.pubsub()
    pubsub.subscribe("product:updated")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            product_id = data['product_id']
            
            # Invalidate
            redis.delete(f"product:{product_id}")
            redis.delete(f"cache:product:{product_id}:price")

# Or use message queue
from app.tasks import celery_app

@celery_app.task
def on_product_updated(product_id):
    """Async invalidation task"""
    redis.delete(f"product:{product_id}")
    redis.delete(f"cache:product:{product_id}:*")
```

### Database Triggers

```python
# PostgreSQL trigger publishes event
CREATE FUNCTION product_updated_trigger() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('product_updated', json_build_object(
        'product_id', NEW.id,
        'timestamp', EXTRACT(EPOCH FROM now())
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER product_update_notify
AFTER UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION product_updated_trigger();

# Python listens to notifications
import psycopg2
import select

conn = psycopg2.connect("dbname=mydb")
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()
cur.execute("LISTEN product_updated")

while True:
    if select.select([conn], [], [], 5) == ([], [], []):
        pass
    else:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            data = json.loads(notify.payload)
            redis.delete(f"product:{data['product_id']}")
```

### Pros/Cons

| | |
|---|---|
| ✅ Reactive (no delay) | ❌ Complex setup (pub/sub, listeners) |
| ✅ Scalable (many invalidators) | ❌ Message delivery not guaranteed |
| ✅ Decoupled (services don't know) | ❌ Hard to debug |

### When to Use

- Distributed systems (multiple services)
- Real-time requirements (live dashboards)
- Audit trail needed

---

## 4. Lazy Invalidation

Check freshness on read.

```python
# Add "version" field to detect stale cache
def get_user_lazy(user_id):
    cached = redis.get(f"user:{user_id}")
    if not cached:
        return fetch_and_cache(user_id)
    
    cached_data = json.loads(cached)
    db_user = db.get_user(user_id)
    
    # Check if versions match
    if cached_data.get('version') != db_user.version:
        # Stale, update cache
        redis.setex(f"user:{user_id}", 3600, json.dumps(db_user.to_dict()))
        return db_user.to_dict()
    
    return cached_data

# Or use checksum
import hashlib

def get_product_lazy(product_id):
    cached = redis.get(f"product:{product_id}")
    if not cached:
        return fetch_and_cache(product_id)
    
    cached_data = json.loads(cached)
    db_product = db.get_product(product_id)
    
    current_checksum = hashlib.md5(
        json.dumps(db_product.to_dict()).encode()
    ).hexdigest()
    
    if cached_data.get('_checksum') != current_checksum:
        # Stale
        updated = db_product.to_dict()
        updated['_checksum'] = current_checksum
        redis.setex(f"product:{product_id}", 3600, json.dumps(updated))
        return updated
    
    return cached_data
```

### Pros/Cons

| | |
|---|---|
| ✅ Handles missed invalidations | ❌ Extra read on every hit |
| ✅ Fault tolerant | ❌ Still serves stale briefly |
| ✅ Simple to implement | ❌ More load on DB |

### When to Use

- Safety margin needed (prevent stale data)
- Occasional inconsistency tolerable
- Simple integrity check possible (version field)

---

## 5. Dependent Cache Groups

Invalidate related keys together.

```python
# Track dependencies
CACHE_DEPENDENCIES = {
    f"user:{user_id}": [
        f"user:{user_id}:profile",
        f"user:{user_id}:settings",
        f"user:{user_id}:notifications"
    ],
    "products:trending": [
        "products:trending:count",
        "products:trending:updated_at"
    ]
}

def invalidate_with_dependents(key):
    """Invalidate key and all dependents"""
    redis.delete(key)
    
    dependents = CACHE_DEPENDENCIES.get(key, [])
    if dependents:
        redis.delete(*dependents)
    
    # Also clear reverse dependencies
    for parent, children in CACHE_DEPENDENCIES.items():
        if key in children:
            redis.delete(parent)

# Usage
def update_user_profile(user_id):
    db.update_user_profile(user_id)
    invalidate_with_dependents(f"user:{user_id}:profile")
```

### Cache Groups

```python
# Use sets to track group members
def add_to_cache_group(group_name, key):
    """Add key to invalidation group"""
    redis.sadd(f"cache_group:{group_name}", key)

def invalidate_group(group_name):
    """Invalidate entire group"""
    keys = redis.smembers(f"cache_group:{group_name}")
    if keys:
        redis.delete(*keys, f"cache_group:{group_name}")

# Usage
def cache_user_data(user_id, data):
    key = f"user:{user_id}:profile"
    redis.setex(key, 3600, json.dumps(data))
    add_to_cache_group(f"user:{user_id}", key)

def update_user(user_id, new_data):
    db.update_user(user_id, new_data)
    invalidate_group(f"user:{user_id}")  # Clear all user-related
```

### Pros/Cons

| | |
|---|---|
| ✅ Atomic group invalidation | ❌ Need to track dependencies |
| ✅ Prevent orphaned cache | ❌ Extra bookkeeping |
| ✅ Easier than pattern delete | ❌ Must update group on cache set |

### When to Use

- Related data often changes together (user + profile + settings)
- Prevent partial invalidations
- Clear, defined relationships

---

## 6. Bloom Filter Invalidation

Probabilistic freshness check.

```python
from pybloom_live import BloomFilter
import json

# Maintain filter of "valid" keys
valid_keys = BloomFilter(capacity=100000, error_rate=0.001)

def mark_invalid(key):
    """Mark key as invalid (remove from bloom)"""
    # Note: Bloom filters don't support removal
    # Instead, keep separate "invalid" set
    redis.sadd("invalidated_keys", key)

def is_valid(key):
    """Check if key is valid (probably)"""
    # If in invalid set, definitely invalid
    if redis.sismember("invalidated_keys", key):
        return False
    # If not in bloom, definitely invalid
    if key not in valid_keys:
        return False
    # Probably valid
    return True

def get_cached_with_bloom(key):
    if is_valid(key):
        return redis.get(key)
    return None

def set_cached_with_bloom(key, value):
    redis.set(key, value)
    valid_keys.add(key)
    redis.srem("invalidated_keys", key)
```

### Pros/Cons

| | |
|---|---|
| ✅ Memory efficient | ❌ False positives possible |
| ✅ Fast membership test | ❌ Can't remove from Bloom filter |
| ✅ Scales well | ❌ Complex for little benefit |

### When to Use

- Huge key spaces (billions of keys)
- Memory constraints severe
- Some stale data acceptable

---

## 7. Conditional Refresh

Update cache if conditions met.

```python
# Refresh only if conditions met
def conditional_refresh(key, predicate_fn):
    """Refresh cache if predicate is true"""
    cached = redis.get(key)
    
    if cached is None:
        # Cache miss, fetch fresh
        return fetch_and_cache(key)
    
    cached_data = json.loads(cached)
    
    # Check if refresh needed
    if predicate_fn(cached_data):
        # Refresh needed
        fresh_data = fetch_from_db(key)
        redis.setex(key, 3600, json.dumps(fresh_data))
        return fresh_data
    
    # Cache still valid
    return cached_data

# Usage: Refresh if cache > 5 minutes old
def get_user_conditional(user_id):
    def needs_refresh(cached):
        age = time.time() - cached.get('cached_at', 0)
        return age > 300  # 5 minutes
    
    return conditional_refresh(f"user:{user_id}", needs_refresh)

# Or: Refresh if version field changed
def get_product_version_check(product_id):
    def version_stale(cached):
        db_version = db.get_version(product_id)
        return cached.get('version') != db_version
    
    return conditional_refresh(f"product:{product_id}", version_stale)
```

### Pros/Cons

| | |
|---|---|
| ✅ Fine-grained control | ❌ Extra DB calls to check |
| ✅ Deferred invalidation | ❌ Complex logic |
| ✅ Reduces wasted cache | ❌ Hard to test |

### When to Use

- Inexpensive version checks possible
- Bandwidth/cost constrained (check < fetch)
- Refresh expensive (compress, process)

---

## 8. Background Refresh (Refresh-Ahead)

Pre-invalidate before expiry.

```python
from celery import shared_task

# ✅ Refresh cache before it expires
@shared_task
def refresh_trending_products():
    """Refresh popular products before cache expires"""
    trending = db.get_trending_products(limit=100)
    
    for product in trending:
        redis.setex(
            f"product:{product.id}",
            300,  # 5 minutes
            json.dumps(product.to_dict())
        )
    
    logger.info(f"Refreshed {len(trending)} trending products")

# Schedule periodic refresh
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-trending': {
        'task': 'tasks.refresh_trending_products',
        'schedule': crontab(minute='*/1')  # Every minute
    }
}

# Or: Refresh-on-access
def get_trending_with_refresh(product_id):
    cached = redis.get(f"product:{product_id}")
    
    if not cached:
        # Miss, fetch fresh
        product = db.get_product(product_id)
        redis.setex(f"product:{product_id}", 300, json.dumps(product.to_dict()))
        return product
    
    # Check TTL, refresh if < 60s left
    ttl = redis.ttl(f"product:{product_id}")
    if ttl < 60:  # Less than 1 minute left
        refresh_task.delay(product_id)  # Queue async refresh
    
    return json.loads(cached)
```

### Pros/Cons

| | |
|---|---|
| ✅ No cache misses for popular items | ❌ Wasted refreshes if unused |
| ✅ Predictable latency | ❌ Schedule complexity |
| ✅ Works with TTL approach | ❌ Need background workers |

### When to Use

- Popular, high-traffic items (trending, featured)
- Predictable access patterns
- Can afford periodic refreshes

---

## 9. Write-Through Pattern

Update cache first, then DB.

```python
# ✅ Always consistent (cache = DB)
def update_user_write_through(user_id, new_data):
    # Update cache first
    cache_key = f"user:{user_id}"
    redis.setex(cache_key, 3600, json.dumps(new_data))
    
    try:
        # Then update DB
        db.update_user(user_id, new_data)
    except Exception as e:
        # If DB fails, rollback cache
        redis.delete(cache_key)
        raise

# ✅ Or: Use transaction to ensure consistency
def update_user_transactional(user_id, new_data):
    try:
        db.begin_transaction()
        db.update_user(user_id, new_data)
        
        # Commit in DB first
        db.commit_transaction()
        
        # Then cache (if DB succeeds)
        redis.setex(f"user:{user_id}", 3600, json.dumps(new_data))
    except Exception as e:
        db.rollback_transaction()
        raise
```

### Pros/Cons

| | |
|---|---|
| ✅ Cache always consistent | ❌ Slower writes (both operations) |
| ✅ No stale data | ❌ Cache failure = whole operation fails |
| ✅ Simple invalidation (never stale) | ❌ Network overhead |

### When to Use

- Consistency critical (payments, inventory)
- Writes less frequent than reads
- Can accept slower writes

---

## Comparison Table

| Strategy | Staleness | Freshness | Complexity | Memory | Use Case |
|---|---|---|---|---|---|
| **TTL** | High | Low | Low | Low | General caching |
| **Manual** | None | High | Medium | Medium | Critical data |
| **Event-Driven** | Very Low | High | High | High | Distributed systems |
| **Lazy** | Low | High | Medium | Low | Safety margin |
| **Groups** | None | High | Medium | Medium | Related data |
| **Bloom** | Medium | Medium | High | Very Low | Huge key spaces |
| **Conditional** | Low | High | High | Medium | Complex rules |
| **Refresh-Ahead** | None | High | High | High | Trending items |
| **Write-Through** | None | High | Medium | Medium | Critical updates |

---

## Decision Tree

```
Is data frequently updated?
├─ No (< once/hour)
│  └─ Use TTL (simple, memory safe)
├─ Yes (> once/minute)
│  └─ Is consistency critical?
│     ├─ Yes (payments, inventory)
│     │  └─ Use Manual + Write-Through
│     ├─ No (user profile, preferences)
│     │  ├─ Is setup effort acceptable?
│     │  │  ├─ Yes → Use Event-Driven
│     │  │  ├─ No → Use Manual
```

---

## Summary

**Start simple:** TTL handles 80% of cases. Add complexity only when needed.

**Default strategy:** TTL + Manual invalidation on update.

**For critical data:** Write-Through or Event-Driven.

**For performance:** Refresh-Ahead or Groups.

**For resilience:** Lazy invalidation + version checks.

