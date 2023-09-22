import socket

import rfc5389stunserver.server

if __name__ == "__main__":
    PORT = 19302
    # PORTS = 5349
    print(f'My hostname is {socket.gethostname()}')

    udp_server = rfc5389stunserver.server.create_udp_server_thread(PORT)
