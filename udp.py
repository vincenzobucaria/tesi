import socket
import time

UDP_IP = "9.0.0.2"
UDP_PORT = 25565
MESSAGE = b"Hello, World!"

print("Invio il datagramma a: %s" % UDP_IP)
print("alla porta: %s" % UDP_PORT)
print("contenuto del messaggio: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM) 

sock.bind(("", 25565))

#sock.bind(("localhost", 5011))
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


while(True):
    data, addr = sock.recvfrom(1024)
    print("Messaggio ricevuto: %s" % data)
    print("dalla macchina:", addr)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    time.sleep(5)
