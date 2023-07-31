import socket
import time

UDP_IP = "localhost"
UDP_PORT = 25565

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind(("", UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
    print(type(addr))
    print(addr)
    print("sto inviando il msg")
    message = "I tuoi ip e porta sono" + str(addr)
    sock.sendto(bytes(message, 'UTF-8'), addr)
    addr2 = ('9.0.0.3', 25565)
    sock.sendto(bytes(str(addr), 'UTF-8'), addr2)



