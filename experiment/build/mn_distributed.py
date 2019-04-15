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
import time
import paramiko

class MininetCluster(object):
    """
        create Mininet Cluster:
        - controller
        - switches
        - hosts
        - links
    """
    def __init__(self):
        print('\n*** Using Mininet Cluster ***\n')

    def topology(self, Link):
        print('\nCreating Mininet network...\n')
        self.net = Mininet(host=RemoteHost, link=eval(Link), switch=RemoteOVSSwitch)

    def controller(self, controllerName, controllerType=RemoteController, controllerIP='192.168.254.1', controllerPort=6633):
        print('self.net.addController(%s, controller=%s, ip=%s, port=%s' \
                % (controllerName, controllerType, controllerIP, controllerPort))
        self.net.addController(controllerName, controller=controllerType, ip=controllerIP, port=controllerPort)

    def controllerPox(self):
        controllerDir='/home/mininet/pox/'
        os.system('%s./pox.py smoc.samples.overseer_launcher 2> /dev/null &' % (controllerDir))

    def switch(self, switchName, clusterNodeName):
        if clusterNodeName == 'node1': # if node1, just create a process
            print('self.net.addSwitch(%s)' % (switchName))
            self.net.addSwitch(switchName)
        else:
            print('self.net.addSwitch(%s, server = %s)' % (switchName, clusterNodeName))
            self.net.addSwitch(switchName, server = clusterNodeName)
 
    def host(self, hostName, clusterNodeName):
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
        os.system('pgrep -f pox.py | sudo xargs kill 2> /dev/null')
        self.net.stop()

    def _CLI(self):
        CLI(self.net)


class MaxiNet(object):
    """
        create MaxiNet:
        - controller (PS.: controller is configured in /etc/MaxiNet.cfg)
        - switches
        - hosts
        - links
    """
    def __init__(self):
        print('\n*** Using MaxiNet ***\n')

    def workers(self, clusterNodeName):
        if clusterNodeName == 'node1': # if node1, create MaxiNetFrontendServer
            os.system('MaxiNetFrontendServer &')
            time.sleep(3)
            os.system('MaxiNetWorker &')
            time.sleep(3)
        else:
            print('paramiko connecting in: %s - client.exec_command("sudo MaxiNetWorker &")' % (clusterNodeName))
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(clusterNodeName, username='mininet', password='abc123')
            stdin, stdout, stderr = client.exec_command('sudo MaxiNetWorker &')
            client.close()
            time.sleep(3)

    def topology(self, clusterNodesLength):
        print('\nCreating Mininet network...\n')
        topo = Topo()
        cluster = maxinet.Cluster(minWorkers=1, maxWorkers=clusterNodesLength)
        self.exp = maxinet.Experiment(cluster, topo, switch=OVSSwitch)
        self.exp.setup()

    def controllerPox(self):
        controllerDir='/home/mininet/pox/'
        os.system('%s./pox.py smoc.samples.overseer_launcher 2> /dev/null &' % (controllerDir))

    def switch(self, switchName, workerId):
        print('self.exp.addSwitch("%s", wid=%s)' % (switchName, workerId))
        self.exp.addSwitch(switchName, wid=workerId)

    def host(self, hostName, workerId):
        print('self.exp.addHost("%s", wid=%s)' % (hostName, workerId))
        self.exp.addHost("%s" % (hostName), wid=workerId)

    def link(self, nodeNameA, nodeNameB):
        print('self.exp.addLink("%s", "%s", autoconf = True)' % (nodeNameA, nodeNameB))
        self.exp.addLink(nodeNameA, nodeNameB, autoconf = True)

    def _stop(self):
        os.system('pgrep -f pox.py | sudo xargs kill 2> /dev/null')
        self.exp.stop()

    def _workers(self, clusterNodeName):
        if clusterNodeName == 'node1':
            os.system('./build/killMaxiNet.sh')
        else:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(clusterNodeName, username='mininet', password='abc123')
            stdin, stdout, stderr = client.exec_command('pgrep -f MaxiNetWorker | sudo xargs kill 2> /dev/null')
            client.close()
            time.sleep(3)

    def _CLI(self):
        maxinet.Experiment.CLI(self.exp, None, None)


class Test(object):
    """
        basic test for Mininet and MaxiNet configuration
    """
    def __init__(self):
        self.testMininetCluster()
        #self.testMaxiNet()

    def testMininetCluster(self):
        mcLink = 'RemoteSSHLink'
        clusterNodeName = 'node1'
        controllerName = 'c0'

        mc = MininetCluster(eval(mcLink))
        mc.controller(controllerName)

        switchName = 's10'
        mc.switch(switchName, clusterNodeName)
        switchName = 's200'
        mc.switch(switchName, clusterNodeName)
        switchName = 's211'
        mc.switch(switchName, clusterNodeName)
        switchName = 's300'
        mc.switch(switchName, clusterNodeName)
        switchName = 's311'
        mc.switch(switchName, clusterNodeName)

        nodeNameA = 's300'
        nodeNameB = 's200'
        mc.link(nodeNameA, nodeNameB)

        nodeNameA = 's311'
        nodeNameB = 's211'
        mc.link(nodeNameA, nodeNameB)

        nodeNameA = 's200'
        nodeNameB = 's10'
        mc.link(nodeNameA, nodeNameB)

        nodeNameA = 's211'
        nodeNameB = 's10'
        mc.link(nodeNameA, nodeNameB)

        hostName = 'h00'
        mc.host(hostName, clusterNodeName)
        nodeNameA = 's300'
        nodeNameB = 'h00'
        mc.link(nodeNameA, nodeNameB)

        hostName = 'h01'
        mc.host(hostName, clusterNodeName)
        nodeNameA = 's300'
        nodeNameB = 'h01'
        mc.link(nodeNameA, nodeNameB)


        hostName = 'h11'
        mc.host(hostName, clusterNodeName)
        nodeNameA = 's311'
        nodeNameB = 'h11'
        mc.link(nodeNameA, nodeNameB)

        #clusterNodeName = 'node1'
        #for i in xrange(3,10):
        #    hostName = 'h1_' + str(i)
        #    nodeNameA = 's1'
        #    nodeNameB = 'h1_' + str(i)

        #    mc.host(hostName, clusterNodeName)
        #    mc.link(nodeNameA, nodeNameB)

        mc._start()
        mc._CLI()
        mc._stop()

    def testMaxiNet(self):
        workerId = 0 
        switchName = 's3_7_31'
        hostName = 'h_31_511'
        nodeNameA = 's3_7_31'
        nodeNameB = 'h_31_511'

        mn = MaxiNet(clusterNodesLength)
        mn.switch(switchName, workerId)
        mn.host(hostName, switchName)
        mn.link(nodeNameA, nodeNameB)

        
        #for i in xrange(3,100):
        #    hostName = 'h1_' + str(i)
        #    nodeNameA = 's1'
        #    nodeNameB = 'h1_' + str(i)

        #    mn.host(hostName, switchName)
        #    mn.link(nodeNameA, nodeNameB)

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
        Test()
