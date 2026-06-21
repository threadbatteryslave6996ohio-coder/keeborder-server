# keeboarder

A multi-protocol keyboard and communication system.

## 🎹 WebSocket Server

A Java-based WebSocket server with Redis-backed client management for real-time personalized messaging and host advertisement.

**[→ Full WebSocket Server Documentation](./WEBSOCKET_SERVER.md)**

### Quick Start

1. **Start Redis:**
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

2. **Build the server:**
   ```bash
   mvn -DskipTests package
   ```

3. **Run the server:**
   ```bash
   java -jar target/websocket-redis-server-0.1.0-jar-with-dependencies.jar
   ```

4. **Test the server:**
   - Open `client-example.html` in your browser for a visual client
   - Or run the Python client: `python3 client-example.py`

### Features

- ✅ Real-time WebSocket communication
- ✅ Redis-backed client registry
- ✅ Personalized message delivery
- ✅ Host advertisement and discovery
- ✅ Broadcast messaging

### Message Protocol

All communication uses JSON. Connect to `ws://localhost:8025/ws/chat`:

```javascript
// Register
{ type: 'register', name: 'My Device' }

// Send personal message
{ type: 'personal', clientId: 'me', toClientId: 'them', content: 'Hello' }

// Send broadcast
{ type: 'broadcast', clientId: 'me', content: 'Hello everyone' }
```

See [WEBSOCKET_SERVER.md](./WEBSOCKET_SERVER.md) for complete documentation.
