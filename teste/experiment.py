#!/usr/bin/python2

from mininet.log import setLogLevel
import mn_distributed as mnd
import os
import re

class FatTree(object):
    """
        Create FatTree Topology
        - MininetCluster
          - test
        - MaxiNet
          - test
    """
    coreSwitchList = {}                                                 # core switch name | cluster node
    aggregateSwitchList = {}                                            # aggregate switch name | cluster node
    edgeSwitchList = {}                                                 # edge switches name | cluter node
    hostList = {}                                                       # host name | cluster node
    controllerList = {}                                                 # controller name
    linksHostEdgeList = {}                                              # hostNameA | HostNameB
    linksEdgeAggregateList = {}                                         # edgeSwitchNameA | aggregateSwitchNameB
    linksAggregateCoreList = {}                                         # aggregateSwitchNameA | coreSwitchNameB

    def __init__(self, clusterNodesLength, networkLength, arrayNetworkLength):
        self.pod = networkLength                                        # Total number of PODs
        self.densityPod = (networkLength / 2) ** 2                      # Number of Hosts per POD
        self.coreSwitch = (networkLength / 2) ** 2                      # Total number of Core switches
        self.aggregateSwitch = networkLength*networkLength / 2          # Total number of Aggregate switches
        self.edgeSwitch = networkLength*networkLength / 2               # Total number of Edge switches
        self.hosts = self.densityPod * self.pod                         # Total number of Hosts
        self.edgeSwitchPerPod = self.edgeSwitch / self.pod              # Number of Edge switches per POD
        self.aggregateSwitchPerPod = self.aggregateSwitch / self.pod    # Number of Aggregate switches per POD
        self.hostsPerEdgeSwitch = self.densityPod / self.edgeSwitchPerPod   # Number of Hosts per Edge switch
        
        print('\nPODs: %s\nCore Switches: %s\nAggregate Switches: %s\nEdge Switches: %s\nHosts: %s\n' \
                % (self.pod, self.coreSwitch, self.aggregateSwitch, self.edgeSwitch, self.hosts))
        print('\nNumber of ... per POD:\nAggregate Switches: %s\nEdge Switches: %s\nHosts: %s' \
                % (self.edgeSwitchPerPod, self.aggregateSwitchPerPod, self.densityPod))

        self.createArrays()
        self.callMininetCluster()
        
    def callMininetCluster(self):
        mclink = ['RemoteSSHLink','RemoteGRELink']
        for i in mclink:
            mc = mnd.MininetCluster(i)
    
            print('\nController...')
            for i in range(len(self.controllerList)):
                mc.controller(self.controllerList[i][0])

            print('\nCore switches...')
            for i in range(len(self.coreSwitchList)):
                mc.switch(self.coreSwitchList[i][0], self.coreSwitchList[i][1])                

            print('\nAggregate switches...')
            for i in range(len(self.aggregateSwitchList)):
                mc.switch(self.aggregateSwitchList[i][0], self.aggregateSwitchList[i][1])

            print('\nEdge switches...')
            for i in range(len(self.edgeSwitchList)):
                mc.switch(self.edgeSwitchList[i][0], self.edgeSwitchList[i][1])

            print('\nHost list...')
            for i in range(len(self.hostList)):
                mc.host(self.hostList[i][0], self.hostList[i][1])

            print('\nlink: Host <-> Edge...')
            for i in range(len(self.linksHostEdgeList)):
                mc.link(self.linksHostEdgeList[i][0], self.linksHostEdgeList[i][1])

            print('\nlink: Edge <-> Aggregate...')
            for i in range(len(self.linksEdgeAggregateList)):
                mc.link(self.linksEdgeAggregateList[i][0], self.linksEdgeAggregateList[i][1])
        
            print('\nlink: Aggregate <-> Core...')
            for i in range(len(self.linksAggregateCoreList)):
                mc.link(self.linksAggregateCoreList[i][0], self.linksAggregateCoreList[i][1])

            #mc._start()
            mc._CLI()
            mc._stop()

    def createArrays(self):
        """
            Host name = 'h' + <edgeSwitchId> + <hostId>
            Edge switches name = 's3' + <podId> + <edgeSwitchId>
            Aggregate switches name = 's2' + <podId> + <aggregateSwitchId>
            Core switches name = 's1' + <coreSwitchId>
            Controller name = 'c0'
        """
        """ 
            Core switches
        """
        arrayCoreLength = [self.coreSwitch / clusterNodesLength] * clusterNodesLength
        restCoreLength = self.coreSwitch % clusterNodesLength
        for i in range(restCoreLength):
            arrayCoreLength[i] = arrayCoreLength[i] + 1                 # Number of core switches per cluster node

        count = 0
        for i in range(len(arrayNetworkLength)):                        # Take nodeId
            for j in range(arrayCoreLength[i]):                         # how many times repeat on each node
                self.coreSwitchList[count] = ['s1' + str(count), 'node' + str(i + 1)]
                count += 1
        """
            Aggregate switches, Edge switches  and Host
        """
        countSw = 0
        countHt = 0
        countPod = 0
        for i in range(len(arrayNetworkLength)):                        # Take nodeId
            for j in range(arrayNetworkLength[i]):                      # how many times repeat on each node
                for x in range(self.aggregateSwitchPerPod):             # how many times repeat on each POD (for switches)
                    self.aggregateSwitchList[countSw] = ['s2' + str(countPod) + str(countSw), 'node' + str(i + 1)]
                    self.edgeSwitchList[countSw] = ['s3' + str(countPod) + str(countSw), 'node' + str(i + 1), countSw]
                    for y in range(self.hostsPerEdgeSwitch):            # how many times repeat on each Switch (for hosts)
                        self.hostList[countHt] = ['h' + str(countSw) + str(countHt), 'node' + str(i + 1), countSw]
                        countHt += 1
                    countSw += 1
                countPod += 1
        """
            Controller
        """
        self.controllerList[0] = ['c0']

        """
            Links
        """
        """
            Host <-> Edge Switches
        """
        for i in range(len(self.hostList)):
            for y in range(len(self.edgeSwitchList)):
                if self.hostList[i][2] == self.edgeSwitchList[y][2]:
                    self.linksHostEdgeList[i] = [self.hostList[i][0], self.edgeSwitchList[y][0]]
        """
            Edge <-> Aggregate
        """
        podRangeNumber = 0
        countLink = 0
        for i in range(len(self.edgeSwitchList)):
            if i >= (podRangeNumber + self.edgeSwitchPerPod):
                podRangeNumber = podRangeNumber + self.edgeSwitchPerPod
            for y in range(self.edgeSwitchPerPod):
                self.linksEdgeAggregateList[countLink] = [self.edgeSwitchList[i][0], 's2' + \
                        str(self.edgeSwitchList[i][0][2:-len(str(self.edgeSwitchList[i][2]))]) + str(podRangeNumber + y)]
                countLink += 1
        """
            Aggregate <--> Core
        """
        forBegin = 0
        forEnd = self.pod / 2
        countLink = 0
        for i in range(len(self.aggregateSwitchList)):
            for y in xrange(forBegin, forEnd):
                self.linksAggregateCoreList[countLink] = [self.aggregateSwitchList[i][0], 's1' + str(y)]
                countLink += 1
            if forEnd == self.coreSwitch:
                forBegin = 0
                forEnd = self.pod / 2
            else:
                forBegin = forEnd
                forEnd = forEnd + (self.pod / 2)

        """
        print('\nCore switches...')
        for i in range(len(self.coreSwitchList)):
            print(self.coreSwitchList[i])

        print('\nAggregate switches...')
        for i in range(len(self.aggregateSwitchList)):
            print(self.aggregateSwitchList[i])

        print('\nEdge switches...')
        for i in range(len(self.edgeSwitchList)):
            print(self.edgeSwitchList[i])

        print('\nHost list...')
        for i in range(len(self.hostList)):
            print(self.hostList[i])

        print('\nlink: Host <-> Edge...')
        for i in range(len(self.linksHostEdgeList)):
            print(self.linksHostEdgeList[i])

        print('\nlink: Edge <-> Aggregate...')
        for i in range(len(self.linksEdgeAggregateList)):
            print(self.linksEdgeAggregateList[i])
        
        print('\nlink: Aggregate <-> Core...')
        for i in range(len(self.linksAggregateCoreList)):
            print(self.linksAggregateCoreList[i])
        """

def arrayNetworkLength(networkLength, clusterNodesLength):
    """
        Define how many cell switches (DCell) and PODs (FatTree) wil be created on each cluster node or worker
    """
    arrayNetworkLength = [networkLength / clusterNodesLength] * clusterNodesLength
    restNetworkLength = networkLength % clusterNodesLength
    for i in range(restNetworkLength):
        arrayNetworkLength[i] = arrayNetworkLength[i] + 1
    return(arrayNetworkLength)

if __name__ == '__main__':
    """
        Verify if root
        Welcome message
        set cluster node length
        set network length (cell switch number (DCell) and POD number (FatTree))
        fatTree density (number of PODs hosts)
    """
    setLogLevel('info')
    if os.getuid() != 0:
        logging.warning(' You are NOT root')
    elif os.getuid() == 0:
        tp = mnd.TopologyLength()
        clusterNodesLength = tp.clusterNodesLength()                    # clusterNodesLength = number of cluster nodes
        networkLength = tp.networkLength()                              # networkLength = number of cell switches (DCell)
                                                                        # and PODs (FatTree)
        arrayNetworkLength = arrayNetworkLength(networkLength, clusterNodesLength) 
                                                                        # arrayNetworkLength = array (clusterNodesLength \
                                                                        # length) where each index contains the number of \
                                                                        # cell switches (DCell) or PODs (FatTree) that will \
                                                                        # be created in each cluster node or worker 
        print('\nArray cluster node Length: %s' % (arrayNetworkLength))
        FatTree(clusterNodesLength, networkLength, arrayNetworkLength)
