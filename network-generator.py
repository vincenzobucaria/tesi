
lan_list = list()
nat_types = ["full_cone", "restricted_cone", "port_restricted cone", "symmetric"]
node_list = list()
nat_dict = dict()
network_topology = dict()




def fileRead(fileName):

    network_file = open(fileName, "r")
    for line in network_file:
        line = line.strip('\n').split(' ')
        if line[1] not in lan_list:
            print("DEBUG: creo una nuova LAN")
            lan_list.append(line[1])
            network_topology[line[1]] = list()
            if line[2] not in nat_types:
                print(line[2])
                print("Errore: NAT sconosciuto")
            nat_dict[line[1]] = line[2]
            
        
        if line[0] not in node_list:
            if line[2] not in nat_dict[line[1]]:
                print("error")
            else:
                node_list.append(line[0])
                network_topology[line[1]].append(line[0])
        

fileRead("network.txt")




print(network_topology)
print(nat_dict)














