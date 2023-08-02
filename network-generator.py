
lan_list = list()
nat_types = ["full_cone", "restricted_cone", "port_restricted", "symmetric", "public"]
node_list = list()
nat_dict = dict()
private_network_topology = dict()
public_network_topology = dict()
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




def fileRead(fileName):

    networks = 1
    network_file = open(fileName, "r")
    for line in network_file:
        line = line.strip('\n').split(' ')



        
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
                host = self.addHost(nodes, ip="10.0.0.{}".format(x), defaultRoute='via 10.0.0.1')
                self.addLink(host, self.switchdict[lan])
                x = x+1
        def build_public_lan(lan, x):
            default_x = x
            print(default_x)
            for nodes in public_network_topology[lan]:
                x = x+1
                print(x)
                print(nodes)
                host = self.addHost(nodes, ip="9.0.0.{}".format(x), defaultRoute='via 9.0.0.{}'.format(default_x))
                self.addLink(host, self.switchdict[lan])
            return x+1
                
        
        x = 0
        for lan in private_network_topology:
            
            #se la lan è privata
            print("Sto costruendo la LAN: " + lan)
            self.switchdict[lan] = self.addSwitch("switch{}".format(x))
            print(self.switchdict[lan])
            self.routersdict[lan] = self.addNode("r{}".format(x), cls=LinuxRouter, ip=router_private_internal_ip)
            self.addLink(self.routersdict[lan], self.switchdict[lan], intfName1='r{}-eth0'.format(x),params1={'ip': router_private_internal_ip+"/24"} )
            self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
            x = x+1
            build_private_lan(lan)

        

        y = 1
        
    
        for lan in public_network_topology:
            print("Sto costruendo la LAN: " + lan)
            self.switchdict[lan] = self.addSwitch("switch{}".format(x))
            print(self.switchdict[lan])
            self.routersdict[lan] = self.addNode("r{}".format(x), cls=LinuxRouter, ip="9.0.0.{}".format(y))
            self.addLink(self.routersdict[lan], self.switchdict[lan], intfName1='r{}-eth0'.format(x),params1={'ip': "9.0.0.{}/24".format(y)} )
            self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
            y = build_public_lan(lan, y)
            x = x+1
            






print("reti pubbliche:", public_network_topology)

test = network()

net = Mininet(topo = test, controller = OVSController)
net.start()

dumpNodeConnections(net.hosts)
CLI(net)

for key in private_network_topology:
    print(key)
    print(nat_dict[key])














