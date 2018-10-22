#!/usr/bin/python

from mininet.net import Mininet, CLI
from mininet.examples.cluster import RemoteHost, RemoteSSHLink, RemoteGRELink, RemoteOVSSwitch
from mininet.node import RemoteController
import executionTime as et
import os

class MininetCluster( object ):
    def __init__( self, arrayNetworkLength, logFileName ):
        """Create DCell topology using SSH and GRE links"""
        for link in ( 'RemoteSSHLink', 'RemoteGRELink' ):
            line = ( link + ',' +  str(arrayNetworkLength) )
            et.wtfLineFile( line, logFileName )
            self.DCell( arrayNetworkLength, logFileName, Link=eval(link) )

    def DCell( self, arrayNetworkLength, logFileName, Link ):
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

    def FatTree( self, arrayNetworkLength ):
        """Create FatTree topology
           - arrayNetworkLength is the number of access switches in FatTree topology"""
        pass

    



def networkLength():
    """Input the number of swtiches existent in Topology:
       - DCell - cell switches
       - FatTree - access switches"""
    networkLength = False
    while not networkLength:
        try:
            networkLength = int ( raw_input ( 'Input network length: ' ) )
            if networkLength < 1:
                print ( 'Network length must be greater than 0' )
                networkLength = False
        except ValueError:
            print "Not a number"
    return ( networkLength )

def clusterNodesLength():
    """Input how many cluster nodes exists"""
    nodesLength = False
    while not nodesLength:
        try:
            nodesLength = int ( raw_input ( 'Input the number of cluster nodes: ' ) )
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
    logFileName = 'log/DCell' + str( et.executionTime() ) + '.log'
    clusterNodesLength = clusterNodesLength()
    networkLength = networkLength()
    arrayNetworkLength = networkLengthDistributed ( networkLength , clusterNodesLength ) 
    MininetCluster( arrayNetworkLength, logFileName )
