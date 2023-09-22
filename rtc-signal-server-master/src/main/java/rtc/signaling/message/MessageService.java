package rtc.signaling.message;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class MessageService {

    private static final Logger LOG = LoggerFactory.getLogger(MessageService.class);

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    public boolean send(String destination, String message) {
        LOG.info("Sending message [" + message + "] to [" + destination + "]");

        WebSocketSession session = sessions.get(destination);
        if (session != null) {
            try {
                session.sendMessage(new TextMessage(message));
            } catch (IOException e) {
                LOG.error("Unable to send message", e);
            }
            return true;
        }

        return false;
    }

    public boolean addSession(String sessionId, WebSocketSession session) {
        LOG.info("New client [{}] connected", sessionId);
        return sessions.putIfAbsent(sessionId, session) == null;
    }

    public void removeSession(String sessionId) {
        LOG.info("Client [{}] disconnected", sessionId);
        sessions.remove(sessionId);
    }

    public Set<String> getSessionIds() {
        return sessions.keySet();
    }
}
