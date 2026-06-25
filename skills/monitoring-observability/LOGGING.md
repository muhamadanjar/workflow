# Structured Logging & Aggregation

## Python Logging

```python
import logging
import json

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Info log
logger.info('User login', extra={'user_id': 123, 'ip': '192.168.1.1'})

# Error with exception
try:
    do_something()
except Exception as e:
    logger.error('Operation failed', exc_info=True, extra={'operation': 'sync'})
```

## JSON Logging

```python
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

## Node.js Logging (Winston)

```javascript
const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Log with context
logger.info('User login', { userId: 123, ip: '192.168.1.1' });
logger.error('Database error', { error: err.message });
```

## ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
```

## Loki (Lightweight Logging)

```yaml
# config.yaml
auth_enabled: false

ingester:
  chunk_idle_period: 3m
  max_chunk_age: 1h

storage_config:
  filesystem:
    directory: /loki/chunks

schema_config:
  configs:
  - from: 2020-10-24
    store: boltdb-shipper
    object_store: filesystem
    schema:
      version: v11
      index:
        prefix: index_
        period: 24h
```

## Best Practices

- ✅ Use structured JSON logging
- ✅ Include request IDs for tracing
- ✅ Log at appropriate levels
- ✅ Don't log sensitive data
- ✅ Use log aggregation for production
