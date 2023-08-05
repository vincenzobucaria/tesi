lan_list = list()
nat_types = ["full_cone", "restricted_cone", "port_restricted", "symmetric", "public"]
node_list = list()
nat_dict = dict()
private_network_topology = dict()
public_network_topology = dict()
import math
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.node import Node
from mininet.log import setLogLevel
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel 
from mininet.node import OVSController

public_network_subnets = dict()

internal_router_list = list()




def fileRead(fileName):

    networks = 1
    network_file = open(fileName, "r")
    for line in network_file:
        line = line.strip('\n').split(' ')
        print(line)



        
        if line[2] not in nat_types:
            print(line[2])
            print("Errore: NAT sconosciuto")
            exit()
        

        elif line[1] in nat_dict and line[2] != nat_dict[line[1]]:
            print("ATTENZIONE,", line[1], "è già associata al NAT", nat_dict[line[1]], "e quindi non verranno apportate modifiche")    

        if line[2] == "public":
            if line[1] not in public_network_topology:
                print("DEBUG: creo una nuova LAN")
                lan_list.append(line[1])
                public_network_topology[line[1]] = list()
                nat_dict[line[1]] = line[2]
                
            
            if line[0] not in node_list:
                node_list.append(line[0])
                public_network_topology[line[1]].append(line[0])
        
    
        else:

            if line[1] not in private_network_topology:
                print("DEBUG: creo una nuova LAN")
                lan_list.append(line[1])
                private_network_topology[line[1]] = list()
                nat_dict[line[1]] = line[2]
                
            
            if line[0] not in node_list:
                
                node_list.append(line[0])
                private_network_topology[line[1]].append(line[0])
        

fileRead("network.txt")



class LinuxRouter( Node ):
    

    
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        #Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate() 




class network(Topo):


    
    
    
    def build_lan(nodes):
        print("ciao")

    def build(self):

        
        self.switchdict = dict()
        self.routersdict = dict()

        router_private_internal_ip = "10.0.0.1"

        self.switchgenerale = self.addSwitch("s1")


        def build_private_lan(lan):
            x = 2
            for nodes in private_network_topology[lan]:
                print(nodes)
                host = self.addHost(nodes, ip="192.168.1.{}".format(x), defaultRoute='via 192.168.1.1')#prima era 10.0.0.1
                self.addLink(host, self.switchdict[lan])
                x = x+1
        def build_public_lan(lan, x):
            default_x = x
            print("Nodi nella sottorete: ", len(public_network_topology[lan]))
            mask, subnet, end_ip = subnet_calculator(default_x, len(public_network_topology[lan]))
            public_network_subnets[lan] = list()
            public_network_subnets[lan].append(subnet)
            print(public_network_subnets)
            print(default_x)
            for nodes in public_network_topology[lan]:
                x = x+1
                print(x)
                print(nodes)
                print("per ", nodes, "default-router: ", "9.0.0.{}".format(default_x))
                host = self.addHost(nodes, ip="9.0.0.{}".format(x)+"/{}".format(32-mask), defaultRoute='via 9.0.0.{}'.format(default_x))
                print("9.0.0.{}".format(x)+"/{}".format(32-mask))
                #host = self.addHost(nodes, ip="9.0.0.{}".format(x))
                #self.host.cmd("route add default gw 9.0.0.{}".format(default_x))
                                    
                self.addLink(host, self.switchdict[lan])
            return end_ip
        
        def subnet_calculator(default_ip, nodes):
            log = math.log2(nodes+2)
            result = int(math.ceil(log))
            print("numero di ip necessari", nodes+2)
            print("risultato", result)
            if result == 1:
                result = 2
            end_ip = int(default_ip + math.pow(2, result))
            return result, str("9.0.0.{}".format(default_ip)) + "/{}".format(32-result), end_ip



                
        
        x = 0
        z = 100
        j = z
        for lan in private_network_topology:
            
            #se la lan è privata
            print("Sto costruendo la LAN: " + lan)
            self.switchdict[lan] = self.addSwitch("switch{}".format(x))
            print(self.switchdict[lan])
            
            self.routersdict[lan] = self.addNode("r{}".format(x), cls=LinuxRouter, ip=router_private_internal_ip+"/24")#prima era rpi
            router = self.addNode("ri{}".format(x), cls=LinuxRouter, ip="10.0.0.2", defaultRoute="10.0.0.1")
            internal_router_list.append(router)
            self.addLink(self.routersdict[lan], router, intfName1='r{}-eth0'.format(x), intfName2='ri{}-eth0'.format(x), params1={'ip': "10.0.0.1/24"}, params2={'ip':'10.0.0.2/24'})
            self.addLink(router, self.switchdict[lan], intfName1='ri{}-eth1'.format(x),params1={'ip': "192.168.1.1/24"})
            self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
            j = j+1
            

            x = x+1
            build_private_lan(lan)

        

        y = 0
        
    
        for lan in public_network_topology:
            print("Sto costruendo la LAN: " + lan)
            self.switchdict[lan] = self.addSwitch("switch{}".format(x))
            print(self.switchdict[lan])
            self.routersdict[lan] = self.addNode("r{}".format(x), cls=LinuxRouter, ip="9.0.0.{}".format(y))
            self.addLink(self.routersdict[lan], self.switchdict[lan], intfName1='r{}-eth0'.format(x),params1={'ip': "9.0.0.{}/24".format(y)} )
            self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
            y = build_public_lan(lan, y)
            public_network_subnets[lan].append("5.0.0.{}".format(x))
            x = x+1


        #REGOLE DI ROUTING
        
            
    

def network_setup(topo, net):
    print("Funzione network_setup")
    print(public_network_subnets)
    x = 0

    for routers in internal_router_list:
        print(net.get(routers).cmd("ip route add default via 10.0.0.1"))




    for lan in private_network_topology:
        #topo.routersdict[lan]
        print(topo.routersdict[lan])
        print(net.get(topo.routersdict[lan]).cmd("ip route add 192.168.1.0/24 via 10.0.0.2"))
        for route in public_network_subnets:
            cmd= "sudo ip route add " + public_network_subnets[route][0] + " via " + public_network_subnets[route][1]
            print("Per il router", topo.routersdict[lan], cmd)
            print(net.get(topo.routersdict[lan]).cmd(cmd))

        nat_type = nat_dict[lan]
        if nat_type == "port_restricted":
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j SNAT --to-source 5.0.0.{}".format(x))
        elif nat_type == "full_cone":
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j FULLCONENAT")
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A PREROUTING -i r{}".format(x)+"-eth1 -j FULLCONENAT")
        elif nat_type == "restricted_cone":
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j FULLCONENAT")
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A PREROUTING -i r{}".format(x)+"-eth1 -j FULLCONENAT --nat-type ar")
        elif nat_type == "symmetric":
            net.get(topo.routersdict[lan]).cmd("iptables --flush")
            net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j MASQUERADE --random")
            net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth1 -o r{}".format(x)+"-eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
            net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth0 -o r{}".format(x)+"-eth1 -j ACCEPT")

            
            
        x = x+1

    for lan in public_network_topology:
        for route in public_network_subnets:
            if route != lan:
                cmd= "sudo ip route add " + public_network_subnets[route][0] + " via " + public_network_subnets[route][1]
                print("Per il router", topo.routersdict[lan], cmd)
                print(net.get(topo.routersdict[lan]).cmd(cmd))












print("reti pubbliche:", public_network_topology)

test = network()

net = Mininet(topo = test, controller = OVSController)
#net.addNAT().configDefault()
net.start()
network_setup(test, net)

dumpNodeConnections(net.hosts)
CLI(net)

for key in private_network_topology:
    print(key)
    print(nat_dict[key])














