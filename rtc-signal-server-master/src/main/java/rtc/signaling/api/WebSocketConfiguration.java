package rtc.signaling.api;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import rtc.signaling.message.MessageService;

@Configuration
@EnableWebSocket
class WebSocketConfiguration {

    @Bean
    MessageTopicWebSocketHandler messageTopicWebSocketHandler(MessageService messageService) {
        return new MessageTopicWebSocketHandler(messageService);
    }

    @Bean
    WebSocketConfigurer webSocketConfigurer(MessageTopicWebSocketHandler messageTopicWebSocketHandler) {
        return registry -> registry.addHandler(messageTopicWebSocketHandler, "/topic/message/**");
    }
}
