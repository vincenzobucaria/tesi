package rtc.signaling.message;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
class MessageConfiguration {

    @Bean
    MessageService messageService() {
        return new MessageService();
    }
}
