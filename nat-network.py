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




class custom_network(Topo):
    
    # ******************** SOTTORETE 1 ********************************+
    
    
    #La topologia circuitale è composta da un router dove si applica il NAT a cono ristretto con restrizione sulla porta, uno switch e diversi host
    #La sottorete interna usa IP privati della classe 10.0.0.x, l'interfaccia esterna avrà un indirizzo IP pubblico 5.0.1.1

    def build(self, n=2):
        switch = self.addSwitch('s1')

        x = 2

        #Istanzio gli host, assegno un ip nel formato 10.0.0.x e li collego allo switch
        for h in range(n):
            host = self.addHost('h%s' % h, ip="10.0.0.{}".format(x), defaultRoute='via 10.0.0.1')
            self.addLink(host, switch)
            x = x+1
        
        
        #Istanzio il router e lo collego allo switch
        router_internal_ip = "10.0.0.1"
        router1_external_ip = "5.0.1.1"
        r1 = self.addNode('r1', cls=LinuxRouter, ip=router_internal_ip)

        self.addLink(r1, switch, intfName1='r1-eth0', params1={'ip': router_internal_ip+"/24"})
        #Considero ottimali le condizioni di trasmissione nella LAN, si ha ovvero un delay nullo e un jitter pari a zero.


        #************************* SOTTORETE 2 *********************************
        #La topologia è identica alla sottorete 1, l'indirizzo dell'interfaccia esterna del router è 5.0.1.3
        
        
        
        
        switch2 = self.addSwitch('s2')

        x = 6
        
        #PRECISAZIONE: per non far confondere mininet, purchè in ambito reale non sia assolutamente necessario, non faccio sovrapporre gli IP delle due sottoreti private.
        
        for h in range(n):
            host = self.addHost('x%s' % h, ip="10.0.0.{}".format(x), defaultRoute='via 10.0.0.1')
            self.addLink(host, switch2)
            x = x+1


        r2 = self.addNode('r2', cls=LinuxRouter, ip=router_internal_ip)
        self.addLink(r2, switch2, intfName1='r2-eth0', params1={'ip': router_internal_ip+"/24"})
        

        
        
        #Collego i due router di frontiera per mezzo di uno switch, le interfacce di frontiera dei router utilizzeranno IP pubblici


        switch3 = self.addSwitch('s3')

        #Simulo le condizioni di una WAN reale

        self.addLink(r1, switch3, cls=TCLink, delay='10ms', jitter='2ms', intfName1='r1-eth1', params1={'ip': router1_external_ip+"/24"}, use_htb=True)
        #Il traffic control permette di simulare una WAN reale, con una larghezza di banda limitata, jitter e ritardo (impostati con valori tipici)
        self.addLink(r2, switch3, cls=TCLink, delay='15ms', jitter='2ms', intfName1='r2-eth1', params1={'ip': "5.0.1.3/24"}, use_htb=True)
        
    
    
    # ******************** RETE 3 *******************************

    # Contiene due "STUN" server, entrambi hanno IP pubblici. L'interfaccia del router ad internet è 5.0.1.2

        r3 = self.addNode('r3', cls=LinuxRouter, ip="9.0.0.1")
        switch4 = self.addSwitch('s4')
        hostServer = self.addHost('server1', ip="9.0.0.2", defaultRoute='via 9.0.0.1')
        hostServer2 = self.addHost('server2', ip='9.0.0.3', defaultRoute = 'via 9.0.0.1')
        
        self.addLink(hostServer, switch4)
        self.addLink(hostServer2, switch4)



        self.addLink(r3, switch4, intfName1='r3-eth1', params1={'ip': "9.0.0.1" + "/24"})
        self.addLink(r3, switch3, cls=TCLink, delay='4ms', jitter='2ms', intfName1='r3-eth2', params1={'ip': "5.0.1.2/24"}, use_htb=True)
        
        
        




class LinuxRouter( Node ):
    

    
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        #Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()    



def setup():

    topo = custom_network(n=4)
    net = Mininet(topo = topo, controller = OVSController)
    net.start()

    dumpNodeConnections(net.hosts)

   
    #Imposto l'ip esterno dei router e le regole di routing 
    r1 = net.get('r1')
    
    print(r1.cmd("sudo ip route add 9.0.0.0/24 via 5.0.1.2"))
    print(r1.cmd("iptables -t nat -A POSTROUTING -o r1-eth1 -j SNAT --to-source 5.0.1.1")) #NAT a cono ristretto con restrizione sulla porta


    r2 = net.get('r2')
    print(r2.cmd("sudo ip route add 9.0.0.0/24 via 5.0.1.2"))
    print(r2.cmd("iptables -t nat -A POSTROUTING -o r2-eth1 -j SNAT --to-source 5.0.1.3")) #NAT a cono ristretto con restrizione sulla porta
    r3 = net.get('r3')
   
    CLI(net)
    net.stop()

if __name__ == '__main__':
    
    info( '*** Avvio di MiniNet *** \n')
    
    setLogLevel('info')
    setup()