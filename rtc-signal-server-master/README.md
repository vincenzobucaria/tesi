# RTC signaling server

This is a simple signaling server for RTC protocol used by [RTC-Tunnel](https://github.com/pcimcioch/rtc-tunnel) application.
It standalone Spring Boot 2 web server.

## Build

To build you need java8 jdk
```
gradlew build
```

## Run

To run
```
gradlew bootRun
```

## Endpoints

Application provides two endpoints to send and receive data and one to check active connections.

Every endpoint is protected by basic auth.
It can be configured by setting spring properties:
- `spring.security.user.name` - username (`user` by default)
- `spring.security.user.password` - password (`password` by default)

1. `POST /message/{destination}` - sends any text data to channel `destination`. Will return `404` if no one is listening on this channel. Will return `200` if request passed.
1. `GET /state` - will return set of open channel names.
1. `WEBSOCKET /topic/message/{name}` - will connect to channel `name` and receive all new data from it. Will fail if someone is already listening on this channel.

## STOMP
Q: This sounds exactly like STOMP protocol, why not to leverage existing Spring WebSocketMessageBroker to do exactly the same?

A: I couldn't find good async python library for STOMP that would support websockets as communication layer. It was just quicker to write this simple app.