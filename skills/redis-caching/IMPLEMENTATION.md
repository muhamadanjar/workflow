# Redis Implementation Guide (Python)

Production-ready Redis patterns using redis-py.

## Installation

```bash
pip install redis
```

## Connection Management

### Basic Connection

```python
from redis import Redis

redis = Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30
)

# Test connection
redis.ping()  # Returns True
```

### Connection Pool

```python
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50,
    retry_on_timeout=True
)

redis = Redis(connection_pool=pool)
```

### Connection String

```python
from redis import from_url

redis = from_url(
    'redis://localhost:6379/0',
    encoding='utf-8',
    decode_responses=True
)
```

## Cache Wrapper Class

```python
import json
import logging
from typing import Any, Optional
from datetime import timedelta
from redis import Redis

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_client: Redis = None, default_ttl: int = 3600):
        self.redis = redis_client or Redis(decode_responses=True)
        self.default_ttl = default_ttl
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return default
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return bool(self.redis.exists(key))
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds"""
        return self.redis.ttl(key)
    
    def clear(self) -> bool:
        """Clear entire cache"""
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

# Usage
cache = RedisCache()
cache.set("user:123", {"name": "John"}, ttl=3600)
user = cache.get("user:123")
```

## Caching Decorator

```python
from functools import wraps
import json

def cached(ttl=3600, key_prefix=""):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k,v in kwargs.items())}"
            
            # Try cache
            cached_value = redis.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache result
            redis.setex(cache_key, ttl, json.dumps(result, default=str))
            
            return result
        
        return wrapper
    return decorator

# Usage
@cached(ttl=3600, key_prefix="user")
def get_user(user_id):
    return db.get_user(user_id)

@cached(ttl=300, key_prefix="products")
def get_trending_products():
    return db.get_trending_products()
```

## Session Management

```python
import uuid
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, redis_client: Redis, ttl: int = 86400):
        self.redis = redis_client
        self.ttl = ttl
    
    def create(self, user_id: str, data: dict = None) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            **(data or {})
        }
        
        self.redis.setex(
            f"session:{session_id}",
            self.ttl,
            json.dumps(session_data)
        )
        
        return session_id
    
    def get(self, session_id: str) -> Optional[dict]:
        data = self.redis.get(f"session:{session_id}")
        if data:
            # Refresh TTL on access
            self.redis.expire(f"session:{session_id}", self.ttl)
            return json.loads(data)
        return None
    
    def delete(self, session_id: str) -> bool:
        return bool(self.redis.delete(f"session:{session_id}"))
    
    def invalidate_user(self, user_id: str) -> int:
        # Delete all sessions for user
        keys = self.redis.keys(f"session:*")
        count = 0
        
        for key in keys:
            session_data = self.redis.get(key)
            if session_data:
                data = json.loads(session_data)
                if data.get("user_id") == user_id:
                    self.redis.delete(key)
                    count += 1
        
        return count

# Usage
sessions = SessionManager(redis)
session_id = sessions.create("user123", {"ip": "192.168.1.1"})
session = sessions.get(session_id)
```

## Rate Limiting

```python
from time import time

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if request is allowed"""
        current_count = self.redis.incr(key)
        
        if current_count == 1:
            # First request in window
            self.redis.expire(key, window_seconds)
        
        return current_count <= max_requests
    
    def get_remaining(self, key: str, max_requests: int) -> int:
        """Get remaining requests in window"""
        current = int(self.redis.get(key) or 0)
        return max(0, max_requests - current)

# Usage
limiter = RateLimiter(redis)

def api_endpoint(user_id):
    if not limiter.is_allowed(f"api:{user_id}", max_requests=100, window_seconds=3600):
        return {"error": "Rate limit exceeded"}, 429
    
    remaining = limiter.get_remaining(f"api:{user_id}", max_requests=100)
    return {"data": get_data(), "remaining": remaining}
```

## Leaderboard

```python
class Leaderboard:
    def __init__(self, redis_client: Redis, key: str):
        self.redis = redis_client
        self.key = key
    
    def add_score(self, player: str, score: float) -> float:
        return self.redis.zadd(self.key, {player: score})
    
    def increment_score(self, player: str, increment: float) -> float:
        return self.redis.zincrby(self.key, increment, player)
    
    def get_score(self, player: str) -> Optional[float]:
        return self.redis.zscore(self.key, player)
    
    def get_rank(self, player: str) -> Optional[int]:
        # Returns 0-indexed rank (higher scores = lower rank number)
        rank = self.redis.zrevrank(self.key, player)
        return rank + 1 if rank is not None else None
    
    def get_top_n(self, n: int = 10) -> list:
        """Get top N players with scores"""
        return self.redis.zrange(
            self.key,
            0,
            n - 1,
            rev=True,
            withscores=True
        )
    
    def get_around_player(self, player: str, radius: int = 5) -> list:
        """Get player's rank and surrounding players"""
        rank = self.get_rank(player)
        if rank is None:
            return []
        
        start = max(0, rank - radius - 1)
        end = rank + radius - 1
        
        return self.redis.zrange(
            self.key,
            start,
            end,
            rev=True,
            withscores=True
        )

# Usage
leaderboard = Leaderboard(redis, "game:leaderboard")
leaderboard.add_score("player1", 1000)
leaderboard.increment_score("player1", 50)
top_10 = leaderboard.get_top_n(10)
```

## Batch Operations (Pipeline)

```python
def batch_cache_set(cache_dict: dict, ttl: int = 3600):
    """Set multiple keys atomically"""
    pipe = redis.pipeline()
    
    for key, value in cache_dict.items():
        pipe.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    
    pipe.execute()

def batch_cache_delete(keys: list) -> int:
    """Delete multiple keys"""
    if not keys:
        return 0
    
    return redis.delete(*keys)

def batch_cache_get(keys: list) -> dict:
    """Get multiple keys at once"""
    pipe = redis.pipeline()
    
    for key in keys:
        pipe.get(key)
    
    results = pipe.execute()
    
    return {
        key: json.loads(value) if value else None
        for key, value in zip(keys, results)
    }

# Usage
cache_data = {
    "user:1": {"name": "Alice"},
    "user:2": {"name": "Bob"},
    "user:3": {"name": "Charlie"}
}
batch_cache_set(cache_data)

users = batch_cache_get(["user:1", "user:2", "user:3"])
```

## Error Handling

```python
from redis.exceptions import RedisError, ConnectionError, TimeoutError

def safe_cache_operation(key: str, operation, *args, **kwargs):
    """Execute cache operation with error handling"""
    try:
        return operation(key, *args, **kwargs)
    except ConnectionError:
        logger.error(f"Redis connection error for {key}")
        return None
    except TimeoutError:
        logger.error(f"Redis timeout for {key}")
        return None
    except RedisError as e:
        logger.error(f"Redis error for {key}: {e}")
        return None

# Usage
def get_user_safe(user_id):
    cached = safe_cache_operation(
        f"user:{user_id}",
        redis.get,
        user_id
    )
    
    if cached:
        return json.loads(cached)
    
    # Fallback to database
    return db.get_user(user_id)
```

## Testing

```python
import pytest
from fakeredis import FakeRedis

@pytest.fixture
def fake_redis():
    return FakeRedis(decode_responses=True)

def test_cache_set_get(fake_redis):
    cache = RedisCache(fake_redis)
    
    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")
    
    assert result == {"data": "value"}

def test_cache_expire(fake_redis):
    cache = RedisCache(fake_redis)
    
    cache.set("test_key", "value", ttl=1)
    assert cache.exists("test_key")
    
    # Simulate expiry
    fake_redis.expire("test_key", -1)
    assert not cache.exists("test_key")
```

---

See **PATTERNS_GUIDE.md** for real-world caching patterns.
