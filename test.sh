server cd rtc-signal-server-master && gradle --stop && gradle bootRun &
server2 cd stun_server && python3 server.py &
py time.sleep(12)
IoT_node1 cd rtc-tunnel-master && python3 rtc-tunnel/server.py -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node2 cd rtc-tunnel-master && python3 rtc-tunnel/client.py -s 25565 -d 25565 -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node1 socat -d -d TCP-L:25565,bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5000,up &
py time.sleep(2)
IoT_node2 socat -d -d TCP:localhost:25565,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5000,up &
py time.sleep(2)
IoT_node2 cd rtc-tunnel-master && python3 rtc-tunnel/server.py -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node3 cd rtc-tunnel-master && python3 rtc-tunnel/client.py -s 25566 -d 25566 -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(5)
IoT_node2 socat -d -d TCP-L:25566,bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5001,up &
py time.sleep(5)
IoT_node3 socat -d -d TCP:localhost:25566,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5001,up &
py time.sleep(5)

IoT_node1 ip addr add 192.168.0.1 brd + dev tap5000 && ip route add 192.168.0.2 dev tap5000 && ip route add 192.168.0.0/24 via 192.168.0.2
IoT_node3 ip addr add 192.168.0.3 brd + dev tap5001 && ip route add 192.168.0.2 dev tap5001 && ip route add 192.168.0.0/24 via 192.168.0.2
IoT_node2 ip addr add 192.168.0.2 brd + dev tap5000 && ip addr add 192.168.0.2 brd + dev tap5001 && sysctl -w net.ipv4.ip_forward=1 && ip route add 192.168.0.1 via 192.168.0.2 dev tap5000 && ip route add 192.168.0.3 via 192.168.0.2 dev tap5001

IoT_node4 cd rtc-tunnel-master && python3 rtc-tunnel/server.py -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node5 cd rtc-tunnel-master && python3 rtc-tunnel/client.py -s 25567 -d 25567 -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node4 socat -d -d TCP-L:25567,bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5000,up &
py time.sleep(2)
IoT_node5 socat -d -d TCP:localhost:25567,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5000,up &
py time.sleep(2)
IoT_node5 cd rtc-tunnel-master && python3 rtc-tunnel/server.py -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node6 cd rtc-tunnel-master && python3 rtc-tunnel/client.py -s 25568 -d 25568 -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(5)
IoT_node5 socat -d -d TCP-L:25568,bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5001,up &
py time.sleep(5)
IoT_node6 socat -d -d TCP:localhost:25568,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap5001,up &
py time.sleep(5)

IoT_node4 ip addr add 192.168.0.4 brd + dev tap5000 && ip route add 192.168.0.5 dev tap5000 && ip route add 192.168.0.0/24 via 192.168.0.5
IoT_node6 ip addr add 192.168.0.6 brd + dev tap5001 && ip route add 192.168.0.5 dev tap5001 && ip route add 192.168.0.0/24 via 192.168.0.5
IoT_node5 ip addr add 192.168.0.5 brd + dev tap5000 && ip addr add 192.168.0.5 brd + dev tap5001 && sysctl -w net.ipv4.ip_forward=1 && ip route add 192.168.0.4 via 192.168.0.5 dev tap5000 && ip route add 192.168.0.6 via 192.168.0.5 dev tap5001

IoT_node2 cd rtc-tunnel-master && python3 rtc-tunnel/server.py -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node5 cd rtc-tunnel-master && python3 rtc-tunnel/client.py -s 25569 -d 25569 -w -u http://user:password@9.0.0.1:8080 -r ws://user:password@9.0.0.1:8080 &
py time.sleep(2)
IoT_node2 socat -d -d TCP-L:25569,bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap_ext,up &
py time.sleep(2)
IoT_node5 socat -d -d TCP:localhost:25569,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=tap_ext,up &
py time.sleep(15)

IoT_node2 ip addr add 192.168.0.2 brd + dev tap_ext && ip route add 192.168.0.5 dev tap_ext && ip route add 192.168.0.4 via 192.168.0.5 && ip route add 192.168.0.6 via 192.168.0.5
IoT_node5 ip addr add 192.168.0.5 brd + dev tap_ext && ip route add 192.168.0.2 dev tap_ext && ip route add 192.168.0.1 via 192.168.0.2 && ip route add 192.168.0.3 via 192.168.0.2

xterm IoT_node1 IoT_node2 IoT_node3 IoT_node4 IoT_node5 IoT_node6