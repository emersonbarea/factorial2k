#!/usr/bin/python

from mininet.net import Mininet, CLI
from mininet.examples.cluster import RemoteHost, RemoteSSHLink, RemoteGRELink, RemoteOVSSwitch
from mininet.node import RemoteController
import executionTime as et
import os

class DCell( object ):

    def __init__( self, arrayNetworkLength, logFileName, Link ):
        """Create DCell topology
           - arrayNetworkLength: is the number of cell switches in DCell topology
           - link: is a link type (RemoteSSHLink and RemoteGRELink) """
        print( '\n*** DCell ***\n' )
        print( '-- using %s' % ( Link ) )
        print( '-- Initializing Ryu...\n' )
        os.system( 'ryu-manager /usr/local/lib/python2.7/dist-packages/ryu/app/simple_switch.py > /dev/null 2>&1 &' )
        t1 = et.executionTime()
        print( '--- Creating Mininet Topology...\n' )
        net = Mininet( host=RemoteHost, link=Link, switch=RemoteOVSSwitch ) 


        ryuController = net.addController(name='ryuController', controller=RemoteController, ip='192.168.254.1', port=6633)



        t2 = et.executionTime() 
        et.wtfExecutionTime( t1, t2, 'local', 'Create Mininet Topology', logFileName )

        print( '---- Creating cell switches... \n' )
        switchNumber = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            for y in range(arrayNetworkLength[i]): # y = number of switches on each cluster node
                t1 = et.executionTime()
                if i == 0: # if node1, just create a process
                    local = True
                    print('net.addSwitch( s%s )' % (switchNumber))
                    net.addSwitch( 's%s' % (switchNumber)) 
                else: # else create a process in a correspond cluster node
                    local = False
                    print('net.addSwitch( s%s , server = node%s)' % (switchNumber, i + 1 ))
                    net.addSwitch( 's%s' % (switchNumber), server = 'node%s' % ( i + 1 ) )
                switchNumber += 1
            t2 = et.executionTime()
            if local:
                et.wtfExecutionTime( t1, t2, 'local', 'Create local cell switches', logFileName )
            else:
                et.wtfExecutionTime( t1, t2, 'remote', 'Create remote cell switches', logFileName )

        print( '---- Creating hosts... \n' )
        totalSwitches = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            totalSwitches = totalSwitches + arrayNetworkLength[i]
        switchNumber = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            for y in range(arrayNetworkLength[i]): # y = number of switches on each cluster node
                hostNumber = 0
                t1 = et.executionTime()
                for z in range(totalSwitches - 1):
                    if i == 0: # if node1, just create a process
                        local = True
                        print('cluster node %s - switch s%s - host h%s-%s' % ( i + 1, switchNumber, switchNumber, hostNumber ))
                        net.addHost( 'h%s-%s' % ( switchNumber, hostNumber ))
                        hostNumber += 1
                    else: # else create a process in a correspond cluster node
                        local = False
                        print('cluster node %s - switch s%s - host h%s-%s' % ( i + 1, switchNumber, switchNumber, hostNumber ))
                        net.addHost( 'h%s-%s' % ( switchNumber, hostNumber ), server = 'node%s' % ( i + 1 ))
                        hostNumber += 1
                switchNumber += 1
            t2 = et.executionTime()
            if local:
                et.wtfExecutionTime( t1, t2, 'local', 'Create local hosts', logFileName )
            else:
                et.wtfExecutionTime( t1, t2, 'remote', 'Create remote hosts', logFileName )

        print( '---- Linking hosts to cell switches...\n' )
        totalSwitches = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            totalSwitches = totalSwitches + arrayNetworkLength[i]

        switchNumber = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            for y in range(arrayNetworkLength[i]): # y = number of switches on each cluster node
                hostNumber = 0
                t1 = et.executionTime()
                if i == 0:
                    local = True
                else:
                    local = False
                for z in range(totalSwitches - 1):
                    print( 'net.addLink(h%s-%s, s%s)' % ( switchNumber, hostNumber, switchNumber ))
                    net.addLink( 'h%s-%s' % ( switchNumber, hostNumber ), 's%s' % ( switchNumber ))
                    hostNumber += 1
                switchNumber += 1
            t2 = et.executionTime()
            if local:
                et.wtfExecutionTime( t1, t2, 'local', 'Link hosts to cell switches', logFileName )
            else:
                et.wtfExecutionTime( t1, t2, 'remote', 'Link hosts to cell switches', logFileName )

        print( '---- Linking host to host...\n' )
        totalSwitches = 0
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            totalSwitches = totalSwitches + arrayNetworkLength[i]
        switchNumber = 0
        t1 = et.executionTime()
        for i in range(len(arrayNetworkLength)): # i = number of cluster nodes
            for y in range(arrayNetworkLength[i]): # y = number of switches on each cluster node
                hostNumber = 0
                for z in range(totalSwitches - 1):
                    if y <= hostNumber:
                        print( 'net.addLink(h%s-%s, h%s-%s)' % ( y, hostNumber, hostNumber + 1, y ))
                        net.addLink( 'h%s-%s' % ( y, hostNumber ), 'h%s-%s' % ( hostNumber + 1, y ))
                    hostNumber += 1
                switchNumber += 1
        t2 = et.executionTime()
        et.wtfExecutionTime( t1, t2, 'local_remote', 'Link host to host', logFileName )


        net.start()
        CLI(net)
        net.stop()
        os.system( 'pkill -9 ryu-manager' )

class FatTree( object ):
    """
        Class of Fattree Topology.
    """
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []

    def __init__(self, cluserNodesLength, k, density, logFileName):
        self.pod = k
	self.density = density
	self.iCoreLayerSwitch = (k/2)**2
	self.iAggLayerSwitch = k*k/2
	self.iEdgeLayerSwitch = k*k/2
	self.iHost = self.iEdgeLayerSwitch * density

    def createNodes(self):
	self.createCoreLayerSwitch(self.iCoreLayerSwitch)
	self.createAggLayerSwitch(self.iAggLayerSwitch)
	self.createEdgeLayerSwitch(self.iEdgeLayerSwitch)
	self.createHost(self.iHost)

    # Create Switch and Host
    def _addSwitch(self, number, level, switch_list):
        """
	    Create switches.
        """
        for i in xrange(1, number+1):
	    PREFIX = str(level) + "00"
	    if i >= 10:
		PREFIX = str(level) + "0"
	    switch_list.append(self.addSwitch(PREFIX + str(i)))

    def createCoreLayerSwitch(self, NUMBER):
	self._addSwitch(NUMBER, 1, self.CoreSwitchList)

    def createAggLayerSwitch(self, NUMBER):
	self._addSwitch(NUMBER, 2, self.AggSwitchList)

    def createEdgeLayerSwitch(self, NUMBER):
	self._addSwitch(NUMBER, 3, self.EdgeSwitchList)

    def createHost(self, NUMBER):
	"""
	    Create hosts.
	"""
	for i in xrange(1, NUMBER+1):
            if i >= 100:
                PREFIX = "h"
            elif i >= 10:
		PREFIX = "h0"
	    else:
		PREFIX = "h00"
	    self.HostList.append(self.addHost(PREFIX + str(i), cpu=1.0/NUMBER))

    def createLinks(self, bw_c2a=10, bw_a2e=10, bw_e2h=10):
	"""
	    Add network links.
	"""
	# Core to Agg
	end = self.pod/2
	for x in xrange(0, self.iAggLayerSwitch, end):
	    for i in xrange(0, end):
		for j in xrange(0, end):
		    self.addLink(
			self.CoreSwitchList[i*end+j],
			self.AggSwitchList[x+i],
			bw=bw_c2a, max_queue_size=1000)   # use_htb=False

	# Agg to Edge
	for x in xrange(0, self.iAggLayerSwitch, end):
	    for i in xrange(0, end):
		for j in xrange(0, end):
		    self.addLink(
			self.AggSwitchList[x+i], self.EdgeSwitchList[x+j],
			bw=bw_a2e, max_queue_size=1000)   # use_htb=False

	# Edge to Host
	for x in xrange(0, self.iEdgeLayerSwitch):
            for i in xrange(0, self.density):
		self.addLink(
		    self.EdgeSwitchList[x],
		    self.HostList[self.density * x + i],
		    bw=bw_e2h, max_queue_size=1000)   # use_htb=False

    def set_ovs_protocol_13(self,):
	"""
	    Set the OpenFlow version for switches.
	"""
	self._set_ovs_protocol_13(self.CoreSwitchList)
	self._set_ovs_protocol_13(self.AggSwitchList)
	self._set_ovs_protocol_13(self.EdgeSwitchList)

    def _set_ovs_protocol_13(self, sw_list):
	for sw in sw_list:
	    cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % sw
	    os.system(cmd)


    def set_host_ip(net, topo):
	hostlist = []
	for k in xrange(len(topo.HostList)):
	    hostlist.append(net.get(topo.HostList[k]))
	i = 1
	j = 1
	for host in hostlist:
	    host.setIP("10.%d.0.%d" % (i, j))
	    j += 1
	    if j == topo.density+1:
		j = 1
		i += 1

    def create_subnetList(topo, num):
	"""
		Create the subnet list of the certain Pod.
	"""
	subnetList = []
	remainder = num % (topo.pod/2)
	if topo.pod == 4:
	    if remainder == 0:
		subnetList = [num-1, num]
	    elif remainder == 1:
		subnetList = [num, num+1]
	    else:
		pass
	elif topo.pod == 8:
	    if remainder == 0:
		subnetList = [num-3, num-2, num-1, num]
	    elif remainder == 1:
		subnetList = [num, num+1, num+2, num+3]
	    elif remainder == 2:
		subnetList = [num-1, num, num+1, num+2]
	    elif remainder == 3:
		subnetList = [num-2, num-1, num, num+1]
	    else:
		pass
	else:
	    pass
	return subnetList

    def createTopo(pod, density, ip="192.168.254.1", port=6653, bw_c2a=10, bw_a2e=10, bw_e2h=10):
	"""
		Create network topology and run the Mininet.
	"""
	# Create Topo.
	topo = Fattree(pod, density)
	topo.createNodes()
	topo.createLinks(bw_c2a=bw_c2a, bw_a2e=bw_a2e, bw_e2h=bw_e2h)

	# Start Mininet.
	CONTROLLER_IP = ip
	CONTROLLER_PORT = port
	net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True)
	net.addController(
		'controller', controller=RemoteController,
		ip=CONTROLLER_IP, port=CONTROLLER_PORT)
	net.start()

	# Set OVS's protocol as OF13.
	topo.set_ovs_protocol_13()
	# Set hosts IP addresses.
	set_host_ip(net, topo)

	CLI(net)
	net.stop()



























    
def welcome():
    print( 'This program creates DCell and FatTree Topologies.\n\n \
            You need input some information:\n \
            - Number of cluster nodes\n \
            - DCell: input number of cell switches (equal the number\n \
              of hosts in each cell switches\n \
            - FatTree: input number of POD (number of edge group switches)\n \
              and Density (number of host on each POD)\n' )
    pass

def fatTreeNetworkDensity():
    """Input the number of hosts on each POD"""
    fatTreeNetworkDensity = False
    while not fatTreeNetworkDensity:
        try:
            fatTreeNetworkDensity = int ( raw_input ( 'Input the number of hosts on each POD (FatTree Density) : ' ) )
            if fatTreeNetworkDensity < 1:
                print ( 'Network length must be greater than 0' )
                fatTreeNetworkDensity = False
        except ValueError:
            print "Not a number"
    return ( fatTreeNetworkDensity )

def networkLength():
    """Input the number of swtiches existent in Topology:
       - DCell - number of cell switches
       - FatTree - number of pods"""
    networkLength = False
    while not networkLength:
        try:
            networkLength = int ( raw_input ( 'Input network length (DCell - cell switches | FatTree - PODs) : ' ) )
            if networkLength < 1 or networkLength % 2 != 0:
                print ( 'Network length must be greater than 0 and even' )
                networkLength = False
        except ValueError:
            print "Not a number"
    return ( networkLength )

def clusterNodesLength():
    """Input how many cluster nodes exists"""
    nodesLength = False
    while not nodesLength:
        try:
            nodesLength = int ( raw_input ( 'Input the number of cluster nodes : ' ) )
            if nodesLength < 1:
                print ( 'The cluster must have 1 or more nodes' )
                nodesLength = False
        except ValueError:
            print "Not a number"
    return ( nodesLength )

def networkLengthDistributed ( networkLength , nodesLength ):
    """Define how many Mininet DCell Switches will be created on each cluster node"""
    arrayNetworkLength = [ networkLength / nodesLength ] * nodesLength
    restNetworkLength = networkLength % nodesLength
    for i in range ( restNetworkLength ):
        arrayNetworkLength[i] = arrayNetworkLength[i]+1
    return ( arrayNetworkLength )

if __name__ == '__main__':
    welcome()
    logFileName = 'log/DCell' + str( et.executionTime() ) + '.log'
    clusterNodesLength = clusterNodesLength()
    networkLength = networkLength()
    fatTreeNetworkDensity = fatTreeNetworkDensity()
    
    FatTree( clusterNodesLength, networkLength, fatTreeNetworkDensity, logFileName )

#def mininetCluster( arrayNetworkLength, logFileName ):
#    """Create DCell topology using SSH and GRE links"""
#    for link in ( 'RemoteSSHLink', 'RemoteGRELink' ):
#        line = ( link + ',' +  str(arrayNetworkLength) )
#        et.wtfLineFile( line, logFileName )
#        DCell( arrayNetworkLength, logFileName, Link=eval(link) )







#    arrayNetworkLength = networkLengthDistributed ( networkLength , clusterNodesLength ) 
#    mininetCluster( arrayNetworkLength, logFileName )



