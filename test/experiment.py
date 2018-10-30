#!/usr/bin/python2

from mininet.log import setLogLevel
import mn_distributed as mnd
import writeToFile as wf
import os
import re
import psutil
import time
import paramiko

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
        self.sleepTime = 0
        self.sleepTimeMem = 0
        self.createArrays()
        self.callMininetCluster()
    
    def getMemLocal(self, Sleep):
        time.sleep(Sleep)
        memory = psutil.virtual_memory()[4]
        return(memory)

    def getMemRemote(self, Sleep, node):
        time.sleep(Sleep)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(node, username='mininet', password='abc123')
        stdin, stdout, stderr = client.exec_command('echo -e "import psutil\nprint(psutil.virtual_memory()[4])" | python')
        for line in stdout:
	    rMem  = line.strip('\n')
        return(int(rMem))

    def getTime(self, Sleep):
        time.sleep(Sleep)
        Time = time.time() - Sleep
        return(Time)

    def callMininetCluster(self):
        timeStamp = self.getTime(0)
        logFile = './log/experiment_' + str(timeStamp) + '.log'
        mclink = ['RemoteSSHLink','RemoteGRELink']
        wf.line('- MininetCluster\n\
        -- cluster_nodes:%s\n\
        -- array_cluster_nodes:%s\n\
        -- total_pod:%s\n\
        -- total_switch_core:%s\n\
        -- total_switch_aggregate:%s\n\
        -- total_switch_edge:%s\n\
        -- total_host:%s\n\
        -- switch_core_per_cluster_node:%s\n\
        -- switch_aggregate_per_pod:%s\n\
        -- switch_edge_per_pod:%s\n\
        -- host_per_pod:%s\n\
        \nLine structure:\n\
        - time: time spent on task execution (seconds)\n\
        - local memory: number of memory used to execute the task on local cluster node (bytes)\n\
        - remote memory: number of memory used to execute the task on remote cluster node (bytes)\n\
        - local processes: number of persistent processes created to execute the task on local cluster node\n\
        - remote processes: number of persistent processes created to execute the task on remote cluster node\n\
        - cluster node: the name of the cluster node on which the task is running\n\
        - amount: amount of elements created (hosts, switches, links) on the task\n\
        - description: a description that describe the what the task does\n'
        % (clusterNodesLength, arrayNetworkLength, self.pod, self.coreSwitch, self.aggregateSwitch, self.edgeSwitch, \
        self.hosts, self.coreSwitchList, self.aggregateSwitchPerPod, self.edgeSwitchPerPod, self.densityPod), logFile)
        for Link in mclink:
            wf.line('-- %s' % (Link), logFile)
            """
                Initiating Mininet Cluster Topology and Ryu Controller
            """
            print('Initiating Mininet Cluster Topology and Ryu Controller...')
            lMem = self.getMemLocal(self.sleepTimeMem)
            pTime = self.getTime(self.sleepTime)
            mc = mnd.MininetCluster(Link, timeStamp)
            pTime = self.getTime(self.sleepTime) - pTime
            lMem = lMem - self.getMemLocal(self.sleepTimeMem)
            wf.string(pTime, lMem, 0, 0, 0, 'node1', 0, 'topology', logFile) 
            """
                Creating Controller
                self.controllerList[i][0] = controller name
            """
            print('\nController...')
            lMem = self.getMemLocal(self.sleepTimeMem)
            pTime = self.getTime(self.sleepTime)
            for i in range(len(self.controllerList)):
                mc.controller(self.controllerList[i][0])
            pTime = self.getTime(self.sleepTime) - pTime
            lMem = lMem - self.getMemLocal(self.sleepTimeMem)
            wf.string(pTime, lMem, 0, 1, 0, 'node1', 0, 'controller', logFile)
            """
                Creating Core switches
                self.coreSwitchList[i][0] = Core switch name (ex.: s10)
                self.coreSwitchList[i][1] = node name (ex.: node1)
            """
            print('\nCore switches...')
            coreSwitchClusterNode = []
            for i in range(len(self.coreSwitchList)):
                exist = False
                for y in range(len(coreSwitchClusterNode)):
                    if self.coreSwitchList[i][1] == coreSwitchClusterNode[y]:
                        exist = True
                if not exist:
                    coreSwitchClusterNode.append(self.coreSwitchList[i][1])
            for i in range(len(coreSwitchClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, coreSwitchClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.coreSwitchList)):
                    if coreSwitchClusterNode[i] == self.coreSwitchList[y][1]:
                        if coreSwitchClusterNode[i] == 'node1':
                            amount += 1
                            lProc += 1
                            rProc = 0
                            rMem = 0
                        else:
                            amount += 1
                            lProc += 2
                            rProc += 4
                            clusterNodeRemote = True
                        mc.switch(self.coreSwitchList[y][0], self.coreSwitchList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, coreSwitchClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, coreSwitchClusterNode[i], amount, 'coreSwitch', logFile)
            """
                Creating Aggregate switches
                self.aggregateSwitchList[i][0] = Aggregate switch name (ex.: s200)
                self.aggregateSwitchList[i][1] = node name (ex.: node1)
            """
            print('\nAggregate switches...')
            aggregateSwitchClusterNode = []
            for i in range(len(self.aggregateSwitchList)):
                exist = False
                for y in range(len(aggregateSwitchClusterNode)):
                    if self.aggregateSwitchList[i][1] == aggregateSwitchClusterNode[y]:
                        exist = True
                if not exist:
                    aggregateSwitchClusterNode.append(self.aggregateSwitchList[i][1])
            for i in range(len(aggregateSwitchClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, aggregateSwitchClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.aggregateSwitchList)):
                    if aggregateSwitchClusterNode[i] == self.aggregateSwitchList[y][1]:
                        if aggregateSwitchClusterNode[i] == 'node1':
                            amount += 1
                            lProc += 1
                            rProc = 0
                            rMem = 0
                        else:
                            amount += 1
                            lProc += 2
                            rProc += 4
                            clusterNodeRemote = True
                        mc.switch(self.aggregateSwitchList[y][0], self.aggregateSwitchList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, aggregateSwitchClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, aggregateSwitchClusterNode[i], amount, 'aggregateSwitch', logFile)
            """
                Creating Edge switches
                self.edgeSwitchList[i][0] = Edge switch name (ex.: s300)
                self.edgeSwitchList[i][1] = node name (ex.: node1)
            """
            print('\nEdge switches...')
            edgeSwitchClusterNode = []
            for i in range(len(self.edgeSwitchList)):
                exist = False
                for y in range(len(edgeSwitchClusterNode)):
                    if self.edgeSwitchList[i][1] == edgeSwitchClusterNode[y]:
                        exist = True
                if not exist:
                    edgeSwitchClusterNode.append(self.edgeSwitchList[i][1])
            for i in range(len(edgeSwitchClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, edgeSwitchClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.edgeSwitchList)):
                    if edgeSwitchClusterNode[i] == self.edgeSwitchList[y][1]:
                        if edgeSwitchClusterNode[i] == 'node1':
                            amount += 1
                            lProc += 1
                            rProc = 0
                            rMem = 0
                        else:
                            amount += 1
                            lProc += 2
                            rProc += 4
                            clusterNodeRemote = True
                        mc.switch(self.edgeSwitchList[y][0], self.edgeSwitchList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, edgeSwitchClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, edgeSwitchClusterNode[i], amount, 'edgeSwitch', logFile)
            """ 
                Creating Hosts
                self.hostList[i][0] = Host name (ex.: h00)
                self.hostList[i][1] = node name (ex.: node1)
            """
            print('\nHost list...')
            hostClusterNode = []
            for i in range(len(self.hostList)):
                exist = False
                for y in range(len(hostClusterNode)):
                    if self.hostList[i][1] == hostClusterNode[y]:
                        exist = True
                if not exist:
                    hostClusterNode.append(self.hostList[i][1])
            for i in range(len(hostClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, hostClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.hostList)):
                    if hostClusterNode[i] == self.hostList[y][1]:
                        if hostClusterNode[i] == 'node1':
                            amount += 1
                            lProc += 1
                            rProc = 0
                            rMem = 0
                        else:
                            amount += 1
                            lProc += 2
                            rProc += 4
                            clusterNodeRemote = True
                        mc.host(self.hostList[y][0], self.hostList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, hostClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, hostClusterNode[i], amount, 'host', logFile)
            """ 
                Link between Hosts and Edge switches
                self.linksHostEdgeList[i][0] = Host name (ex.: h00)
                self.linksHostEdgeList[i][1] = Edge switch name (ex.: s300)
            """
            print('\nlink: Host <-> Edge...')
            linksHostEdgeClusterNode = []
            for i in range(len(self.linksHostEdgeList)):
                exist = False
                for y in range(len(linksHostEdgeClusterNode)):
                    if self.linksHostEdgeList[i][2] == linksHostEdgeClusterNode[y]:
                        exist = True
                if not exist:
                    linksHostEdgeClusterNode.append(self.linksHostEdgeList[i][2]) 
            for i in range(len(linksHostEdgeClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, linksHostEdgeClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.linksHostEdgeList)):
                    if linksHostEdgeClusterNode[i] == self.linksHostEdgeList[y][2]:
                        if linksHostEdgeClusterNode[i] == 'node1':
                            amount += 1
                            rMem = 0
                        else:
                            lMem = 0
                            amount += 1
                            clusterNodeRemote = True
                        mc.link(self.linksHostEdgeList[y][0], self.linksHostEdgeList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                if not clusterNodeRemote:
                    lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, linksHostEdgeClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, linksHostEdgeClusterNode[i], amount, 'linkHostEdge', logFile)
            """ 
                Link between Edge and Aggregate switches
                self.linksEdgeAggregateList[i][0] = Edge switch name (ex.: s300)
                self.linksEdgeAggregateList[i][1] = Aggregate switch name (ex.: s200)
            """
            print('\nlink: Edge <-> Aggregate...')
            linksEdgeAggregateClusterNode = []
            for i in range(len(self.linksEdgeAggregateList)):
                exist = False
                for y in range(len(linksEdgeAggregateClusterNode)):
                    if self.linksEdgeAggregateList[i][2] == linksEdgeAggregateClusterNode[y]:
                        exist = True
                if not exist:
                    linksEdgeAggregateClusterNode.append(self.linksEdgeAggregateList[i][2])
            for i in range(len(linksEdgeAggregateClusterNode)):
                lMem = self.getMemLocal(self.sleepTimeMem)
                rMem = self.getMemRemote(self.sleepTimeMem, linksEdgeAggregateClusterNode[i])
                pTime = self.getTime(self.sleepTime)
                amount = 0
                lProc = 0
                rProc = 0
                clusterNodeRemote = False
                for y in range(len(self.linksEdgeAggregateList)):
                    if linksEdgeAggregateClusterNode[i] == self.linksEdgeAggregateList[y][2]:
                        if linksEdgeAggregateClusterNode[i] == 'node1':
                            amount += 1
                            rMem = 0
                        else:
                            lMem = 0
                            amount += 1
                            clusterNodeRemote = True
                        mc.link(self.linksEdgeAggregateList[y][0], self.linksEdgeAggregateList[y][1])
                pTime = self.getTime(self.sleepTime) - pTime
                if not clusterNodeRemote:
                    lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                if clusterNodeRemote:
                    rMem = rMem - self.getMemRemote(self.sleepTimeMem, linksEdgeAggregateClusterNode[i])
                wf.string(pTime, lMem, rMem, lProc, rProc, linksEdgeAggregateClusterNode[i], amount, 'linkEdgeAggregate', logFile)
            """ 
                Link between Aggregate and Core switches
                self.linksAggregateCoreList[i][0] = Aggregate switch name (ex.: s200)
                self.linksAggregateCoreList[i][1] = Core switch name (ex.: s10)
            """
            print('\nlink: Aggregate <-> Core...')
            linksAggregateCoreClusterNodeSrc = []
            linksAggregateCoreClusterNodeDst = []
            for i in range(len(self.linksAggregateCoreList)):
                exist = False
                for y in range(len(linksAggregateCoreClusterNodeSrc)):
                    if self.linksAggregateCoreList[i][2] == linksAggregateCoreClusterNodeSrc[y]:
                        exist = True
                if not exist:
                    linksAggregateCoreClusterNodeSrc.append(self.linksAggregateCoreList[i][2])
            for i in range(len(self.linksAggregateCoreList)):
                exist = False
                for y in range(len(linksAggregateCoreClusterNodeDst)):
                    if self.linksAggregateCoreList[i][3] == linksAggregateCoreClusterNodeDst[y]:
                        exist = True
                if not exist:
                    linksAggregateCoreClusterNodeDst.append(self.linksAggregateCoreList[i][3])
            
            for i in range(len(linksAggregateCoreClusterNodeSrc)):
                for y in range(len(linksAggregateCoreClusterNodeDst)):
                    lMem = 0
                    rMem1 = 0
                    rMem2 = 0
                    lProc = 0
                    rProc1 = 0
                    rProc2 = 0
                    cNode2 = 0
                    amount = 0
                    local_local = False
                    local_remote = False
                    remote_local = False
                    remoteX_remoteX = False
                    remoteX_remoteY = False
                    """
                        local - local: (node1 - node1)
                        - local veth
                        - 0 local process - 0 remote process
                    """
                    lMem = self.getMemLocal(self.sleepTimeMem)
                    pTime = self.getTime(self.sleepTime)
                    for x in range(len(self.linksAggregateCoreList)):
                        if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                                self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                                linksAggregateCoreClusterNodeSrc[i] == 'node1' and linksAggregateCoreClusterNodeDst[y] == 'node1':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                            amount += 1
                            local_local = True
                    if local_local:
                        pTime = self.getTime(self.sleepTime) - pTime
                        lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                        wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                                linksAggregateCoreClusterNodeSrc[i], 0, amount, 'linkAggregateCore-local-local', logFile)
                        continue
                    """
                        local - remote (node1 - nodeX)
                        - SSH tunnel
                        - 2 local process - 2 remote process
                    """
                    lMem = self.getMemLocal(self.sleepTimeMem)
                    rMem1 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    pTime = self.getTime(self.sleepTime)
                    for x in range(len(self.linksAggregateCoreList)):
                        if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                                self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                                linksAggregateCoreClusterNodeSrc[i] == 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                            amount += 1
                            local_remote = True
                    if local_remote:
                        pTime = self.getTime(self.sleepTime) - pTime
                        lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                        rMem1 = rMem1 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                        lProc = 2 * amount
                        rProc1 = 2 * amount
                        wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                                linksAggregateCoreClusterNodeSrc[i], 0, amount, 'linkAggregateCore-local-remote', logFile)
                        continue
                    """
                        remote - local (nodeX - node1)
                        - SSH tunnel
                        - 2 local process - 2 remote process
                    """
                    lMem = self.getMemLocal(self.sleepTimeMem)
                    rMem1 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    pTime = self.getTime(self.sleepTime)
                    for x in range(len(self.linksAggregateCoreList)):
                        if self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                                self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                                linksAggregateCoreClusterNodeDst[y] == 'node1' and linksAggregateCoreClusterNodeSrc[i] != 'node1':
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                            amount += 1
                            remote_local = True
                    if remote_local:
                        pTime = self.getTime(self.sleepTime) - pTime
                        lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                        rMem1 = rMem1 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                        lProc = 2 * amount
                        rProc1 = 2 * amount
                        wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                                linksAggregateCoreClusterNodeSrc[i], 0, amount, 'linkAggregateCore-remote-local', logFile)
                        continue
                    """
                        remote - remote (nodeX - nodeX)
                        - remote veth
                        - 0 local process - 0 remote process
                    """
                    rMem1 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    rMem2 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    pTime = self.getTime(self.sleepTime)
                    for x in range(len(self.linksAggregateCoreList)):
                        if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                                self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                                linksAggregateCoreClusterNodeSrc[i] != 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1' and \
                                self.linksAggregateCoreList[x][0] == self.linksAggregateCoreList[x][1]:
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                            amount += 1
                            remoteX_remoteX = True
                    if remoteX_remoteX:
                        pTime = self.getTime(self.sleepTime) - pTime
                        rMem1 = rMem1 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                        rMem2 = rMem2 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                        wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                                linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeSrc[y], amount, \
                                'linkAggregateCore-remoteX-remoteX', logFile)
                        continue
                    """
                        remote - remote (nodeX - nodeY)
                        - SSH tunnel to send command (2 local process - 2 remote process)
                        - 2 local process - 2 remote process (nodeX) - 2 remote process (nodeY)
                    """
                    lMem = self.getMemLocal(self.sleepTimeMem)
                    rMem1 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                    rMem2 = self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                    pTime = self.getTime(self.sleepTime)
                    for x in range(len(self.linksAggregateCoreList)):
                        if self.linksAggregateCoreList[x][2] == linksAggregateCoreClusterNodeSrc[i] and \
                                self.linksAggregateCoreList[x][3] == linksAggregateCoreClusterNodeDst[y] and \
                                linksAggregateCoreClusterNodeSrc[i] != 'node1' and linksAggregateCoreClusterNodeDst[y] != 'node1' and \
                                self.linksAggregateCoreList[x][0] != self.linksAggregateCoreList[x][1]:
                            mc.link(self.linksAggregateCoreList[x][0], self.linksAggregateCoreList[x][1])
                            amount += 1
                            remoteX_remoteY = True
                    if remoteX_remoteY:
                        pTime = self.getTime(self.sleepTime) - pTime
                        lMem = lMem - self.getMemLocal(self.sleepTimeMem)
                        rMem1 = rMem1 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeSrc[i])
                        rMem2 = rMem2 - self.getMemRemote(self.sleepTimeMem, linksAggregateCoreClusterNodeDst[y])
                        lProc = 2 * amount
                        rProc1 = 2 * amount
                        rProc2 = 2 * amount
                        wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                                linksAggregateCoreClusterNodeSrc[i], linksAggregateCoreClusterNodeSrc[y], amount, \
                                'linkAggregateCore-remoteX-remoteX', logFile)
                        continue

            lMem = self.getMemLocal(self.sleepTimeMem)
            pTime = self.getTime(self.sleepTime)
            mc._start()
            pTime = self.getTime(self.sleepTime) - pTime
            lMem = lMem - self.getMemLocal(self.sleepTimeMem)
            wf.string(pTime, lMem, 0, 0, 0, 'node1', 1, 'start', logFile)
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
                    self.linksHostEdgeList[i] = [self.hostList[i][0], self.edgeSwitchList[y][0], self.hostList[i][1]]
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
                        str(self.edgeSwitchList[i][0][2:-len(str(self.edgeSwitchList[i][2]))]) + str(podRangeNumber + y), \
                        self.edgeSwitchList[i][1]]
                countLink += 1
        """
            Aggregate <--> Core
        """
        forBegin = 0
        forEnd = self.pod / 2
        countLink = 0
        for i in range(len(self.aggregateSwitchList)):
            for y in xrange(forBegin, forEnd):
                for x in range(len(self.coreSwitchList)):
                    if self.coreSwitchList[x][0] == 's1' + str(y):
                        corePlace = self.coreSwitchList[x][1]
                        #if self.aggregateSwitchList[i][1] == 'node1' and corePlace == 'node1':
                        #    srcDstPlace = 'local-local'
                        #elif self.aggregateSwitchList[i][1] != 'node1' and corePlace != 'node1':
                        #    srcDstPlace = 'remote-remote'
                        #else:
                        #    srcDstPlace = 'local-remote'
                #self.linksAggregateCoreList[countLink] = [self.aggregateSwitchList[i][0], 's1' + str(y), srcDstPlace]
                self.linksAggregateCoreList[countLink] = [self.aggregateSwitchList[i][0], 's1' + str(y), self.aggregateSwitchList[i][1], corePlace]
                #print(self.linksAggregateCoreList[countLink])
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
