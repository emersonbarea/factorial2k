#!/usr/bin/python2

from mininet.net import Mininet, CLI
from mininet.node import RemoteController, OVSSwitch
from mininet.log import setLogLevel
from mininet.topo import Topo

from mininet.examples.cluster import RemoteHost, RemoteSSHLink, RemoteGRELink, RemoteOVSSwitch

from MaxiNet.Frontend import maxinet
from MaxiNet.tools import Tools

import os
import logging

class MininetCluster(object):
    """
        create Mininet Cluster:
        - controller
        - switches
        - hosts
        - links
    """
    def __init__(self, Link):
        print('\n*** Using Mininet Cluster ***\n')
        print('\nCreating Mininet network...\n')
        self.net = Mininet(host=RemoteHost, link=Link, switch=RemoteOVSSwitch)

    def controller(self, controllerId, controllerType=RemoteController, controllerIP='192.168.254.1', controllerPort=6653):
        controllerName = ('c%s' % (controllerId))
        print('self.net.addController(%s, controller=%s, ip=%s, port=%s' % (controllerName, controllerType, controllerIP, controllerPort))
        self.net.addController(controllerName, controller=controllerType, ip=controllerIP, port=controllerPort)

    def switch(self, switchId, clusterNodeId):
        switchName = ('s%s' % (switchId))
        clusterNodeName = ('node%s' % (clusterNodeId))
        if clusterNodeName == 'node1': # if node1, just create a process
            print('self.net.addSwitch(%s)' % (switchName))
            self.net.addSwitch(switchName)
        else:
            print('self.net.addSwitch(%s, server = %s)' % (switchName, clusterNodeName))
            self.net.addSwitch(switchName, server = clusterNodeName)
 
    def host(self, hostId, switchId, clusterNodeId):
        hostName = ('h%s_%s' % (switchId, hostId))
        clusterNodeName = ('node%s' % (clusterNodeId))
        if clusterNodeName == 'node1': # if node1, just create a process
            print('self.net.addHost(%s)' % (hostName))
            self.net.addHost(hostName)
        else:
            print('self.net.addHost(%s, server = %s)' % (hostName, clusterNodeName))
            self.net.addHost(hostName, server = clusterNodeName)

    def link(self, nodeNameA, nodeNameB):
        print('self.addLink(%s,%s)' % (nodeNameA, nodeNameB))
        self.net.addLink(nodeNameA, nodeNameB)

    def _start(self):
        self.net.start()

    def _stop(self):
        self.net.stop()

    def _CLI(self):
        CLI(self.net)


class MaxiNet(object):
    """
        create MaxiNet:
        - controller
        - switches
        - hosts
        - links
    """
    def __init__(self, clusterNodesLength):
        print('\n*** Using MaxiNet ***\n')
        print('\nCreating Mininet network...\n')
        topo = Topo()
        cluster = maxinet.Cluster(minWorkers=1, maxWorkers=clusterNodesLength)
        self.exp = maxinet.Experiment(cluster, topo, switch=OVSSwitch)
        self.exp.setup()

    def switch(self, switchId, workerId):
        switchName = ('s%s' % (switchId))
        print('self.exp.addSwitch("%s", dpid="%s", wid=%s)' % (switchName, switchId, workerId))
        self.exp.addSwitch(switchName, dpid=switchId, wid=workerId)

    def host(self, hostId, switchId):
        hostName = ('h%s_%s' % (switchId, hostId))
        switchName = ('s%s' % (switchId))
        print('self.exp.addHost("%s",ip=Tools.makeIP(%s), max=Tools.makeMAC(%s), pos="%s")' % (hostName, hostId, hostId, switchName))
        self.exp.addHost("%s" % (hostName),ip=Tools.makeIP(int(hostId)), max=Tools.makeMAC(int(hostId)), pos="%s" % (switchName))

    def link(self, nodeNameA, nodeNameB):
        print('self.exp.addLink("%s", "%s", autoconf = True)' % (nodeNameA, nodeNameB))
        self.exp.addLink(nodeNameA, nodeNameB, autoconf = True)

    def _stop(self):
        self.exp.stop()

    def _CLI(self):
        maxinet.Experiment.CLI(self.exp, None, None)


class Test(object):
    """
        basic test for Mininet and MaxiNet configuration
    """
    def __init__(self):
        self.testMininetCluster()
        self.testMaxiNet()

    def testMininetCluster(self):
        mcLink = 'RemoteSSHLink'
        clusterNodeId = 1
        controllerId = '1'
        switchId = '1'
        hostId = '1'
        nodeNameA = 's1'
        nodeNameB = 'h1_1'

        mc = MininetCluster(eval(mcLink))
        mc.controller(controllerId)
        mc.switch(switchId, clusterNodeId)
        mc.host(hostId, switchId, clusterNodeId)
        mc.link(nodeNameA, nodeNameB)

        hostId = '2'
        nodeNameB = 'h1_2'

        mc.host(hostId, switchId, clusterNodeId)
        mc.link(nodeNameA, nodeNameB)

        mc._start()
        mc._CLI()
        mc._stop()

    def testMaxiNet(self):
        workerId = 0
        controllerId = '1'
        switchId = '11999'
        hostId = '1'
        nodeNameA = 's11999'
        nodeNameB = 'h11999_1'

        mn = MaxiNet(clusterNodesLength)
        #mn.controller(controllerId)
        mn.switch(switchId, workerId)
        mn.host(hostId, switchId)
        mn.link(nodeNameA, nodeNameB)

        hostId = '2'
        nodeNameA = 's11999'
        nodeNameB = 'h11999_2'

        mn.host(hostId, switchId)
        mn.link(nodeNameA, nodeNameB)

        mn._CLI()
        mn._stop()


class TopologyLength(object):
    def __init__(self):
        self.welcome()

    def welcome(self):
        print( '\nThis program creates DCell and FatTree Topologies.\n\n \
                You need input some information:\n \
                - Number of cluster nodes\n \
                - DCell: input number of cell switches (equal the number\n \
                  of hosts in each cell switches\n \
                - FatTree: input number of POD (number of edge group switches)\n \
                  and Density (number of host on each POD)\n' )
        pass

    def clusterNodesLength(self):
        """
            Input how many cluster nodes exists
        """
        nodesLength = False
        while not nodesLength:
            try:
                nodesLength = int(raw_input('Input the number of cluster nodes : '))
                if nodesLength < 1:
                    logging.error(' Cluster must have 1 or more nodes')
                    nodesLength = False
            except ValueError:
                logging.error(' Not a number')
        return(nodesLength)

    def networkLength(self):
        """
            Input the number of swtiches existent in Topology:
            - DCell - number of cell switches
            - FatTree - number of pods
        """
        networkLength = False
        while not networkLength:
            try:
                networkLength = int(raw_input('Input network length (DCell - cell switches | FatTree - PODs) : '))
                if networkLength < 1 or networkLength % 2 != 0:
                    logging.error(' Network length must be greater than 0 and even')
                    networkLength = False
            except ValueError:
                logging.error(' Not a number')
        return(networkLength)

    def fatTreeDensity(self):
        """
            Input the number of hosts on each POD
        """
        fatTreeNetworkDensity = False
        while not fatTreeNetworkDensity:
            try:
                fatTreeNetworkDensity = int(raw_input('Input the number of hosts on each POD (FatTree Density) : '))
                if fatTreeNetworkDensity < 1:
                    plogging.error(' Network length must be greater than 0')
                    fatTreeNetworkDensity = False
            except ValueError:
                logging.error('Not a number')
        return(fatTreeNetworkDensity)

if __name__ == '__main__':
    """
        PS.: Hosts and switches can't use number 0 in its names !!!
    """
    setLogLevel('info')
    if os.getuid() != 0:
        logging.warning(' You are NOT root')
    elif os.getuid() == 0:
        """
            Topology Length (Cluster length, Network length etc)
            MininetCluster
                DCell
                FatTree
            Maxinet
                DCell
                FatTree
        """
        tp = TopologyLength()
        clusterNodesLength = tp.clusterNodesLength()
        networkLength = tp.networkLength()
        fatTreeDensity = tp.fatTreeDensity()
     
        Test()
