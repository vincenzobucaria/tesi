lan_list = list()
nat_types = ["full_cone", "restricted_cone", "port_restricted", "symmetric", "public"]
node_list = list()
nat_dict = dict()
private_network_topology = dict()
public_network_topology = dict()
properties_dict = dict()
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

link_properties = dict()




routing_dict = dict()



def topologyRead(fileName):

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




            
        
topologyRead("network.txt")


print("NUOVO DIZIONARIO:", properties_dict)



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
            
            public_network_subnets[lan] = subnet
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
            #self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
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
            #self.addLink(self.routersdict[lan], self.switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
            y = build_public_lan(lan, y)
            #public_network_subnets[lan].append("5.0.0.{}".format(x))
            x = x+1


        
        def topologyProperties(fileName):

            networks = 1
            network_file = open(fileName, "r")
            for line in network_file:
                line = line.strip('\n').split(' ')
                print(line)
        
                if len(line) >= 4:
                    
                    if line[0] and line[1] in lan_list:
                        r1 = self.routersdict[line[0]]
                        r2 = self.routersdict[line[1]]
                        if r1 not in properties_dict:
                            properties_dict[r1] = dict()
                        properties_dict[r1][r2] = [line[2],line[3]]
                        if r2 not in properties_dict:
                            properties_dict[r2] = dict()
                        properties_dict[r2][r1] = [line[2],line[3]]
        
        print(self.routersdict)
        topologyProperties("properties.txt")
        print(properties_dict)
        
        
        
        
        
        
        #CREAZIONE RETE FULL-MESH ROUTER
        
        print("creo la rete full mesh tra i router: " + str(self.routersdict))
        print(len(self.routersdict))

        r2_intf = 1
        r1_intf = 1

        r1_ip = 0
        r2_ip = r1_ip + 1

        for r1 in range(0, len(self.routersdict)):
            print("collego " + "r{}".format(r1))
            if "r{}".format(r1) not in routing_dict:
                routing_dict["r{}".format(r1)] = dict()
            r2 = r1 +1 
            while r2 < len(self.routersdict):
                
                if "r{}".format(r1) in properties_dict and "r{}".format(r2) in properties_dict["r{}".format(r1)]:
                    dl = int((properties_dict["r{}".format(r1)]["r{}".format(r2)][0]))/2
                    dl = str(dl)+"ms"
                    speed = int(properties_dict["r{}".format(r1)]["r{}".format(r2)][1])
                
                    print("Collego r{}".format(r1) + "-eth{}".format(r1_intf) + " al router r{}".format(r2)+"-eth{}".format(r2_intf) +" ip1: 5.0.0.{}".format(r1_ip) + " ip2: 5.0.0.{}".format(r2_ip) + " con latenza " + dl+ " e banda: ",speed, "Mbps") 
                    self.addLink("r{}".format(r1), "r{}".format(r2), cls=TCLink, delay=dl, jitter='2ms', bw=speed, intfName1='r{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='r{}'.format(r2)+'-eth{}'.format(r2_intf), params1={'ip': "5.0.0.{}/31".format(r1_ip)}, params2={'ip': "5.0.0.{}/31".format(r2_ip)},use_htb=True)
                
                else:
                    print("Collego r{}".format(r1) + "-eth{}".format(r1_intf) + " al router r{}".format(r2)+"-eth{}".format(r2_intf) +" ip1: 5.0.0.{}".format(r1_ip) + " ip2: 5.0.0.{}".format(r2_ip)) 
                    self.addLink("r{}".format(r1), "r{}".format(r2), cls=TCLink, delay='1ms', jitter='2ms', intfName1='r{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='r{}'.format(r2)+'-eth{}'.format(r2_intf), params1={'ip': "5.0.0.{}/31".format(r1_ip)}, params2={'ip': "5.0.0.{}/31".format(r2_ip)},use_htb=True)
                #r1_dict = dict()
                #r1_dict["r{}".format(r2)] = "5.0.0.{}/24".format(r2_ip)
                routing_dict["r{}".format(r1)]["r{}".format(r2)] = "5.0.0.{}/24".format(r2_ip)

                if "r{}".format(r2) not in routing_dict:
                    routing_dict["r{}".format(r2)] = dict()
                #r2_dict = dict()
                #r2_dict["r{}".format(r1)] = "5.0.0.{}".format(r1_ip)
                routing_dict["r{}".format(r2)]["r{}".format(r1)] = "5.0.0.{}/24".format(r1_ip)
                #print(routing_dict)
                r2 = r2 + 1
                r1_ip = r2_ip + 1
                r2_ip = r1_ip + 1
                r1_intf = r1_intf + 1

            r1_intf = r2_intf + 1
            r2_intf = r2_intf + 1

        print("ROUTING:" ,routing_dict)
            
            
            
            #while(k<len(self.routersdict)-1):
                #print("sto collegando r{}".format(i) + " sull'interfaccia eth{}".format(k) + " al router r{}".format(k) + " sull'interfaccia eth{}".format(j) + "ip: 5.0.0.{}/24".format(z) + ", ip: 5.0.0.{}/24".format(y))
                #self.addLink("r{}".format(i), "r{}".format(k), cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}'.format(i)+'-eth{}'.format(k), intfName2='r{}'.format(k)+'-eth{}'.format(j), params1={'ip': "5.0.0.{}/24".format(z)}, params2={'ip': "5.0.0.{}/24".format(y)},use_htb=True)
              
           

        
            
    

def network_setup(topo, net):
    print("Funzione network_setup")
    print("Reti pubbliche: ", public_network_subnets)
    print("Routers:", topo.routersdict)
    x = 0

    for routers in internal_router_list:
        print(net.get(routers).cmd("ip route add default via 10.0.0.1"))




    for lan in private_network_topology:
        #topo.routersdict[lan]
        print(topo.routersdict[lan])
        print(net.get(topo.routersdict[lan]).cmd("ip route add 192.168.1.0/24 via 10.0.0.2"))
        for route in public_network_subnets:
            
            print("routing tra " + topo.routersdict[lan] + topo.routersdict[route] + " per raggiungere" + public_network_subnets[route])
            print(routing_dict[topo.routersdict[lan]][topo.routersdict[route]][:-3])
            
            
            cmd= "sudo ip route add " + public_network_subnets[route] + " via " + routing_dict[topo.routersdict[lan]][topo.routersdict[route]][:-3]
            print("Per il router", topo.routersdict[lan], cmd)
            print(net.get(topo.routersdict[lan]).cmd(cmd))

        nat_type = nat_dict[lan]
        x = 1
        while(x < len(routing_dict)): 
            if nat_type == "port_restricted":
                cmd = "iptables -t nat -A POSTROUTING -o "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT --nat-type pr"
                print(cmd)
                print(cmd1)
                net.get(topo.routersdict[lan]).cmd(cmd)
                net.get(topo.routersdict[lan]).cmd(cmd1)
            elif nat_type == "full_cone":
                cmd = "iptables -t nat -A POSTROUTING -o "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                print(cmd)
                print(cmd1)
                net.get(topo.routersdict[lan]).cmd(cmd)
                net.get(topo.routersdict[lan]).cmd(cmd1)
            elif nat_type == "restricted_cone":
                cmd = "iptables -t nat -A POSTROUTING -o "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j FULLCONENAT --nat-type ar"
                print(cmd)
                print(cmd1)
                net.get(topo.routersdict[lan]).cmd(cmd)
                net.get(topo.routersdict[lan]).cmd(cmd1)
            elif nat_type == "symmetric":
                print("\n \n symmetric")
                net.get(topo.routersdict[lan]).cmd("iptables --flush")
                #net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j MASQUERADE --random")
                cmd1 = "iptables -t nat -A POSTROUTING -o "+ topo.routersdict[lan]+"-eth{}".format(x) +" -j MASQUERADE --random"
                cmd2 = "iptables -A FORWARD -i "+ topo.routersdict[lan]+"-eth{}".format(x)+" -o "+topo.routersdict[lan]+"-eth0 -m state --state RELATED, ESTABLISHED -j ACCEPT"
                #net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth1 -o r{}".format(x)+"-eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
                cmd3 = "iptables -A FORWARD -i "+topo.routersdict[lan]+"-eth0 -o "+topo.routersdict[lan]+"-eth{}".format(x)+" -j ACCEPT"
                net.get(topo.routersdict[lan]).cmd(cmd1)
                net.get(topo.routersdict[lan]).cmd(cmd2)
                net.get(topo.routersdict[lan]).cmd(cmd3)

                #print(cmd1, cmd2, cmd3)

                net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth0 -o r{}".format(x)+"-eth1 -j ACCEPT")
            x = x+1

            
            
        x = x+1

    for lan in public_network_topology:
        for route in public_network_subnets:
            print(lan)
            print(route)
            if route != lan:
                print("routing tra " + topo.routersdict[lan] + topo.routersdict[route] + " per raggiungere" + public_network_subnets[route])
                print(routing_dict[topo.routersdict[lan]][topo.routersdict[route]][:-3])
                cmd= "sudo ip route add " + public_network_subnets[route] + " via " + routing_dict[topo.routersdict[lan]][topo.routersdict[route]][:-3]
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
