import socket
import time

UDP_IP = "localhost"
UDP_PORT = 25565

sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM) 
sock.bind(("", UDP_PORT))


while(True):
    data, addr = sock.recvfrom(1024) 
    print("received message: %s" % data.decode())
    data = data.decode()
    data = data.replace('(', '')
    data = data.replace(')', '')
    data = data.split(',')
    data[0] = data[0].replace("'", '')
    addr2 = (str(data[0]), int(data[1]))
    print(addr2)
    print(addr)
    print(type(addr2))
    print("sto inviando il msg")
    message = "SERVER2, ip e porta rilevati dal server: " + str(addr2)
    sock.sendto(bytes(message, 'UTF-8'), addr2)
    


