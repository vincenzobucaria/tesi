import socket
import time

UDP_IP = "localhost"
UDP_PORT = 25565

sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM) 
sock.bind(("", UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) 
    print("Messaggio ricevuto: %s" % data)
    #print(type(addr))
    #print(addr)
    #print("sto inviando il msg")
    message = "IP e porta rilevati dal server: " + str(addr)
    sock.sendto(bytes(message, 'UTF-8'), addr) #Contatta l'host privato
    
    addr2 = ('9.0.0.3', 25565)
    sock.sendto(bytes(str(addr), 'UTF-8'), addr2) #Contatta il secondo server



