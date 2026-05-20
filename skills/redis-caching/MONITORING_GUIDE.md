# Redis Monitoring & Performance

Production monitoring, debugging, performance tuning.

## Connection Monitoring

### Connection Pool Stats

```python
from redis import Redis, ConnectionPool

pool = ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50
)
redis = Redis(connection_pool=pool)

def get_pool_stats():
    """Monitor connection pool health"""
    return {
        'connection_count': pool.connection_count,
        'pid': pool.pid,
        'reset_count': pool.reset_count
    }

print(get_pool_stats())
```

### Connection Timeout Tuning

```python
redis = Redis(
    host='localhost',
    port=6379,
    socket_connect_timeout=5,      # Connection timeout
    socket_keepalive=True,         # Keep alive
    socket_keepalive_options={},   # Platform-specific
    health_check_interval=30,      # Health check
    retry_on_timeout=True          # Retry on timeout
)
```

## Memory Management

### Memory Usage

```bash
# Redis CLI
redis-cli INFO memory

# Output example:
# used_memory: 1048576 bytes
# used_memory_human: 1M
# used_memory_rss: 2097152 bytes
# used_memory_peak: 1048576 bytes
# used_memory_peak_human: 1M
```

### Memory by Key

```python
from redis import Redis
import json

redis = Redis(decode_responses=True)

def analyze_memory():
    """Estimate memory usage per key"""
    info = redis.info('memory')
    
    # Scan all keys
    total_size = 0
    key_sizes = {}
    
    for key in redis.scan_iter(match='*', count=1000):
        size = redis.memory_usage(key)
        if size:
            key_sizes[key] = size
            total_size += size
    
    # Top 10 memory consumers
    top_keys = sorted(key_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'total_memory': info['used_memory_human'],
        'total_key_memory': total_size,
        'top_keys': top_keys
    }

print(analyze_memory())
```

### Eviction Policies

```bash
# Configure in redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru

# Policies:
# noeviction        - No eviction, error on full
# allkeys-lru       - Remove least recently used
# allkeys-lfu       - Remove least frequently used
# volatile-lru      - LRU among keys with TTL
# volatile-lfu      - LFU among keys with TTL
# volatile-ttl      - Remove keys with shortest TTL
# volatile-random   - Random key with TTL
```

```python
# Check current policy
redis.config_get('maxmemory-policy')

# Set at runtime (temporary)
redis.config_set('maxmemory-policy', 'allkeys-lru')
```

## Performance Metrics

### Command Latency

```python
import time
from redis import Redis

redis = Redis()

def measure_latency(command, *args, iterations=1000):
    """Measure command latency"""
    start = time.perf_counter()
    
    for _ in range(iterations):
        redis.execute_command(command, *args)
    
    end = time.perf_counter()
    avg_latency = (end - start) / iterations * 1000  # ms
    
    return avg_latency

# Benchmark common operations
print(f"GET latency: {measure_latency('GET', 'test_key'):.3f}ms")
print(f"SET latency: {measure_latency('SET', 'test_key', 'value'):.3f}ms")
print(f"INCR latency: {measure_latency('INCR', 'counter'):.3f}ms")
```

### Cache Hit Ratio

```python
from redis import Redis

redis = Redis()

def get_cache_stats():
    """Cache hit/miss ratio"""
    info = redis.info('stats')
    
    hits = info['keyspace_hits']
    misses = info['keyspace_misses']
    total = hits + misses
    
    hit_ratio = (hits / total * 100) if total > 0 else 0
    
    return {
        'hits': hits,
        'misses': misses,
        'hit_ratio': f"{hit_ratio:.2f}%",
        'total_queries': total
    }

stats = get_cache_stats()
print(f"Cache hit ratio: {stats['hit_ratio']}")
```

### Slow Log

```python
redis = Redis()

# View slow log (commands > 10ms)
slow_queries = redis.slowlog_get(10)

for query in slow_queries:
    log_id, timestamp, duration_micros, command, client, name = query
    print(f"{duration_micros/1000:.2f}ms - {' '.join(str(c) for c in command)}")

# Clear slow log
redis.slowlog_reset()

# Configure threshold (redis.conf)
# slowlog-log-slower-than 10000  # Microseconds
# slowlog-max-len 128
```

## Database Monitoring

### Keyspace Stats

```bash
# CLI
redis-cli INFO keyspace

# Output:
# db0: keys=1000, expires=500, avg_ttl=3600000
# db1: keys=200, expires=50, avg_ttl=1800000
```

```python
def keyspace_report():
    """Detailed keyspace analysis"""
    info = redis.info('keyspace')
    
    for db, stats in info.items():
        if not db.startswith('db'):
            continue
        
        keys = stats['keys']
        expires = stats['expires']
        avg_ttl = stats['avg_ttl']
        
        print(f"{db}: {keys} keys, {expires} expire in {avg_ttl}ms avg")
```

### Key Expiration Patterns

```python
def analyze_expiration():
    """Find expiration hotspots"""
    ttl_buckets = {
        '< 1 min': 0,
        '1-5 min': 0,
        '5-30 min': 0,
        '30 min-1h': 0,
        '1-24h': 0,
        '> 24h': 0,
        'no expiry': 0
    }
    
    for key in redis.scan_iter(count=1000):
        ttl = redis.ttl(key)  # Seconds
        
        if ttl == -1:
            ttl_buckets['no expiry'] += 1
        elif ttl < 60:
            ttl_buckets['< 1 min'] += 1
        elif ttl < 300:
            ttl_buckets['1-5 min'] += 1
        elif ttl < 1800:
            ttl_buckets['5-30 min'] += 1
        elif ttl < 3600:
            ttl_buckets['30 min-1h'] += 1
        elif ttl < 86400:
            ttl_buckets['1-24h'] += 1
        else:
            ttl_buckets['> 24h'] += 1
    
    return ttl_buckets

print(analyze_expiration())
```

## Real-Time Monitoring

### Monitor Command

```bash
# Monitor all commands in real-time
redis-cli MONITOR

# Output:
# 1234567890.123456 [0 127.0.0.1:12345] "SET" "key" "value"
# 1234567890.234567 [0 127.0.0.1:12345] "GET" "key"
```

### Client Tracking

```bash
# List connected clients
redis-cli CLIENT LIST

# Kill slow client
redis-cli CLIENT KILL IP:PORT

# Set client name
redis-cli CLIENT SETNAME my-app

# Get current client info
redis-cli CLIENT INFO
```

## Health Checks

### Connection Health

```python
def health_check():
    """Verify Redis connectivity"""
    try:
        result = redis.ping()
        return {'status': 'healthy', 'ping': result}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

print(health_check())
```

### Replication Status

```python
def replication_info():
    """Check replication health"""
    info = redis.info('replication')
    
    return {
        'role': info['role'],
        'connected_slaves': info.get('connected_slaves', 0),
        'master_repl_offset': info.get('master_repl_offset', 0)
    }

print(replication_info())
```

## Production Dashboards

### Prometheus Export

```python
from redis import Redis
from prometheus_client import Gauge, CollectorRegistry

registry = CollectorRegistry()

redis_memory = Gauge('redis_memory_bytes', 'Redis memory usage', registry=registry)
redis_keys = Gauge('redis_keys_total', 'Total keys in Redis', registry=registry)
redis_hits = Gauge('redis_cache_hits_total', 'Cache hits', registry=registry)
redis_misses = Gauge('redis_cache_misses_total', 'Cache misses', registry=registry)

def update_metrics():
    """Push Redis metrics to Prometheus"""
    info = redis.info()
    
    redis_memory.set(info['used_memory'])
    redis_keys.set(sum(db['keys'] for db in info.get('keyspace', {}).values()))
    redis_hits.set(info['keyspace_hits'])
    redis_misses.set(info['keyspace_misses'])
```

### Grafana Queries

```
# Memory usage over time
redis_memory_human

# Keys count
redis_keyspace_keys_total

# Cache hit ratio
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))

# Commands per second
rate(redis_commands_processed_total[1m])
```

## Debugging Commands

### Key Inspection

```bash
# View key structure
redis-cli TYPE key

# Memory used by key
redis-cli MEMORY USAGE key

# Serialized length
redis-cli STRLEN key

# List length
redis-cli LLEN key

# Set size
redis-cli SCARD key

# Hash field count
redis-cli HLEN key

# Sorted set size
redis-cli ZCARD key
```

### Data Export/Inspect

```python
def inspect_key(key):
    """Debug key contents"""
    key_type = redis.type(key)
    ttl = redis.ttl(key)
    memory = redis.memory_usage(key)
    
    if key_type == b'string':
        value = redis.get(key)
    elif key_type == b'hash':
        value = redis.hgetall(key)
    elif key_type == b'list':
        value = redis.lrange(key, 0, -1)
    elif key_type == b'set':
        value = redis.smembers(key)
    elif key_type == b'zset':
        value = redis.zrange(key, 0, -1, withscores=True)
    else:
        value = None
    
    return {
        'type': key_type.decode() if isinstance(key_type, bytes) else key_type,
        'ttl_seconds': ttl,
        'memory_bytes': memory,
        'value': value
    }

print(inspect_key('user:123'))
```

## Alerting Rules

### Critical Thresholds

```yaml
# Prometheus alerting rules
groups:
  - name: redis
    rules:
      - alert: RedisMemoryHigh
        expr: redis_memory_bytes > 900000000  # 900MB
        for: 5m
        annotations:
          summary: "Redis memory usage high"
      
      - alert: RedisEvictions
        expr: increase(redis_evicted_keys_total[5m]) > 100
        annotations:
          summary: "Redis evicting keys"
      
      - alert: RedisCacheHitLow
        expr: |
          (rate(redis_keyspace_hits_total[5m]) / 
           (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))) < 0.8
        annotations:
          summary: "Cache hit ratio below 80%"
      
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        annotations:
          summary: "Redis instance down"
```

## Troubleshooting

### High Memory Usage

```python
# 1. Find large keys
def find_large_keys(limit=100):
    large_keys = []
    for key in redis.scan_iter(count=1000):
        size = redis.memory_usage(key)
        if size > limit * 1024:  # KB
            large_keys.append((key, size))
    return sorted(large_keys, key=lambda x: x[1], reverse=True)[:10]

# 2. Check eviction
info = redis.info('stats')
print(f"Evicted keys: {info['evicted_keys']}")

# 3. Adjust maxmemory-policy
redis.config_set('maxmemory-policy', 'allkeys-lru')
```

### Slow Operations

```python
# Check slow log
queries = redis.slowlog_get()
for duration, command in queries:
    if duration > 1000000:  # > 1 second
        print(f"SLOW: {duration/1000000:.2f}s - {command}")

# Profile hot keys
redis.config_set('loglevel', 'debug')
# Monitor for 10s, then analyze
```

### Connection Timeouts

```python
# Increase timeouts
redis = Redis(
    socket_connect_timeout=10,  # Connection
    socket_timeout=10,          # Read/write
    retry_on_timeout=True
)

# Use connection pool
redis = Redis(
    connection_pool=ConnectionPool(
        socket_connect_timeout=10,
        retry_on_timeout=True
    )
)
```

## Checklist

- [ ] Monitor memory usage (INFO memory)
- [ ] Track cache hit ratio > 80%
- [ ] Check slow log regularly
- [ ] Configure maxmemory + eviction policy
- [ ] Health check in application
- [ ] Alert on memory > 90%
- [ ] Alert on evictions > 0
- [ ] Monitor replication lag (if replicated)
- [ ] Audit key TTL patterns
- [ ] Measure command latency

---

See **BEST_PRACTICES.md** for production patterns.
