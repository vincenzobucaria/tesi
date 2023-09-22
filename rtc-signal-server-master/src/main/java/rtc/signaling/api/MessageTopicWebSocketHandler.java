package rtc.signaling.api;

import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import rtc.signaling.message.MessageService;

public class MessageTopicWebSocketHandler extends TextWebSocketHandler {

    private final MessageService messageService;

    MessageTopicWebSocketHandler(MessageService messageService) {
        this.messageService = messageService;
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        super.afterConnectionEstablished(session);

        String sessionId = getSessionId(session);
        if (!messageService.addSession(sessionId, session)) {
            throw new IllegalStateException("Client for this message pipe already connected");
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        super.afterConnectionClosed(session, status);

        String sessionId = getSessionId(session);
        messageService.removeSession(sessionId);
    }

    private String getSessionId(WebSocketSession session) {
        String path = session.getUri().getPath();
        return path.substring(path.lastIndexOf('/') + 1);
    }
}
