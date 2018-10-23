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
    print('\n*** Using Mininet Cluster ***\n')
    def __init__(self, Link):
        print('Creating Mininet network...\n')
        self.net = Mininet(host=RemoteHost, link=Link, switch=RemoteOVSSwitch)

    def controller(self, name, controllerType=RemoteController, controllerIP='192.168.254.1', controllerPort=6653):
        print('self.net.addController(c%s, controller=%s, ip=%s, port=%s' % (name, controllerType, controllerIP, controllerPort))
        self.net.addController('c%s' % (name), controller=controllerType, ip=controllerIP, port=controllerPort)

    def switch(self, name, clusterNode):
        if clusterNode == 0: # if node1, just create a process
            print('self.net.addSwitch(s%s)' % (name))
            self.net.addSwitch('s%s' % (name))
        else:
            print('self.net.addSwitch(s%s, server = node%s)' % (name, clusterNode))
            self.net.addSwitch('s%s' % (name), server = 'node%s' % (clusterNode))
 
    def host(self, name, switch, clusterNode):
        if clusterNode == 0: # if node1, just create a process
            print('self.net.addHost(h%s%s)' % (name, switch))
            self.net.addHost('h%s%s' % (name, switch))
        else:
            print('self.net.addHost(h%s%s, server = node%s)' % (name, switch, clusterNode))
            self.net.addHost('h%s%s' % (name, switch), server = 'node%s' % (clusterNode))

    def link(self, a, b):
        print('self.addLink(%s,%s)' % (a, b))
        self.net.addLink('%s' % (a),'%s' % (b))

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
    print('*** Using MaxiNet ***')
    def __init__(self, Link):
        print('Creating Mininet network...\n')
        self.net = Mininet(host=RemoteHost, link=Link, switch=RemoteOVSSwitch)

    def controller(self, name, controllerType=RemoteController, controllerIP='192.168.254.1', controllerPort=6653):
        print('self.net.addController(c%s, controller=%s, ip=%s, port=%s' % (name, controllerType, controllerIP, controllerPort))
        self.net.addController('c%s' % (name), controller=controllerType, ip=controllerIP, port=controllerPort)

    def switch(self, name, clusterNode):
        if clusterNode == 0: # if node1, just create a process
            print('self.net.addSwitch(s%s)' % (name))
            self.net.addSwitch('s%s' % (name))
        else:
            print('self.net.addSwitch(s%s, server = node%s)' % (name, clusterNode))
            self.net.addSwitch('s%s' % (name), server = 'node%s' % (clusterNode))

    def host(self, name, switch, clusterNode):
        if clusterNode == 0: # if node1, just create a process
            print('self.net.addHost(h%s%s)' % (name, switch))
            self.net.addHost('h%s%s' % (name, switch))
        else:
            print('self.net.addHost(h%s%s, server = node%s)' % (name, switch, clusterNode))
            self.net.addHost('h%s%s' % (name, switch), server = 'node%s' % (clusterNode))

    def link(self, a, b):
        print('self.addLink(%s,%s)' % (a, b))
        self.net.addLink('%s' % (a),'%s' % (b))

    def _start(self):
        self.net.start()

    def _stop(self):
        self.net.stop()

    def _CLI(self):
        CLI(self.net)













class TopologyLength(object):
    def __init__(self):
        self.welcome()
        self.clusterNodesLength()
        self.networkLength()
        self.fatTreeDensity()

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
        TopologyLength()
      


        switch=0
        a='h00'
        b='s0'
        name=0
        clusterNode=0
        bw=10
        delay=20
        controllerIP=None
        link='RemoteGRELink'



        #mc = MininetCluster(eval(link))
        #mc.controller(name)
        #mc.switch(name, clusterNode)
        #mc.host(name, switch, clusterNode)
        #mc.link(a, b)
              
        #mc._start()
        #mc._CLI()
        #mc._stop()



        mn = MaxiNet(eval(link))
