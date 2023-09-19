from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
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
import math






lan_list = list()
lan_number_dict = dict()
nat_types = ["full_cone", "restricted_cone", "port_restricted", "symmetric", "public"]
node_list = list()
nat_dict = dict()
private_network_topology = dict()
public_network_topology = dict()
public_network_subnets = dict()
domestic_router_list = list()
switchdict = dict()
routersdict = dict()

routing_dict = dict()

border_router_number = int



last_ip_octect = int

properties_dict = dict()

nat_routers = dict()
core_routers = dict()


subnet_dict = dict()



core_routers_internal_ip = dict()
















def topologyProperties(fileName):

            networks = 1
            network_file = open(fileName, "r")
            for line in network_file:
                line = line.strip('\n').split(' ')
                print("TOP: PROP", line)
        
                if len(line) >= 4:
                    
                    if line[0] and line[1] in lan_list:
                        r1 = "re{}".format(lan_number_dict[line[0]])
                        r2 = "re{}".format(lan_number_dict[line[1]])
                        if r1 not in properties_dict:
                            properties_dict[r1] = dict()
                        properties_dict[r1][r2] = [line[2],line[3]]
                        if r2 not in properties_dict:
                            properties_dict[r2] = dict()
                        properties_dict[r2][r1] = [line[2],line[3]]
        
        
#topologyProperties("properties.txt")
        
        




def fileRead(fileName): #Legge dal file di testo la topologia ed i parametri di rete


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

        for i in range(0, len(lan_list)):
             lan_number_dict[lan_list[i]] = i
             print("LAN NUMBER DICT: ", lan_number_dict )
                




class LinuxRouter( Node ):
    

    
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        #Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate() 


def network_topology_creator(net):
    
  
    router_private_internal_ip = "10.0.0.1"

    
    def build_private_lan(lan): #Genera la rete domestica
            x = 2
            for nodes in private_network_topology[lan]:
                print(nodes)
                print("192.168.1.{}".format(x))
                host = net.addHost(nodes, ip="192.168.1.{}/24".format(x), defaultRoute='via 192.168.1.1')
                host.cmd("ip route flush table main")
                net.addLink(host, switchdict[lan], intfName1=nodes+"-eth0", params1={'ip':"192.168.1.{}/24".format(x)})
                host.cmd("ip route add default via 192.168.1.1")
                x = x+1
    

    def build_public_lan(lan, x, y):
            default_x = x
            print("Nodi nella sottorete: ", len(public_network_topology[lan]))
            mask, subnet, end_ip = subnet_calculator(default_x, len(public_network_topology[lan]))
            #public_network_subnets[lan] = list()
            #public_network_subnets[lan].append(subnet)

            #subnet_dict[y] = subnet #Per la chiave LAN sta creando una lista
            print("LA SUBNET è", subnet)
            #subnet_dict[lan].append(subnet)
            core_routers_internal_ip[y] = subnet




            #print(public_network_subnets)
            #print(default_x)
            for nodes in public_network_topology[lan]:
                x = x+1
                print(x)
                print(nodes)
                print("per ", nodes, "default-router: ", "9.0.0.{}".format(default_x))
                host = net.addHost(nodes, ip="9.0.0.{}".format(x)+"/{}".format(32-mask), defaultRoute='via 9.0.0.{}'.format(default_x))
                #print("9.0.0.{}".format(x)+"/{}".format(32-mask))
                #host = self.addHost(nodes, ip="9.0.0.{}".format(x))
                #self.host.cmd("route add default gw 9.0.0.{}".format(default_x))
                                    
                net.addLink(host, switchdict[lan])
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


    def docker_host_creator(i):
        
        for lan in private_network_topology: #Per ogni LAN privata
            switchdict[lan] = net.addSwitch("switch{}".format(i)) #Istanzia uno switch di LAN che collega tutti i nodi afferenti alla LAN
            build_private_lan(lan)
            i = i+1
        return i
        
    
    x = 0 #Tiene conto del numero dello switch, ovvero x tiene conto del numero di reti private
    y = 0 #Tiene conto dell'ultimo ottetto dell'IP dei server


    x = docker_host_creator(x) #Per prima cosa crea le LAN private


    #Successivamente crea le LAN con indirizzi pubblici (servers)

    for lan in public_network_topology:
        print("Sto costruendo la LAN: " + lan)
        switchdict[lan] = net.addSwitch("switch{}".format(x)) #Aggiunge lo switch di LAN


        core_routers[lan] = net.addHost("re{}".format(x), ip="9.0.0.{}".format(y))#Istanzia il router di frontiera
        core_routers[lan].cmd( 'sysctl net.ipv4.ip_forward=1' )
        net.addLink(core_routers[lan], switchdict[lan], intfName1='re{}-eth0'.format(x),params1={'ip': "9.0.0.{}/24".format(y)} ) #Collega il router di frontiera allo switch
        
        y = build_public_lan(lan, y, x)
        x = x+1


    x = 0

    
    #net.start()
    z = 100
    border_ip = 0
    j = z



    for lan in private_network_topology:
            
        
        
        border_router_internal_ip = "5.0.0.{}/24".format(border_ip)

        nat_router_internal_ip = "10.0.0.1/24"

        nat_router_external_ip = "5.0.0.{}/32".format(border_ip+1)

        



        # ____________________ - DEFINIZIONE ROUTERS - ______________________________
        
        nat_routers[lan] = net.addHost("r{}".format(x),cls=LinuxRouter, ip=router_private_internal_ip+"/24") #Router che applica CG-NAT
        domestic_router = net.addHost("ri{}".format(x), ip="10.0.0.2", defaultRoute="via 10.0.0.1", cls=LinuxRouter) #Router domestico
        core_routers[lan] = net.addHost("re{}".format(x),cls=LinuxRouter, ip=border_router_internal_ip) #Router di frontiera
        domestic_router_list.append(domestic_router)

        core_routers_internal_ip[x] = nat_router_external_ip




        # _______________ - ABILITAZIONE IP FORWARDING - __________________________
        
        nat_routers[lan].cmd( 'sysctl net.ipv4.ip_forward=1' )
        domestic_router.cmd( 'sysctl net.ipv4.ip_forward=1' )
        # __________________________________________________________________________


        
        # ______________ - GENERAZIONE DEI LINK - _____________________________________
        
        
        
        
        #Router domestico ----> WAN (Router NAT) 

        net.addLink(nat_routers[lan], domestic_router, intfName1='r{}-eth0'.format(x), intfName2='ri{}-eth0'.format(x), params1={'ip':nat_router_internal_ip}, params2={'ip':'10.0.0.2/24'})
        
        
        #Router domestico ----> switch lan
        net.addLink(domestic_router, switchdict[lan], intfName1='ri{}-eth1'.format(x),params1={'ip': "192.168.1.1/24"})
        
        #Router NAT ------> Router CORE

        net.addLink(nat_routers[lan], core_routers[lan], intfName='r{}-eth1'.format(x), intfName2='re{}-eth0'.format(x), params1={'ip':nat_router_external_ip}, params2={'ip':border_router_internal_ip})



        # _______________ - REGOLE DI ROUTING - __________________________-


        
        domestic_router.cmd("ip route add default via 10.0.0.1")
        print(domestic_router.cmd("ifconfig"))
        nat_routers[lan].cmd("ip route add 192.168.1.0/24 via 10.0.0.2")
        print("PER IL ROUTER NAT:   ", border_router_internal_ip[:-3])
        print(nat_routers[lan].cmd("ip route add ", border_router_internal_ip[:-3], " dev r{}-eth1".format(x)))
        print(nat_routers[lan].cmd("ip route add default via ", border_router_internal_ip[:-3]))
        
        
        # _____________________ - REGOLE DI NAT - _____________________________

        nat_type = nat_dict[lan]

        if nat_type == "port_restricted":
            cmd = "iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j FULLCONENAT"
            cmd1 = "iptables -t nat -A PREROUTING -i r{}".format(x)+"-eth1 -j FULLCONENAT --nat-type pr"
            nat_routers[lan].cmd(cmd)
            nat_routers[lan].cmd(cmd1)
        elif nat_type == "full_cone":
            cmd = "iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j FULLCONENAT"
            cmd1 = "iptables -t nat -A PREROUTING -i r{}".format(x)+"-eth1 -j FULLCONENAT"
            nat_routers[lan].cmd(cmd)
            nat_routers[lan].cmd(cmd1)
        elif nat_type == "restricted_cone":
            cmd = "iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j FULLCONENAT"
            cmd1 = "iptables -t nat -A PREROUTING -i r{}".format(x)+"-eth1 -j FULLCONENAT --nat-type ar"
            nat_routers[lan].cmd(cmd)
            nat_routers[lan].cmd(cmd1)
        elif nat_type == "symmetric":
            nat_routers[lan].cmd("iptables --flush")
                #net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j MASQUERADE --random")
            cmd1 = "iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j MASQUERADE --random"
            cmd2 = "iptables -A FORWARD -i r{}".format(x)+"-eth1 -o r{}".format(x)+"-eth0 -m state --state RELATED, ESTABLISHED -j ACCEPT"
            cmd3 = "iptables -A FORWARD -i r{}".format(x)+"-eth0 -o r{}".format(x)+"-eth1 -j ACCEPT"
            
            nat_routers[lan].cmd(cmd1)
            nat_routers[lan].cmd(cmd2)
            nat_routers[lan].cmd(cmd3)





        
        #net.addLink(nat_routers[lan], switchgenerale, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r{}-eth1'.format(x), params1={'ip': "5.0.0.{}/24".format(x)}, use_htb=True)
        
        
        j = j+1
        x = x+1
        border_ip = border_ip+2 
        
    


        

    y = 0
        

        #REGOLE DI ROUTING
    

    topologyProperties("properties.txt")
    print("PROPRIETA' RETE:", properties_dict)


    print("L'ultima cagata che ho fatto:    ", core_routers_internal_ip)

    print("creo la rete full mesh tra i router: " + str(core_routers))
        #print(len(self.routersdict))

    print("ROUTING DICT:  ", routing_dict)
    r2_intf = 1
    r1_intf = 1

    r1_ip = 0
    r2_ip = r1_ip + 1

    for r1 in range(0, len(core_routers)):  #Prende un router R1 
            print("collego " + "re{}".format(r1))
            if "re{}".format(r1) not in routing_dict:
                routing_dict["re{}".format(r1)] = dict() #Se non è già presente nel dizionario del routing lo inserisce
            r2 = r1 +1 
            while r2 < len(core_routers): #Per ogni altro router R2 nella lista dei routers esterni
                
                
                #Se per questo specifico link è stata specificata una proprietà:
                if "re{}".format(r1) in properties_dict and "re{}".format(r2) in properties_dict["re{}".format(r1)]:
                    dl = int((properties_dict["re{}".format(r1)]["re{}".format(r2)][0]))/2
                    dl = str(dl)+"ms"
                    speed = int(properties_dict["re{}".format(r1)]["re{}".format(r2)][1])
                
                    print("Collego re{}".format(r1) + "-eth{}".format(r1_intf) + " al router re{}".format(r2)+"-eth{}".format(r2_intf) +" ip1: 151.0.0.{}".format(r1_ip) + " ip2: 151.0.0.{}".format(r2_ip) + " con latenza " + dl+ " e banda: ",speed, "Mbps") 
                    net.addLink("re{}".format(r1), "re{}".format(r2), cls=TCLink, delay=dl, jitter='2ms', bw=speed, intfName1='re{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='re{}'.format(r2)+'-eth{}'.format(r2_intf), params1={'ip': "151.0.0.{}/31".format(r1_ip)}, params2={'ip': "151.0.0.{}/31".format(r2_ip)},use_htb=True)
                
                #Altrimenti
                else:
                    print("Collego re{}".format(r1) + "-eth{}".format(r1_intf) + " al router re{}".format(r2)+"-eth{}".format(r2_intf) +" ip1: 151.0.0.{}".format(r1_ip) + " ip2: 151.0.0.{}".format(r2_ip)) 
                    net.addLink("re{}".format(r1), "re{}".format(r2), cls=TCLink, delay='1ms', jitter='2ms', intfName1='re{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='re{}'.format(r2)+'-eth{}'.format(r2_intf), params1={'ip': "151.0.0.{}/31".format(r1_ip)}, params2={'ip': "151.0.0.{}/31".format(r2_ip)},use_htb=True)
                #r1_dict = dict()
                #r1_dict["r{}".format(r2)] = "5.0.0.{}/24".format(r2_ip)


                route_r1_cmd = "ip route add " + core_routers_internal_ip[r2] + " via 151.0.0.{}".format(r2_ip)
                route_r2_cmd = "ip route add " + core_routers_internal_ip[r1] + " via 151.0.0.{}".format(r1_ip)
                
                print("STO IMPOSTANDO LA REGOLA DI ROUTING PER R{}:  ".format(r1),route_r1_cmd)
                net.getNodeByName("re{}".format(r1)).cmd(route_r1_cmd)
                routing_dict["re{}".format(r1)]["r{}".format(r2)] = "151.0.0.{}/24".format(r2_ip)

                print("STO IMPOSTANDO LA REGOLA DI ROUTING PER R{}:  ".format(r2),route_r2_cmd)
                net.getNodeByName("re{}".format(r2)).cmd(route_r2_cmd)



                if "re{}".format(r2) not in routing_dict:
                    routing_dict["re{}".format(r2)] = dict()
                #r2_dict = dict()
                #r2_dict["r{}".format(r1)] = "5.0.0.{}".format(r1_ip)
                routing_dict["re{}".format(r2)]["re{}".format(r1)] = "151.0.0.{}/24".format(r1_ip)
                #print(routing_dict)
                r2 = r2 + 1
                r1_ip = r2_ip + 1
                r2_ip = r1_ip + 1
                r1_intf = r1_intf + 1

            r1_intf = r2_intf + 1
            r2_intf = r2_intf + 1

            print("ROUTING:" ,routing_dict)
        

def network_setup(net):
    print("Funzione network_setup")
    print("Reti pubbliche: ", public_network_subnets)
    #print("Routers:", topo.routersdict)
    x = 0

    

    for lan in private_network_topology:
        #topo.routersdict[lan]
        #print(topo.routersdict[lan])
        #print(net.get(topo.routersdict[lan]).cmd("ip route add 192.168.1.0/24 via 10.0.0.2"))
        for route in public_network_subnets:
            
            #print("routing tra " + core_routers[lan] + core_routers[route] + " per raggiungere" + public_network_subnets[route])
            #print(routing_dict[core_routers[lan]][core_routers[route]][:-3])
            
            
            cmd= "sudo ip route add " + public_network_subnets[route] + " via " + routing_dict[core_routers[lan]][core_routers[route]][:-3]
            #print("Per il router", core_routers[lan], cmd)
            core_routers[lan].cmd(cmd)

        nat_type = nat_dict[lan]
        x = 1
        while(x < len(routing_dict)): 
            if nat_type == "port_restricted":
                cmd = "iptables -t nat -A POSTROUTING -o "+ nat_routers[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ nat_routers[lan]+"-eth{}".format(x) +" -j FULLCONENAT --nat-type pr"
                print(cmd)
                print(cmd1)
                nat_routers.cmd(cmd)
                nat_routers.cmd(cmd1)
            elif nat_type == "full_cone":
                cmd = "iptables -t nat -A POSTROUTING -o "+ nat_routers[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ nat_routers[lan]+"-eth{}".format(x) +" -j FULLCONENAT"
                print(cmd)
                print(cmd1)
                nat_routers.cmd(cmd)
                nat_routers.cmd(cmd1)
            elif nat_type == "restricted_cone":
                cmd = "iptables -t nat -A POSTROUTING -o "+ nat_routers+"-eth{}".format(x) +" -j FULLCONENAT"
                cmd1 = "iptables -t nat -A PREROUTING -i "+ nat_routers+"-eth{}".format(x) +" -j FULLCONENAT --nat-type ar"
                print(cmd)
                print(cmd1)
                nat_routers.cmd(cmd)
                nat_routers.cmd(cmd1)
            elif nat_type == "symmetric":
                print("\n \n symmetric")
                nat_routers.cmd("iptables --flush")
                #net.get(topo.routersdict[lan]).cmd("iptables -t nat -A POSTROUTING -o r{}".format(x)+"-eth1 -j MASQUERADE --random")
                cmd1 = "iptables -t nat -A POSTROUTING -o "+ nat_routers[lan]+"-eth{}".format(x) +" -j MASQUERADE --random"
                cmd2 = "iptables -A FORWARD -i "+ nat_routers[lan]+"-eth{}".format(x)+" -o "+nat_routers[lan]+"-eth0 -m state --state RELATED, ESTABLISHED -j ACCEPT"
                #net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth1 -o r{}".format(x)+"-eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
                cmd3 = "iptables -A FORWARD -i "+nat_routers[lan]+"-eth0 -o "+topo.routersdict[lan]+"-eth{}".format(x)+" -j ACCEPT"
                nat_routers.cmd(cmd1)
                nat_routers.cmd(cmd2)
                nat_routers.cmd(cmd3)

                #print(cmd1, cmd2, cmd3)

                #net.get(topo.routersdict[lan]).cmd("iptables -A FORWARD -i r{}".format(x)+"-eth0 -o r{}".format(x)+"-eth1 -j ACCEPT")
            x = x+1

            
            
        x = x+1

    for lan in public_network_topology:
        for route in public_network_subnets:
            print(lan)
            print(route)
            if route != lan:
                print("routing tra " + nat_routers[lan] + nat_routers[route] + " per raggiungere" + public_network_subnets[route])
                print(routing_dict[nat_routers[lan]][nat_routers[route]][:-3])
                cmd= "sudo ip route add " + public_network_subnets[route] + " via " + routing_dict[nat_routers[lan]][nat_routers[route]][:-3]
                print("Per il router", nat_routers[lan], cmd)
                print(nat_routers[lan]).cmd(cmd)




fileRead("network.txt")



net=Mininet(waitConnected=True )
net.addController('c0')



network_topology_creator(net)
#net.start()
print("Router core:  ", core_routers)
net.start()
#network_setup(net)



#dumpNodeConnections(net.hosts)
CLI(net)
net.stop()

for key in private_network_topology:
    print(key)
    print(nat_dict[key])









