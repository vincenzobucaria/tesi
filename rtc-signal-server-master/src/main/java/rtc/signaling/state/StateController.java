package rtc.signaling.state;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import rtc.signaling.message.MessageService;

import java.util.Set;

@RestController
@RequestMapping("state")
public class StateController {

    private final MessageService messageService;

    @Autowired
    public StateController(MessageService messageService) {
        this.messageService = messageService;
    }

    @GetMapping
    public Set<String> state() {
        return messageService.getSessionIds();
    }
}
