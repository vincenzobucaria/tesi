package rtc.signaling.api;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import rtc.signaling.message.MessageService;

@RestController
@RequestMapping("message")
public class MessageController {

    private final MessageService messageService;

    @Autowired
    public MessageController(MessageService messageService) {
        this.messageService = messageService;
    }

    @PostMapping(value = "{destination}")
    public ResponseEntity send(@PathVariable("destination") String destination, @RequestBody String message) {
        if(!messageService.send(destination, message)) {
            
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok().build();
        
    }
}
