# Server-Sent Events (SSE)

## Server Side

### Python (Flask)

```python
from flask import Flask, Response
import time
import json

app = Flask(__name__)

@app.route('/events')
def events():
    def generate():
        while True:
            data = {
                'timestamp': time.time(),
                'message': 'Server message'
            }
            yield f'data: {json.dumps(data)}\n\n'
            time.sleep(5)
    
    return Response(generate(), mimetype='text/event-stream')
```

### Node.js (Express)

```javascript
app.get('/events', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    const interval = setInterval(() => {
        res.write(`data: ${JSON.stringify({ message: 'Server message' })}\n\n`);
    }, 5000);
    
    req.on('close', () => {
        clearInterval(interval);
        res.end();
    });
});
```

## Client Side

```javascript
const eventSource = new EventSource('/events');

// Handle incoming events
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Error handling
eventSource.onerror = (error) => {
    console.log('Connection error:', error);
    eventSource.close();
};

// Close connection
eventSource.close();
```

## Named Events

```python
@app.route('/events')
def events():
    def generate():
        yield 'event: user-login\n'
        yield 'data: {"userId": 123}\n\n'
        
        yield 'event: notification\n'
        yield 'data: {"text": "New message"}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')
```

Client:
```javascript
eventSource.addEventListener('user-login', (event) => {
    console.log('User logged in:', JSON.parse(event.data));
});

eventSource.addEventListener('notification', (event) => {
    console.log('Notification:', JSON.parse(event.data));
});
```

## vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WebSocket |
| Overhead | Low | Higher |
| Use Case | Notifications, updates | Chat, gaming |
| Reconnect | Automatic | Manual |

## Best Practices

- ✅ SSE for one-way updates
- ✅ WebSocket for bidirectional
- ✅ Handle disconnections
- ✅ Use heartbeat to detect stales
- ✅ Set appropriate timeouts
