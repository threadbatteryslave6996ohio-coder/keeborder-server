package com.keeboarder.server;

import org.glassfish.tyrus.server.Server;

public class ChatServer {
    public static void main(String[] args) {
        String host = System.getenv().getOrDefault("WEBSOCKET_HOST", "localhost");
        int port = Integer.parseInt(System.getenv().getOrDefault("WEBSOCKET_PORT", "8025"));
        String redisHost = System.getenv().getOrDefault("REDIS_HOST", "localhost");
        int redisPort = Integer.parseInt(System.getenv().getOrDefault("REDIS_PORT", "6379"));
        String serverName = System.getenv().getOrDefault("SERVER_NAME", "KeeboarderWS");

        RedisClientCache clientCache = new RedisClientCache(redisHost, redisPort);
        ChatEndpoint.initialize(clientCache);

        Server server = new Server(host, port, "/ws", null, ChatEndpoint.class);

        // Start a small HTTP API server (separate port) to expose client list and send messages
        String httpHost = System.getenv().getOrDefault("HTTP_HOST", "0.0.0.0");
        int httpPort = Integer.parseInt(System.getenv().getOrDefault("HTTP_PORT", "8080"));
        final HttpApiServer[] httpApiHolder = new HttpApiServer[1];
        try {
            httpApiHolder[0] = new HttpApiServer(httpHost, httpPort);
            httpApiHolder[0].start();
            System.out.println("HTTP API started on http://" + httpHost + ":" + httpPort + "/api");
        } catch (Exception e) {
            System.out.println("Warning: failed to start HTTP API: " + e.getMessage());
        }

        try {
            System.out.println("Starting WebSocket server on ws://" + host + ":" + port + "/ws/chat");
            System.out.println("Using Redis at " + redisHost + ":" + redisPort);
            System.out.println("Server name: " + serverName);
            server.start();
            System.out.println("Press CTRL+C to stop the server.");

            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("Stopping WebSocket server...");
                clientCache.close();
                server.stop();
                if (httpApiHolder[0] != null) {
                    System.out.println("Stopping HTTP API...");
                    httpApiHolder[0].stop();
                }
            }));

            Thread.currentThread().join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
