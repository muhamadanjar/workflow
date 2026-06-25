# Socket.io - Real-time Communication

## Server Setup

```javascript
const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
    cors: {
        origin: 'http://localhost:3000',
        methods: ['GET', 'POST']
    }
});

server.listen(3000, () => {
    console.log('Server listening on 3000');
});
```

## Connection Handling

```javascript
// Connection event
io.on('connection', (socket) => {
    console.log(`User ${socket.id} connected`);
    
    // Emit to client
    socket.emit('welcome', { message: 'Welcome!' });
    
    // Listen to client
    socket.on('message', (data) => {
        console.log(data);
    });
    
    // Disconnect
    socket.on('disconnect', () => {
        console.log(`User ${socket.id} disconnected`);
    });
});
```

## Broadcasting

```javascript
// Send to all clients
io.emit('notification', { text: 'Server message' });

// Send to all except sender
socket.broadcast.emit('user-joined', { userId: socket.id });

// Send to specific socket
io.to(socketId).emit('private', { message: 'Private message' });

// Send to room
io.to('roomName').emit('room-event', { data: 'data' });

// Send to all in room except sender
socket.to('roomName').emit('message', { data: 'data' });
```

## Rooms

```javascript
// Join room
socket.join('room1');

// Leave room
socket.leave('room1');

// Emit to room
io.to('room1').emit('message', { text: 'Room message' });

// Room members
const clients = io.sockets.adapter.rooms.get('room1');
console.log(clients.size);

// Get user rooms
const rooms = socket.rooms;
```

## Namespaces

```javascript
// Create namespace
const nsp = io.of('/chat');

nsp.on('connection', (socket) => {
    console.log('Chat namespace connection');
    
    socket.on('send-message', (msg) => {
        nsp.emit('receive-message', msg);
    });
});

// Client connects to namespace
// const socket = io('http://localhost:3000/chat');
```

## Client Side

```javascript
import io from 'socket.io-client';

// Connect
const socket = io('http://localhost:3000');

// Listen to server
socket.on('welcome', (data) => {
    console.log(data);
});

// Send to server
socket.emit('message', { text: 'Hello server' });

// Acknowledgment
socket.emit('ask', {}, (response) => {
    console.log('Server responded:', response);
});

// Disconnect
socket.disconnect();

// Reconnect events
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));
socket.on('reconnect', () => console.log('Reconnected'));
```

## Acknowledgments (Callbacks)

```javascript
// Server sends with callback
socket.on('request', (data, callback) => {
    callback({ status: 'received' });
});

// Client with acknowledgment
socket.emit('message', { text: 'Hi' }, (response) => {
    console.log('Acknowledged:', response);
});
```

## Error Handling

```javascript
// Connection errors
io.on('connect_error', (error) => {
    console.log('Connection error:', error);
});

// Handle socket errors
socket.on('error', (error) => {
    console.log('Socket error:', error);
});

// Disconnect reasons
socket.on('disconnect', (reason) => {
    console.log('Disconnect reason:', reason);
    // 'io server disconnect', 'io client namespace disconnect',
    // 'ping timeout', 'transport close', 'transport error'
});
```

## Middleware

```javascript
// Server middleware
io.use((socket, next) => {
    const token = socket.handshake.auth.token;
    
    if (validateToken(token)) {
        next();
    } else {
        next(new Error('Authentication error'));
    }
});

// Namespace middleware
nsp.use((socket, next) => {
    // Check permissions
    next();
});
```

## Binary Data

```javascript
// Send binary data
socket.emit('binary-event', new ArrayBuffer(10));

// Receive binary
socket.on('binary-response', (buffer) => {
    console.log('Received buffer:', buffer);
});
```

## Production Patterns

### Load Balancing

```javascript
const { createAdapter } = require('@socket.io/redis-adapter');
const { redis } = require('./redis');

io.adapter(createAdapter(redis.pub, redis.sub));
```

### Authentication

```javascript
io.use((socket, next) => {
    const userId = socket.handshake.query.userId;
    const token = socket.handshake.headers.authorization;
    
    if (validateAuth(userId, token)) {
        socket.userId = userId;
        next();
    } else {
        next(new Error('Unauthorized'));
    }
});
```

### Rate Limiting

```javascript
const limiter = require('express-rate-limit');

socket.on('message', limiter.rateLimit({
    max: 10,
    windowMs: 60000
}), (data) => {
    io.emit('message', data);
});
```

## Best Practices

- ✅ Use namespaces for organization
- ✅ Implement authentication
- ✅ Handle disconnections gracefully
- ✅ Use Redis adapter for scaling
- ✅ Set connection timeouts
- ✅ Validate all data
- ✅ Monitor connections
