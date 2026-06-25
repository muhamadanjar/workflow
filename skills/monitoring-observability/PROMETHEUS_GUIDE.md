# Prometheus Metrics

## Setup Python

```python
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
import time

# Create metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', buckets=(0.1, 0.5, 1.0, 2.5, 5.0))
active_connections = Gauge('active_connections', 'Number of active connections')
response_size = Summary('http_response_size_bytes', 'HTTP response size')

# Start metrics server
start_http_server(8000)  # Metrics at http://localhost:8000/metrics

# Use metrics
request_count.labels(method='GET', endpoint='/api/users').inc()

with request_duration.labels(endpoint='/api/users').time():
    # Do work
    time.sleep(1)

active_connections.inc()
active_connections.dec()

response_size.observe(1024)
```

## Setup Node.js

```javascript
const prometheus = require('prom-client');
const express = require('express');

const app = express();

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new prometheus.Counter({
    name: 'http_requests_total',
    help: 'Total HTTP requests',
    labelNames: ['method', 'route', 'status_code']
});

// Middleware
app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;
        httpRequestDuration.labels(req.method, req.route?.path || req.path, res.statusCode).observe(duration);
        httpRequestTotal.labels(req.method, req.route?.path || req.path, res.statusCode).inc();
    });
    
    next();
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    res.set('Content-Type', prometheus.register.contentType);
    res.end(prometheus.register.metrics());
});
```

## Metric Types

### Counter
Only increases:
```python
errors = Counter('errors_total', 'Total errors', ['error_type'])
errors.labels(error_type='timeout').inc()
```

### Gauge
Can increase or decrease:
```python
memory_usage = Gauge('memory_usage_bytes', 'Memory usage')
memory_usage.set(1024 * 1024)  # 1MB
memory_usage.inc(512)
memory_usage.dec(256)
```

### Histogram
Distribution of values:
```python
response_time = Histogram('response_time_seconds', 'Response time', buckets=[0.1, 0.5, 1, 2, 5])
response_time.observe(0.25)  # Record 250ms
```

### Summary
Quantiles:
```python
query_time = Summary('query_time_seconds', 'Query time')
query_time.observe(0.5)  # Record 500ms
# Provides _sum, _count, quantile
```

## Configuration

prometheus.yml:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'my-app'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'node-app'
    static_configs:
      - targets: ['localhost:3000']
```

## Custom Labels

```python
# With labels
request_duration = Histogram(
    'http_request_duration',
    'Request duration',
    labelNames=['method', 'endpoint', 'status']
)

request_duration.labels(
    method='GET',
    endpoint='/api/users',
    status=200
).observe(0.5)
```

## Querying

PromQL queries:
```
# Total requests
http_requests_total

# Requests per second (rate)
rate(http_requests_total[5m])

# Average response time
rate(http_request_duration_sum[5m]) / rate(http_request_duration_count[5m])

# 95th percentile
histogram_quantile(0.95, http_request_duration_bucket)

# Errors per minute
rate(errors_total[1m])
```

## Best Practices

- ✅ Use consistent naming
- ✅ Add meaningful labels
- ✅ Don't create unbounded cardinality
- ✅ Use appropriate metric types
- ✅ Set sensible histogram buckets
- ✅ Monitor key business metrics
- ✅ Health check endpoints
