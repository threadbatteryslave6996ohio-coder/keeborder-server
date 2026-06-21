#!/usr/bin/env python3
"""
Keeboarder WebSocket Client - Python Example
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime


class KeeboarderClient:
    def __init__(self, server_url="ws://localhost:8025/ws/chat", name="PythonClient"):
        self.server_url = server_url
        self.name = name
        self.client_id = None
        self.ws = None
        self.connected_clients = {}

    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = await websockets.connect(self.server_url)
            print(f"✓ Connected to {self.server_url}")

            # Send registration
            await self.ws.send(json.dumps({
                'type': 'register',
                'name': self.name
            }))

            # Listen for messages
            await self.listen()
        except Exception as e:
            print(f"✗ Connection error: {e}")

    async def listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.ws:
                msg = json.loads(message)
                await self.handle_message(msg)
        except websockets.exceptions.ConnectionClosed:
            print("✗ Connection closed")

    async def handle_message(self, msg):
        """Handle received message"""
        msg_type = msg.get('type')

        if msg_type == 'registered':
            self.client_id = msg['clientId']
            print(f"\n✓ Registered successfully")
            print(f"  Client ID: {self.client_id}")
            print(f"  Name: {msg['name']}\n")

        elif msg_type == 'host_joined':
            self.connected_clients[msg['clientId']] = msg['name']
            print(f"\n👤 {msg['name']} joined")
            print(f"   Connected at: {msg['connectedAt']}\n")

        elif msg_type == 'personal':
            from_name = self.connected_clients.get(msg['fromClientId'], 'Unknown')
            print(f"\n💬 Personal message from {from_name}:")
            print(f"   {msg['content']}\n")

        elif msg_type == 'broadcast':
            from_name = self.connected_clients.get(msg['fromClientId'], 'Unknown')
            print(f"\n📢 Broadcast from {from_name}:")
            print(f"   {msg['content']}\n")

        elif msg_type == 'error':
            print(f"\n⚠️  Error: {msg['message']}\n")

        else:
            print(f"Unknown message type: {msg_type}")

    async def send_personal(self, to_client_id, content):
        """Send a personal message"""
        if not self.client_id:
            print("Not registered yet")
            return

        await self.ws.send(json.dumps({
            'type': 'personal',
            'clientId': self.client_id,
            'toClientId': to_client_id,
            'content': content
        }))
        print(f"✓ Sent personal message to {to_client_id}")

    async def send_broadcast(self, content):
        """Send a broadcast message"""
        if not self.client_id:
            print("Not registered yet")
            return

        await self.ws.send(json.dumps({
            'type': 'broadcast',
            'clientId': self.client_id,
            'content': content
        }))
        print(f"✓ Sent broadcast message")

    async def list_clients(self):
        """List all connected clients"""
        print("\nConnected clients:")
        for client_id, name in self.connected_clients.items():
            print(f"  - {name} ({client_id})")
        if not self.connected_clients:
            print("  (none)")

    async def interactive_mode(self):
        """Interactive command loop"""
        print("\nCommands:")
        print("  list              - List connected clients")
        print("  personal <id>     - Send personal message (enter content when prompted)")
        print("  broadcast         - Send broadcast message (enter content when prompted)")
        print("  quit              - Exit\n")

        loop = asyncio.get_event_loop()

        while True:
            try:
                # Run input in executor to avoid blocking
                command = await loop.run_in_executor(None, input, "> ")
                
                if command == 'quit':
                    break
                elif command == 'list':
                    await self.list_clients()
                elif command.startswith('personal '):
                    client_id = command.split(' ', 1)[1]
                    content = input("Message: ")
                    await self.send_personal(client_id, content)
                elif command == 'broadcast':
                    content = input("Message: ")
                    await self.send_broadcast(content)
                else:
                    print("Unknown command")
            except EOFError:
                break


async def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "PythonClient"

    client = KeeboarderClient(name=name)
    
    # Run connection and interactive mode concurrently
    await asyncio.gather(
        client.connect(),
        asyncio.sleep(1),  # Wait for connection
        client.interactive_mode()
    )


if __name__ == "__main__":
    print("🎹 Keeboarder WebSocket Python Client")
    print("=" * 40)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
