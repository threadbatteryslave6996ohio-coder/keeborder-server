# Keeboarder WebSocket Redis Server

A Java WebSocket server that maintains a Redis cache of all connected clients, enabling personalized message delivery and host advertisement.

## Features

- **WebSocket Communication**: Real-time bidirectional communication using WebSocket protocol
- **Redis-Backed Client Registry**: All connected clients are stored in Redis for persistence and scalability
- **Personalized Messages**: Send targeted messages to specific clients by their ID
- **Host Advertisement**: New clients can advertise themselves with a custom name
- **Broadcast Messages**: Send messages to all connected clients

## Architecture

### Components

1. **ChatServer** - Main server entry point that initializes and starts the WebSocket server
2. **ChatEndpoint** - WebSocket endpoint handler that manages client connections and message routing
3. **RedisClientCache** - Redis client wrapper for managing connected client metadata
4. **Message** - Data class representing client messages

### Message Flow

```
Client connects → Register with name → Get unique clientId
                    ↓
            Announcement broadcast
         (other clients see new host)
                    ↓
        Client can send/receive messages
                    ↓
      On disconnect → Cleanup Redis entry
```

## Prerequisites

- Java 21+
- Redis server running on localhost:6379 (or configured via environment variables)
- Maven (for building from source)

## Building

```bash
cd /home/kamina_goat/Desktop/keeboarder
mvn -DskipTests package
```

This creates:
- `target/websocket-redis-server-0.1.0.jar` - Lightweight JAR
- `target/websocket-redis-server-0.1.0-jar-with-dependencies.jar` - Executable JAR with all dependencies

## Running the Server

### Prerequisites: Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or if Redis is installed locally
redis-server
```

### Start the WebSocket Server

```bash
java -jar target/websocket-redis-server-0.1.0-jar-with-dependencies.jar
```

### Configuration via Environment Variables

```bash
WEBSOCKET_HOST=0.0.0.0          # Default: localhost
WEBSOCKET_PORT=8025             # Default: 8025
REDIS_HOST=localhost            # Default: localhost
REDIS_PORT=6379                 # Default: 6379
SERVER_NAME=KeeboarderWS        # Default: KeeboarderWS
```

Example with custom configuration:

```bash
WEBSOCKET_HOST=0.0.0.0 WEBSOCKET_PORT=9000 REDIS_HOST=redis.example.com \
  java -jar target/websocket-redis-server-0.1.0-jar-with-dependencies.jar
```

## Message Protocol

All messages are JSON formatted. The server communicates on `ws://host:port/ws/chat`.

### Client Registration

**Request** (Client → Server):
```json
{
  "type": "register",
  "clientId": "unique-id-or-leave-empty",
  "name": "MyKeeboarder"
}
```

**Response** (Server → Client):
```json
{
  "type": "registered",
  "clientId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "MyKeeboarder"
}
```

If you omit `clientId`, the server generates a UUID for you.

### Host Join Announcement

When a new host registers, all other connected clients receive:

```json
{
  "type": "host_joined",
  "clientId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "MyKeeboarder",
  "connectedAt": "2026-06-21T15:30:45.123Z"
}
```

### Personalized Message

**Request** (Client → Server):
```json
{
  "type": "personal",
  "clientId": "sender-id",
  "toClientId": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Hello specific client!"
}
```

**Response** (Server → Target Client):
```json
{
  "type": "personal",
  "fromClientId": "sender-id",
  "content": "Hello specific client!"
}
```

### Broadcast Message

**Request** (Client → Server):
```json
{
  "type": "broadcast",
  "clientId": "sender-id",
  "content": "Message for everyone except me"
}
```

**Broadcast** (Server → All Other Clients):
```json
{
  "type": "broadcast",
  "fromClientId": "sender-id",
  "content": "Message for everyone except me"
}
```

### Error Messages

```json
{
  "type": "error",
  "message": "Description of what went wrong"
}
```

## Redis Schema

The server uses Redis to store client information:

- **Key**: `ws:clients` - Set containing all connected client IDs
- **Key**: `ws:client:{clientId}` - Hash containing:
  - `name`: Client's advertised name
  - `connectedAt`: ISO 8601 timestamp of connection

### Example Redis Data

```
127.0.0.1:6379> SMEMBERS ws:clients
1) "550e8400-e29b-41d4-a716-446655440000"
2) "660e8400-e29b-41d4-a716-446655440001"

127.0.0.1:6379> HGETALL ws:client:550e8400-e29b-41d4-a716-446655440000
1) "name"
2) "MyKeeboarder"
3) "connectedAt"
4) "2026-06-21T15:30:45.123Z"
```

## Example Client (JavaScript/WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8025/ws/chat');

ws.onopen = () => {
  console.log('Connected to server');
  
  // Register with the server
  ws.send(JSON.stringify({
    type: 'register',
    name: 'My Keyboard'
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.type === 'registered') {
    console.log('Got clientId:', msg.clientId);
    window.myClientId = msg.clientId;
  } else if (msg.type === 'host_joined') {
    console.log(`${msg.name} joined!`);
  } else if (msg.type === 'personal') {
    console.log(`Message from ${msg.fromClientId}:`, msg.content);
  } else if (msg.type === 'broadcast') {
    console.log(`Broadcast from ${msg.fromClientId}:`, msg.content);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Send a personal message
function sendPersonal(targetClientId, message) {
  ws.send(JSON.stringify({
    type: 'personal',
    clientId: window.myClientId,
    toClientId: targetClientId,
    content: message
  }));
}

// Send a broadcast message
function sendBroadcast(message) {
  ws.send(JSON.stringify({
    type: 'broadcast',
    clientId: window.myClientId,
    content: message
  }));
}
```

## Example Client (Python)

```python
import asyncio
import json
import websockets
import uuid

async def main():
    client_id = None
    
    async with websockets.connect('ws://localhost:8025/ws/chat') as ws:
        # Register
        await ws.send(json.dumps({
            'type': 'register',
            'name': 'Python Client'
        }))
        
        # Receive registration response
        response = json.loads(await ws.recv())
        print(f"Registered: {response}")
        client_id = response['clientId']
        
        # Listen for messages
        while True:
            msg = json.loads(await ws.recv())
            print(f"Received: {msg}")
            
            if msg['type'] == 'host_joined':
                print(f"New host: {msg['name']}")
            elif msg['type'] == 'personal':
                print(f"Personal message from {msg['fromClientId']}: {msg['content']}")
            elif msg['type'] == 'broadcast':
                print(f"Broadcast from {msg['fromClientId']}: {msg['content']}")

asyncio.run(main())
```

## Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM openjdk:21-jdk-slim
WORKDIR /app
COPY target/websocket-redis-server-0.1.0-jar-with-dependencies.jar app.jar
ENV WEBSOCKET_HOST=0.0.0.0
ENV WEBSOCKET_PORT=8025
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
EXPOSE 8025
CMD ["java", "-jar", "app.jar"]
```

Build and run with Docker Compose:

```yaml
version: '3.8'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
  
  websocket-server:
    build: .
    ports:
      - "8025:8025"
    depends_on:
      - redis
    environment:
      REDIS_HOST: redis
```

Run:
```bash
docker-compose up
```

## Troubleshooting

### Connection Refused
- Check that Redis is running: `redis-cli ping`
- Verify WebSocket server is started: `netstat -an | grep 8025`

### Clients Not Appearing
- Verify Redis is accessible with correct host/port
- Check server logs for connection errors
- Use `redis-cli SMEMBERS ws:clients` to verify client registration

### Message Not Delivered
- Verify target clientId exists: `redis-cli SMEMBERS ws:clients`
- Check client is still connected (not disconnected)
- Ensure proper JSON formatting in message

## Performance Considerations

- Each client connection maintains a WebSocket session
- Redis operations are optimized with connection pooling (via Jedis)
- Server scales horizontally by connecting multiple instances to the same Redis
- Message broadcasting is done in-memory for active sessions

## License

MIT
