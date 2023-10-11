import subprocess
import time
from mininet.topo import Topo
import os
import subprocess 
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
from threading import Thread
from multiprocessing import Process
import shutil
from mininet.util import pmonitor
import math
from multiprocessing import Process
from mininet.util import pmonitor
import threading
import pexpect


lan_list = list() #Lista che permette di memorizzare le LAN presenti nella topologia
lan_number_dict = dict() #Dizionario che associa una LAN ad un numero
nat_types = ["full_cone", "restricted_cone", "port_restricted", "symmetric", "public"] #Tipi di NAT ammessi
node_list = list() #Lista contenente tutti i nodi della topologia 
nat_dict = dict() #Dizionario contenente (LAN->nat_type)
private_network_topology = dict() #Dizionario con chiavi le LAN private e valori i nodi appartenenti a tali LAN
public_network_topology = dict() #Dizionario con chiavi le LAN pubbliche e valori i nodi appartenenti a tali LAN
domestic_router_list = list() #Contiene i nomi di tutti i router domestici
switchdict = dict() #Contiene i nomi di tutti gli switch (la chiave è la LAN di appartenenza)
routing_dict = dict() #Dizionario con chiavi i router di frontiera della topologia, i valori sono i router collegati (e relativa interfaccia pubblica) al router che costituisce la chiave
properties_dict = dict() #Dizionario con chiavi i router di frontiera, i valori sono a loro volta dizionari con chiavi altri router di frontiera, i valori sono le proprietà degli archi tra il router costituente la chiave del dizionario primario e del dizionario secondario

nat_routers = dict() #Dizionario con chiave il nome della LAN e valore il nome del router applicante il NAT per tale LAN.
core_routers = dict() #Dizionario con chiave il nome della LAN e valore il relativo router di frontiera
core_routers_internal_ip = dict() #Dizionario con chiavi i router di frontiera e valori i loro ip dell'interfaccia interna

servers = list() #Lista che contiene i nodi che possono agire da STUN e signaling server






def topologyProperties(fileName): #Permette di leggere le proprietà desiderate per ciascun arco specificato (ne crea poi le strutture dati necessarie)

            
            network_file = open(fileName, "r") #Apre il file in cui sono descritte le proprietà degli archi
            for line in network_file:
                line = line.strip('\n').split(' ') #Da ogni riga estrae ciascuna keyword
                if len(line) >= 4: #Controlla che l'utente abbia specificato tutti i parametri (lan1_name, lan2_name, latenza, banda)
                    
                    if line[0] and line[1] in lan_list: #Controlla che effittamente la LAN selezionata esista
                        r1 = "re{}".format(lan_number_dict[line[0]]) #Prendendo il numero della LAN e conseguentemente il numero del router compone la stringa re[numero-router] per individuare il router di frontiera dove applicare le regole
                        r2 = "re{}".format(lan_number_dict[line[1]])
                        if r1 not in properties_dict: 
                            properties_dict[r1] = dict()
                        properties_dict[r1][r2] = [line[2],line[3]] 
                        if r2 not in properties_dict:
                            properties_dict[r2] = dict()
                        properties_dict[r2][r1] = [line[2],line[3]]
        
        
def fileRead(fileName): #Legge dal file di testo la topologia ed i parametri di rete


    network_file = open(fileName, "r") #Apre il file in modalità lettura
    for line in network_file:
        line = line.strip('\n').split(' ') #E separa le varie parole 
       



        if line[2] not in nat_types: #Controlla che il NAT descritto nel file sia esistente
            print("Errore: NAT sconosciuto")
            exit()
        

        elif line[1] in nat_dict and line[2] != nat_dict[line[1]]:
            print("ATTENZIONE,", line[1], "è già associata al NAT", nat_dict[line[1]], "e quindi non verranno apportate modifiche")  #Se ad una LAN è già stato associato un NAT, ignora la nuova assegnazione  

        if line[2] == "public": 
            if line[1] not in public_network_topology: #Crea la LAN se questa non è già nel dizionario
                lan_list.append(line[1])
                public_network_topology[line[1]] = list() 
                nat_dict[line[1]] = line[2] #Associa il tipo di "NAT" (in questo caso è improprio parlare di NAT perchè la LAN è pubblica)
            if line[0] not in node_list: #Associa i nodi alla LAN, se questi non sono già stati definiti (non possono esserci nodi con lo stesso nome)
                node_list.append(line[0])
                public_network_topology[line[1]].append(line[0])


            try:
                if line[3] == "SERVER":
                    if len(servers) < 2:
                        servers.append(line[0])
                    else:
                        print("\n\n Attenzione, su Mininet è possibile definire soltanto uno server. \n Il server sarà il primo nodo che è stato dichiarato come server. \n I successivi verranno ignorati")
            except:
                 pass
        
    
        else:

            if line[1] not in private_network_topology: #Crea la LAN se questa non è già nel dizionario
                lan_list.append(line[1])
                private_network_topology[line[1]] = list()
                nat_dict[line[1]] = line[2] #Associa il tipo di NAT alla LAN
                
            
            if line[0] not in node_list:
                
                node_list.append(line[0]) #Associa i nodi alla LAN, se questi non sono già stati definiti (non possono esserci nodi con lo stesso nome)
                private_network_topology[line[1]].append(line[0])

            #myString = '12345pippopluto'
        for i in range(0, len(lan_list)):
            #lan_number = re.match('\d+', myString)
            lan_number_dict[lan_list[i]] = i #Associa ad ogni LAN un numero
             
                

class LinuxRouter( Node ): #Definisce la classe LinuxRouter, i nodi che usano questa classe presentano l'ip forward abilitato.
    

    
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        #Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate() 


def network_topology_creator(net): #Funzione che permette di istanziare la topologia
    
  
    nat_private_internal_ip = "10.0.0.1" #Ip dell'interfaccia interna del router NAT

    
    def build_private_lan(lan): #Genera la rete domestica relativa a una LAN (passata come parametro)
            x = 2 #Poichè l'indirizzo del gateway domestico sarà 192.168.1.1, il primo ip disponibile per i nodi è 192.168.1.2
            for nodes in private_network_topology[lan]:
                host = net.addHost(nodes, ip="192.168.1.{}/24".format(x), defaultRoute='via 192.168.1.1') #Istanzia il nodo e imposta il default gateway
                host.cmd("ip route flush table main") #Per evitare problemi con mininet ho ritenuto necessario fare il flush della routing table
                net.addLink(host, switchdict[lan], intfName1=nodes+"-eth0", params1={'ip':"192.168.1.{}/24".format(x)}) #Successivamente si collega il nodo allo switch della LAN
                host.cmd("ip route add default via 192.168.1.1") #Dunque re-imposto il default gateway
                x = x+1 #Si incrementa l'ottetto 
    

    def build_public_lan(lan, x, y): #Genera la rete pubblica relativa a una LAN (passata come parametro)
            default_x = x
            mask, subnet, new_start_ip = subnet_calculator(default_x, len(public_network_topology[lan])) #E' necessario determinare la maschera di sottorete per garantire un routing corretto
            core_routers_internal_ip[y] = subnet


            for nodes in public_network_topology[lan]: #Successivamente istanzia tutti i nodi pubblici della LAN
                x = x+1
                host = net.addHost(nodes, ip="9.0.0.{}".format(x)+"/{}".format(32-mask), defaultRoute='via 9.0.0.{}'.format(default_x))
                #print(host.name)
                net.addLink(host, switchdict[lan])
            return new_start_ip




    def subnet_calculator(default_ip, nodes): #Funzione che permette di determinare la maschera di sottorete
            log = math.log2(nodes+2)
            result = int(math.ceil(log))
            if result == 1:
                result = 2
            new_start_ip = int(default_ip + math.pow(2, result))
            return result, str("9.0.0.{}".format(default_ip)) + "/{}".format(32-result), new_start_ip


    def host_creator(i):
        
        for lan in private_network_topology: #Per ogni LAN privata
            switchdict[lan] = net.addSwitch("switch{}".format(i)) #Istanzia uno switch di LAN che collega tutti i nodi afferenti alla LAN
            build_private_lan(lan) #Dunque chiama la funzione build_private_lan che si occuperà di istanziare tutti i nodi della LAN
            i = i+1
        return i
        
    
    x = 0 #Tiene conto del numero dello switch
    y = 0 #Tiene conto dell'ultimo ottetto dell'IP dei nodi pubblici


    switch_number = host_creator(x) #Per prima cosa crea le LAN private
    router_number = 0


    #Successivamente crea le sottoreti con indirizzi pubblici 

    for lan in public_network_topology:
        router_number = lan_number_dict[lan]
        switchdict[lan] = net.addSwitch("switch{}".format(switch_number)) #Aggiunge lo switch di LAN
        core_routers[lan] = net.addHost("re{}".format(router_number), ip="9.0.0.{}".format(y), cls=LinuxRouter)#Istanzia il router core di frontiera
        core_routers[lan].cmd( 'sysctl net.ipv4.ip_forward=1' )
        net.addLink(core_routers[lan], switchdict[lan], intfName1='re{}-eth0'.format(router_number),params1={'ip': "9.0.0.{}/24".format(y)} ) #Collega il router allo switch
        
        y = build_public_lan(lan, y, router_number) #y tiene conto dell'ultimo ottetto dell'IP dei nodi pubblici
        


    x = 0
    border_ip = 0 #Permette di assegnare IP unici ai router di frontiera (presso l'interfaccia esterna e anche interna)
    



    for lan in private_network_topology:
            
        
        router_number = lan_number_dict[lan]
        border_router_internal_ip = "5.0.0.{}/24".format(border_ip)
        nat_router_internal_ip = "10.0.0.1/24"
        nat_router_external_ip = "5.0.0.{}/32".format(border_ip+1)

        
        # ____________________ - DEFINIZIONE ROUTERS - ______________________________
        
        nat_routers[lan] = net.addHost("r{}".format(router_number),cls=LinuxRouter, ip=nat_private_internal_ip+"/24") #Router che applica CG-NAT
        domestic_router = net.addHost("ri{}".format(router_number), ip="10.0.0.2", defaultRoute="via 10.0.0.1", cls=LinuxRouter) #Router domestico
        core_routers[lan] = net.addHost("re{}".format(router_number),cls=LinuxRouter, ip=border_router_internal_ip) #Router di frontiera
        domestic_router_list.append(domestic_router) #Appende il il router domestico alla lista dei router domestici
        core_routers_internal_ip[router_number] = nat_router_external_ip

        # ______________ - GENERAZIONE DEI LINK - _____________________________________
        
        
        #Router domestico ----> WAN (Router NAT) 

        net.addLink(nat_routers[lan], domestic_router, intfName1='r{}-eth0'.format(router_number), intfName2='ri{}-eth0'.format(router_number), params1={'ip':nat_router_internal_ip}, params2={'ip':'10.0.0.2/24'})
        
        
        #Router domestico ----> switch lan
        net.addLink(domestic_router, switchdict[lan], intfName1='ri{}-eth1'.format(router_number),params1={'ip': "192.168.1.1/24"})
        
        #Router NAT ------> Router CORE

        net.addLink(nat_routers[lan], core_routers[lan], intfName='r{}-eth1'.format(router_number), intfName2='re{}-eth0'.format(router_number), params1={'ip':nat_router_external_ip}, params2={'ip':border_router_internal_ip})



        # _______________ - REGOLE DI ROUTING - __________________________-


        
        domestic_router.cmd("ip route add default via 10.0.0.1")
        #print(domestic_router.cmd("ifconfig"))
        #nat_routers[lan].cmd("ip route add 192.168.1.0/24 via 10.0.0.2")
        #print("PER IL ROUTER NAT:   ", border_router_internal_ip[:-3])
        nat_routers[lan].cmd("ip route add ", border_router_internal_ip[:-3], " dev r{}-eth1".format(router_number))
        nat_routers[lan].cmd("ip route add default via ", border_router_internal_ip[:-3])
        
        
        # _____________________ - SETUP NAT - _____________________________

        
        cmd1 = "iptables -t nat -A POSTROUTING -o ri{}".format(router_number)+"-eth0 -j FULLCONENAT"
        cmd2 = "iptables -t nat -A PREROUTING -i ri{}".format(router_number)+"-eth0 -j FULLCONENAT"
        domestic_router.cmd(cmd1)
        domestic_router.cmd(cmd2)
        nat_type = nat_dict[lan]

        if nat_type == "port_restricted":
            nat_routers[lan].cmd("iptables -t nat -A POSTROUTING -o r{}".format(router_number)+"-eth1 -j FULLCONENAT")
            nat_routers[lan].cmd("iptables -t nat -A PREROUTING -i r{}".format(router_number)+"-eth1 -j FULLCONENAT --nat-type pr")
        elif nat_type == "full_cone":
            nat_routers[lan].cmd("iptables -t nat -A POSTROUTING -o r{}".format(router_number)+"-eth1 -j FULLCONENAT")
            nat_routers[lan].cmd("iptables -t nat -A PREROUTING -i r{}".format(router_number)+"-eth1 -j FULLCONENAT")
        elif nat_type == "restricted_cone":
            nat_routers[lan].cmd("iptables -t nat -A POSTROUTING -o r{}".format(router_number)+"-eth1 -j FULLCONENAT")
            nat_routers[lan].cmd("iptables -t nat -A PREROUTING -i r{}".format(router_number)+"-eth1 -j FULLCONENAT --nat-type ar")
        elif nat_type == "symmetric":
            nat_routers[lan].cmd("iptables --flush")
            nat_routers[lan].cmd("iptables -t nat -A POSTROUTING -o r{}".format(router_number)+"-eth1 -j MASQUERADE --random")
            nat_routers[lan].cmd("iptables -A FORWARD -i r{}".format(x)+"-eth1 -o r{}".format(router_number)+"-eth0 -m state --state RELATED, ESTABLISHED -j ACCEPT")
            nat_routers[lan].cmd("iptables -A FORWARD -i r{}".format(x)+"-eth0 -o r{}".format(router_number)+"-eth1 -j ACCEPT")

        x = x+1
        border_ip = border_ip+2 
        
    


    

    #____________________ - GENERAZIONE DELLA RETE FULL MESH TRA I ROUTER DI FRONTIERA - _____________________________    
    

    topologyProperties("properties2.txt") #Chiama la funzione che legge i parametri desiderati per gli archi e crea le relative strutture dati
  
    # VARIABILI AUSILIARIE
    r2_intf = 1
    r1_intf = 1
    r1_ip = 0
    r2_ip = r1_ip + 1
    for r1 in range(0, len(core_routers)):  #Prende un router R1 
            if "re{}".format(r1) not in routing_dict:
                routing_dict["re{}".format(r1)] = dict() #Se non è già presente nel dizionario del routing lo inserisce
            r2 = r1 +1 
            while r2 < len(core_routers): #Per ogni altro router R2 nella lista dei routers esterni
                #Se per questo specifico link è stata specificata una proprietà:
                if "re{}".format(r1) in properties_dict and "re{}".format(r2) in properties_dict["re{}".format(r1)]:
                    dl = int((properties_dict["re{}".format(r1)]["re{}".format(r2)][0]))/2
                    dl = str(dl)+"ms"
                    speed = int(properties_dict["re{}".format(r1)]["re{}".format(r2)][1])
                    net.addLink("re{}".format(r1), "re{}".format(r2), cls=TCLink, delay=dl, jitter='2ms', bw=speed,\
                                 intfName1='re{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='re{}'.format(r2)+'-eth{}'.format(r2_intf),\
                                      params1={'ip': "151.0.0.{}/31".format(r1_ip)}, params2={'ip': "151.0.0.{}/31".format(r2_ip)},use_htb=True)
                else:
                    
                    net.addLink("re{}".format(r1), "re{}".format(r2), cls=TCLink, delay='1ms', jitter='2ms',\
                                 intfName1='re{}'.format(r1)+'-eth{}'.format(r1_intf), intfName2='re{}'.format(r2)+'-eth{}'.format(r2_intf),\
                                      params1={'ip': "151.0.0.{}/31".format(r1_ip)}, params2={'ip': "151.0.0.{}/31".format(r2_ip)},use_htb=True)
                
                route_r1_cmd = "ip route add " + core_routers_internal_ip[r2] + " via 151.0.0.{}".format(r2_ip)
                route_r2_cmd = "ip route add " + core_routers_internal_ip[r1] + " via 151.0.0.{}".format(r1_ip)
                net.getNodeByName("re{}".format(r1)).cmd(route_r1_cmd)
                routing_dict["re{}".format(r1)]["r{}".format(r2)] = "151.0.0.{}/24".format(r2_ip)
                net.getNodeByName("re{}".format(r2)).cmd(route_r2_cmd)



                if "re{}".format(r2) not in routing_dict:
                    routing_dict["re{}".format(r2)] = dict()
                
                routing_dict["re{}".format(r2)]["re{}".format(r1)] = "151.0.0.{}/24".format(r1_ip)
                
                r2 = r2 + 1
                r1_ip = r2_ip + 1
                r2_ip = r1_ip + 1
                r1_intf = r1_intf + 1

            r1_intf = r2_intf + 1
            r2_intf = r2_intf + 1

            
        
def host_system_configuration():
     
    print("*** Configurazione del sistema *** ")
    
    #Se è la prima volta che si avvia lo script verranno installati tutti i moduli necessari
    installation_status = open("nat_module/installation", "r+") #Apre il file in modalità lettura
    
    if(installation_status.read() == "false"):
        print(installation_status.read())    
        print("*** INSTALLAZIONE COMPONENTI NECESSARI ***\n\n")
        
        os.system("cd nat_module && make && sudo insmod xt_FULLCONENAT.ko")
        shutil.copy("nat_module/libipt_FULLCONENAT.c", "iptables-1.8.7/extensions")
        os.system("cd iptables-1.8.7 && ./configure --disable-nftables && make && sudo make install")

        installation_status.close()
        with open("nat_module/installation", "w") as file:
            file.write("true")


    
    print("*** Aggiunta del modulo NAT, non preoccuparti in caso di errore (il modulo potrebbe già essere stato agguinto) ***\n\n")
    os.system("cd nat_module && sudo insmod xt_FULLCONENAT.ko")
   

    

if __name__ == '__main__':
    
    
    
    
    print("*** Preparo il tuo sistema ***\n\n")
    host_system_configuration()
    fileRead("network2.txt")
    
    net=Mininet(waitConnected=True )
    net.addController('c0')
    
    print("\n\n\n*** Sto istanziando la rete ***\n\n")
    
    network_topology_creator(net)

    print("\n\n\n*** Rete istanziata ***\n\n")
    
    
    node1 = net.getNodeByName("IoT_node1")
    
    net.start()
   
   
    cli = CLI(net, script = "overlay.sh") #Avvia lo script che permette la generazione dell'overlay network
    
    CLI(net)
    
    net.stop()

