# Alerting & Notifications

## Prometheus Alerting Rules

```yaml
# alerts.yml
groups:
  - name: application
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_bucket) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
```

## Alertmanager Configuration

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster']
  
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 1h
    
    - match:
        severity: warning
      receiver: 'warnings'
      repeat_interval: 6h

receivers:
  - name: 'default'
    slack_configs:
      - api_url: 'SLACK_WEBHOOK_URL'
        channel: '#alerts'
  
  - name: 'critical'
    slack_configs:
      - api_url: 'SLACK_WEBHOOK_URL'
        channel: '#critical-alerts'
    pagerduty_configs:
      - service_key: 'PAGERDUTY_KEY'
  
  - name: 'warnings'
    slack_configs:
      - api_url: 'SLACK_WEBHOOK_URL'
        channel: '#warnings'
```

## Custom Alerting (Python)

```python
class AlertManager:
    def __init__(self, slack_webhook):
        self.webhook = slack_webhook
    
    def send_alert(self, title, message, severity='warning'):
        import requests
        
        color = {
            'critical': '#FF0000',
            'warning': '#FFA500',
            'info': '#0099FF'
        }.get(severity, '#999999')
        
        payload = {
            'attachments': [{
                'color': color,
                'title': title,
                'text': message,
                'ts': int(time.time())
            }]
        }
        
        requests.post(self.webhook, json=payload)

# Usage
alerter = AlertManager(os.environ['SLACK_WEBHOOK'])
alerter.send_alert('Database Down', 'Connection timeout', severity='critical')
```

## Health Checks

```python
# Flask health endpoint
from flask import jsonify

@app.route('/health')
def health():
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'database': check_db_connection(),
        'cache': check_redis_connection()
    }
    
    if not health_data['database'] or not health_data['cache']:
        health_data['status'] = 'degraded'
        return jsonify(health_data), 503
    
    return jsonify(health_data)
```

## Best Practices

- ✅ Alert on symptoms, not causes
- ✅ Set appropriate thresholds
- ✅ Avoid alert fatigue
- ✅ Clear runbooks for each alert
- ✅ Test alerts regularly
