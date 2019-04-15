#!/usr/bin/python2

import writeToFile as wf
import resourceData as rd
import mn_distributed as mnd
import time

class Mininet(object):
    def __init__(self, mininet, timeStamp, logFile, sleepTime, sleepTimeMem, clusterNodesLength, networkLength, \
            arrayNetworkLength, mclink):
        self.mininet = mininet
        self.timeStamp = timeStamp
        self.logFile = logFile
        self.sleepTime = sleepTime
        self.sleepTimeMem = sleepTimeMem
        self.clusterNodesLength = clusterNodesLength
        self.mclink = mclink
	
        object_array = CreateArray(self.logFile, self.clusterNodesLength, networkLength, arrayNetworkLength, self.mclink)
        self.cellSwitchList = object_array.cellSwitches(arrayNetworkLength)
        self.hostCellList, self.hostSwitchCellList = object_array.hostsSwitchesCell(arrayNetworkLength)
        self.controllerList = object_array.controller()
        self.linksHostHostSwitch, self.linksHostSwitchHostSwitch, self.linksHostCellSwitch = \
                object_array.links(self.hostCellList, self.hostSwitchCellList)

        wf.line('\nLine structure:\n\
        - time: time spent on task execution (seconds)\n\
        - local memory: number of memory used to execute the task on local cluster node (bytes)\n\
        - remote memory: number of memory used to execute the task on remote cluster node (bytes)\n\
        - local processes: number of persistent processes created to execute the task on local cluster node\n\
        - remote processes: number of persistent processes created to execute the task on remote cluster node\n\
        - cluster node: the name of the cluster node on which the task is running\n\
        - amount: amount of elements created (hosts, switches, links) on the task\n\
        - description: a description that describe the what the task does\n', logFile)

        self.callMininet()

    def callMininet(self):
        for mininet in self.mininet:                    # Mininet Cluster and Maxinet
            if mininet == 'mc':
                for link in self.mclink:
                    self.distributedMininet(mininet, link)
            elif mininet == 'mn':
                self.distributedMininet(mininet, None)

    def distributedMininet(self, mininet, link):
        if mininet == 'mc':
            print('\n-<MininetCluster>-\n--<%s>--' % (link))
            wf.line('-<MininetCluster>-\n--<%s>--' %(link), self.logFile)
        elif mininet == 'mn':
            print('\n-<MaxiNet>-\n')
            wf.line('--<MaxiNet>--', self.logFile)
        """
            Initiating Mininet Cluster Topology
        """
        if mininet == 'mc':
            print('\nInitiating Mininet Cluster Topology...')
            mc = mnd.MininetCluster()
        elif mininet == 'mn':
            print('\nInitiating Maxinet Topology...')
            mn = mnd.MaxiNet()
            for i in range(self.clusterNodesLength):
                clusterNodeName = 'node%s' % (i +1)
                if clusterNodeName == 'node1':
                    lMem = rd.getMemLocal(self.sleepTimeMem)
                    pTime = rd.getTime(self.sleepTime)
                    mn.workers(clusterNodeName)
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    wf.string(pTime, lMem, 0, 4, 0, clusterNodeName, 2, 'MaxiNetFrontendServer', self.logFile)
                else:
                    rMem = rd.getMemRemote(self.sleepTimeMem, clusterNodeName)
                    pTime = rd.getTime(self.sleepTime)
                    mn.workers(clusterNodeName)
                    pTime = rd.getTime(self.sleepTime) - pTime
                    rMem = rMem - rd.getMemRemote(self.sleepTimeMem, clusterNodeName)
                    wf.string(pTime, 0, rMem, 0, 3, clusterNodeName, 1, 'MaxiNetWorker', self.logFile)
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            mc.topology(link)
        elif mininet == 'mn':
            mn.topology(self.clusterNodesLength)
        pTime = rd.getTime(self.sleepTime) - pTime
        lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
        wf.string(pTime, lMem, 0, 0, 0, 'node1', 0, 'topology', self.logFile)
        """
            Creating Controller
            self.controllerList[i][0] = controller name
        """
        print('\nController...')
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            for i in range(len(self.controllerList)):
                mc.controller(self.controllerList[i][0])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            wf.string(pTime, lMem, 0, 1, 0, 'node1', 0, 'controller', self.logFile)
        """
            Creating Cell switches
            self.cellSwitchList[i][0] = Cell switch name (ex.: s0)
            self.self.cellSwitchList[i][1] = node name (ex.: node1)
            self.self.cellSwitchList[i][2] = worker ID (ex.: 0)
        """
        print('\nCell switches...')
        cellSwitchClusterNode = []
        for i in range(len(self.cellSwitchList)):
            exist = False
            for y in range(len(cellSwitchClusterNode)):
                if self.cellSwitchList[i][1] == cellSwitchClusterNode[y]:
                    exist = True
            if not exist:
                cellSwitchClusterNode.append(self.cellSwitchList[i][1])
        for i in range(len(cellSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, cellSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.cellSwitchList)):
                if cellSwitchClusterNode[i] == self.cellSwitchList[y][1]:
                    if cellSwitchClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.switch(self.cellSwitchList[y][0], self.cellSwitchList[y][1])
                    elif mininet == 'mn':
                        mn.switch(self.cellSwitchList[y][0], self.cellSwitchList[y][2])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, cellSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, cellSwitchClusterNode[i], amount, 'cellSwitch', self.logFile)
        """
            Creating Hosts
            self.hostCellList[i][0] = host name (ex.: h00)
            self.hostCellList[i][3] = node name (ex.: node1)
            self.hostCellList[i][4] = worker ID (ex.: 0)
        """
        print('\nHosts cell...')
        hostCellClusterNode = []
        for i in range(len(self.hostCellList)):
            exist = False
            for y in range(len(hostCellClusterNode)):
                if self.hostCellList[i][3] == hostCellClusterNode[y]:
                    exist = True
            if not exist:
                hostCellClusterNode.append(self.hostCellList[i][3])
        for i in range(len(hostCellClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, hostCellClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.hostCellList)):
                if hostCellClusterNode[i] == self.hostCellList[y][3]:
                    if hostCellClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.host(self.hostCellList[y][0], self.hostCellList[y][3])
                    elif mininet == 'mn':
                        mn.host(self.hostCellList[y][0], self.hostCellList[y][4])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, hostCellClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, hostCellClusterNode[i], amount, 'hostCell', self.logFile)
        """
            Creating Host Switches
            self.hostSwitchCellList[i][0] = host name (ex.: hs00)
            self.hostSwitchCellList[i][3] = node name (ex.: node1)
            self.hostSwitchCellList[i][4] = worker ID (ex.: 0)
        """
        print('\nHost switches cell...')
        hostSwitchCellClusterNode = []
        for i in range(len(self.hostSwitchCellList)):
            exist = False
            for y in range(len(hostSwitchCellClusterNode)):
                if self.hostSwitchCellList[i][3] == hostSwitchCellClusterNode[y]:
                    exist = True
            if not exist:
                hostSwitchCellClusterNode.append(self.hostSwitchCellList[i][3])
        for i in range(len(hostSwitchCellClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, hostSwitchCellClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.hostSwitchCellList)):
                if hostSwitchCellClusterNode[i] == self.hostSwitchCellList[y][3]:
                    if hostSwitchCellClusterNode[i] == 'node1':
                        amount += 1
                        lProc += 1
                        rProc = 0
                        rMem = 0
                    else:
                        amount += 1
                        lProc += 2
                        rProc += 4
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.switch(self.hostSwitchCellList[y][0], self.hostSwitchCellList[y][3])
                    elif mininet == 'mn':
                        mn.switch(self.hostSwitchCellList[y][0], self.hostSwitchCellList[y][4])
            pTime = rd.getTime(self.sleepTime) - pTime
            lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, hostSwitchCellClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, hostSwitchCellClusterNode[i], amount, 'hostSwitchCell', self.logFile)
        """
            Link between Hosts and Host Switches
            self.linksHostHostSwitch[i][0] = Host name (ex.: h00)
            self.linksHostHostSwitch[i][1] = Host switch name (ex.: hs00)
            self.linksHostHostSwitch[i][2] = node name (ex.: node1)

        """
        print('\nlink: Host <-> Host Switch...')
        linksHostHostSwitchClusterNode = []
        for i in range(len(self.linksHostHostSwitch)):
            exist = False
            for y in range(len(linksHostHostSwitchClusterNode)):
                if self.linksHostHostSwitch[i][2] == linksHostHostSwitchClusterNode[y]:
                    exist = True
            if not exist:
                linksHostHostSwitchClusterNode.append(self.linksHostHostSwitch[i][2])
        for i in range(len(linksHostHostSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, linksHostHostSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.linksHostHostSwitch)):
                if linksHostHostSwitchClusterNode[i] == self.linksHostHostSwitch[y][2]:
                    if linksHostHostSwitchClusterNode[i] == 'node1':
                        amount += 1
                        rMem = 0
                    else:
                        lMem = 0
                        amount += 1
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.link(self.linksHostHostSwitch[y][0], self.linksHostHostSwitch[y][1])
                    elif mininet == 'mn':
                        mn.link(self.linksHostHostSwitch[y][0], self.linksHostHostSwitch[y][1])
            pTime = rd.getTime(self.sleepTime) - pTime
            if not clusterNodeRemote:
                lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, linksHostHostSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, linksHostHostSwitchClusterNode[i], amount, 'linkHostHostSwitch', self.logFile) 
        """
            Link between Hosts and Cell Switches
            self.linksHostCellSwitch[i][0] = Host name (ex.: h00)
            self.linksHostCellSwitch[i][1] = Cell switch name (ex.: s0)
            self.linksHostCellSwitch[i][2] = node name (ex.: node1)
        """
        print('\nlink: Host <-> Cell Switch...')
        linksHostCellSwitchClusterNode = []
        for i in range(len(self.linksHostCellSwitch)):
            exist = False
            for y in range(len(linksHostCellSwitchClusterNode)):
                if self.linksHostCellSwitch[i][2] == linksHostCellSwitchClusterNode[y]:
                    exist = True
            if not exist:
                linksHostCellSwitchClusterNode.append(self.linksHostCellSwitch[i][2])
        for i in range(len(linksHostCellSwitchClusterNode)):
            lMem = rd.getMemLocal(self.sleepTimeMem)
            rMem = rd.getMemRemote(self.sleepTimeMem, linksHostCellSwitchClusterNode[i])
            pTime = rd.getTime(self.sleepTime)
            amount = 0
            lProc = 0
            rProc = 0
            clusterNodeRemote = False
            for y in range(len(self.linksHostCellSwitch)):
                if linksHostCellSwitchClusterNode[i] == self.linksHostCellSwitch[y][2]:
                    if linksHostCellSwitchClusterNode[i] == 'node1':
                        amount += 1
                        rMem = 0
                    else:
                        lMem = 0
                        amount += 1
                        clusterNodeRemote = True
                    if mininet == 'mc':
                        mc.link(self.linksHostCellSwitch[y][0], self.linksHostCellSwitch[y][1])
                    elif mininet == 'mn':
                        mn.link(self.linksHostCellSwitch[y][0], self.linksHostCellSwitch[y][1])
            pTime = rd.getTime(self.sleepTime) - pTime
            if not clusterNodeRemote:
                lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
            if clusterNodeRemote:
                rMem = rMem - rd.getMemRemote(self.sleepTimeMem, linksHostCellSwitchClusterNode[i])
            wf.string(pTime, lMem, rMem, lProc, rProc, linksHostCellSwitchClusterNode[i], amount, 'linkHostCellSwitch', self.logFile)        
        """
            Link between Host Switch to Host Switch
            self.linksHostSwitchHostSwitch[i][0] = Host Switch name A (ex.: hs00)
            self.linksHostSwitchHostSwitch[i][1] = Host Switch name B (ex.: hs10)
            self.linksHostSwitchHostSwitch[i][2] = Host Switch A cluster node (ex.: node1)
            self.linksHostSwitchHostSwitch[i][3] = Host Switch B cluster node (ex.: node2)
        """
        print('\nlink: Host Switch <-> Host Switch...')
        linksHostSwitchHostSwitchClusterNodeSrc = []
        linksHostSwitchHostSwitchClusterNodeDst = []
        for i in range(len(self.linksHostSwitchHostSwitch)):
            exist = False
            for y in range(len(linksHostSwitchHostSwitchClusterNodeSrc)):
                if self.linksHostSwitchHostSwitch[i][2] == linksHostSwitchHostSwitchClusterNodeSrc[y]:
                    exist = True
            if not exist:
                linksHostSwitchHostSwitchClusterNodeSrc.append(self.linksHostSwitchHostSwitch[i][2])
        for i in range(len(self.linksHostSwitchHostSwitch)):
            exist = False
            for y in range(len(linksHostSwitchHostSwitchClusterNodeDst)):
                if self.linksHostSwitchHostSwitch[i][3] == linksHostSwitchHostSwitchClusterNodeDst[y]:
                    exist = True
            if not exist:
                linksHostSwitchHostSwitchClusterNodeDst.append(self.linksHostSwitchHostSwitch[i][3])
        for i in range(len(linksHostSwitchHostSwitchClusterNodeSrc)):
            for y in range(len(linksHostSwitchHostSwitchClusterNodeDst)):
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
                lMem = rd.getMemLocal(self.sleepTimeMem)
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksHostSwitchHostSwitch)):
                    if self.linksHostSwitchHostSwitch[x][2] == linksHostSwitchHostSwitchClusterNodeSrc[i] and \
                            self.linksHostSwitchHostSwitch[x][3] == linksHostSwitchHostSwitchClusterNodeDst[y] and \
                            linksHostSwitchHostSwitchClusterNodeSrc[i] == 'node1' and linksHostSwitchHostSwitchClusterNodeDst[y] == 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        amount += 1
                        local_local = True
                if local_local:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksHostSwitchHostSwitchClusterNodeSrc[i], linksHostSwitchHostSwitchClusterNodeDst[y], amount, \
                            'linkHostSwitchHostSwitch-local-local', self.logFile)
                    continue
                """
                    local - remote (node1 - nodeX)
                    - SSH tunnel
                    - 2 local process - 2 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksHostSwitchHostSwitch)):
                    if self.linksHostSwitchHostSwitch[x][2] == linksHostSwitchHostSwitchClusterNodeSrc[i] and \
                            self.linksHostSwitchHostSwitch[x][3] == linksHostSwitchHostSwitchClusterNodeDst[y] and \
                            linksHostSwitchHostSwitchClusterNodeSrc[i] == 'node1' and linksHostSwitchHostSwitchClusterNodeDst[y] != 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        amount += 1
                        local_remote = True
                if local_remote:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksHostSwitchHostSwitchClusterNodeSrc[i], linksHostSwitchHostSwitchClusterNodeDst[y], amount, \
                            'linkHostSwitchHostSwitch-local-remote', self.logFile)
                    continue
                """
                    remote - local (nodeX - node1)
                    - SSH tunnel
                    - 2 local process - 2 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksHostSwitchHostSwitch)):
                    if self.linksHostSwitchHostSwitch[x][3] == linksHostSwitchHostSwitchClusterNodeDst[y] and \
                            self.linksHostSwitchHostSwitch[x][2] == linksHostSwitchHostSwitchClusterNodeSrc[i] and \
                            linksHostSwitchHostSwitchClusterNodeDst[y] == 'node1' and linksHostSwitchHostSwitchClusterNodeSrc[i] != 'node1':
                        if mininet == 'mc':
                            mc.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        amount += 1
                        remote_local = True
                if remote_local:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksHostSwitchHostSwitchClusterNodeSrc[i], linksHostSwitchHostSwitchClusterNodeDst[y], amount, \
                            'linkHostSwitchHostSwitch-remote-local', self.logFile)
                    continue
                """
                    remote - remote (nodeX - nodeX)
                    - remote veth
                    - 0 local process - 0 remote process
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                rMem2 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksHostSwitchHostSwitch)):
                    if self.linksHostSwitchHostSwitch[x][2] == linksHostSwitchHostSwitchClusterNodeSrc[i] and \
                            self.linksHostSwitchHostSwitch[x][3] == linksHostSwitchHostSwitchClusterNodeDst[y] and \
                            linksHostSwitchHostSwitchClusterNodeSrc[i] != 'node1' and linksHostSwitchHostSwitchClusterNodeDst[y] != 'node1' and \
                            self.linksHostSwitchHostSwitch[x][2] == self.linksHostSwitchHostSwitch[x][3]:
                        if mininet == 'mc':
                            mc.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        amount += 1
                        remoteX_remoteX = True
                if remoteX_remoteX:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                    rMem2 = rMem2 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksHostSwitchHostSwitchClusterNodeSrc[i], linksHostSwitchHostSwitchClusterNodeDst[y], amount, \
                            'linkHostSwitchHostSwitch-remoteX-remoteX', self.logFile)
                    continue
                """
                    remote - remote (nodeX - nodeY)
                    - SSH tunnel to send command (2 local process - 2 remote process)
                    - 2 local process - 2 remote process (nodeX) - 2 remote process (nodeY)
                """
                lMem = rd.getMemLocal(self.sleepTimeMem)
                rMem1 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                rMem2 = rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                pTime = rd.getTime(self.sleepTime)
                for x in range(len(self.linksHostSwitchHostSwitch)):
                    if self.linksHostSwitchHostSwitch[x][2] == linksHostSwitchHostSwitchClusterNodeSrc[i] and \
                            self.linksHostSwitchHostSwitch[x][3] == linksHostSwitchHostSwitchClusterNodeDst[y] and \
                            linksHostSwitchHostSwitchClusterNodeSrc[i] != 'node1' and linksHostSwitchHostSwitchClusterNodeDst[y] != 'node1' and \
                            self.linksHostSwitchHostSwitch[x][2] != self.linksHostSwitchHostSwitch[x][3]:
                        if mininet == 'mc':
                            mc.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        elif mininet == 'mn':
                            mn.link(self.linksHostSwitchHostSwitch[x][0], self.linksHostSwitchHostSwitch[x][1])
                        amount += 1
                        remoteX_remoteY = True
                if remoteX_remoteY:
                    pTime = rd.getTime(self.sleepTime) - pTime
                    lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
                    rMem1 = rMem1 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeSrc[i])
                    rMem2 = rMem2 - rd.getMemRemote(self.sleepTimeMem, linksHostSwitchHostSwitchClusterNodeDst[y])
                    lProc = 2 * amount
                    rProc1 = 2 * amount
                    rProc2 = 2 * amount
                    wf.stringAggregateCoreRemote(pTime, lMem, rMem1, rMem2, lProc, rProc1, rProc2, \
                            linksHostSwitchHostSwitchClusterNodeSrc[i], linksHostSwitchHostSwitchClusterNodeDst[y], amount, \
                            'linkHostSwitchHostSwitch-remoteX-remoteY', self.logFile)
                    continue
        if mininet == 'mc':
            pass
            #mc.controllerPox()
        elif mininet == 'mn':
            pass
            #mn.controllerPox()
        lMem = rd.getMemLocal(self.sleepTimeMem)
        pTime = rd.getTime(self.sleepTime)
        if mininet == 'mc':
            mc._start()
        pTime = rd.getTime(self.sleepTime) - pTime
        lMem = lMem - rd.getMemLocal(self.sleepTimeMem)
        wf.string(pTime, lMem, 0, 0, 0, 'node1', 1, 'start', self.logFile)
        if mininet == 'mc':
            mc._stop()
        elif mininet == 'mn':
            mn._stop()
            for i in range(self.clusterNodesLength):
                clusterNodeName = 'node%s' % (i +1)
                mn._workers(clusterNodeName)


class CreateArray(object):
    """
        Host name = 'h' + <cellId> + <hostId>
        Switch-host name = 'hs' + <cellId> + <hostId>
        Cell switches name = 's' + <cellId>
        Controller name = 'c0'
    """
    def __init__(self, logFile, clusterNodesLength, networkLength, arrayNetworkLength, mclink):
        self.totalCell = networkLength                                          # Total number of cells
        self.hostPerCell = networkLength - 1                                    # Number of hosts per cell
        self.hostSwitchPerCell = self.hostPerCell                               # Number of host switches per cell
        self.totalHosts = self.hostPerCell * self.totalCell                     # Total number of hosts 
        self.totalHostSwitches = self.totalHosts                                # Total number of hosts switches

        print('\n-- DCELL --\n')
        print('\nTotal cells: %s\nTotal hosts: %s\nTotal host switches: %s\nHosts per cell: %s\nHost switches per cell: %s\n'
                % (self.totalCell, self.totalHosts, self.totalHostSwitches, self.hostPerCell, self.hostSwitchPerCell))

        wf.line('-- DCELL --\n\
        -- total_cell:%s\n\
        -- total_hosts:%s\n\
        -- total_host_switches:%s\n\
        -- hosts_per_cell:%s\n\
        -- host_switches_per_cell:%s\n'
        % (self.totalCell, self.totalHosts, self.totalHostSwitches, self.hostPerCell, self.hostSwitchPerCell), logFile)

    def cellSwitches(self, arrayNetworkLength):
        """
            Cell switches
        """
        cellSwitchList = []
        count = 0
        for i in range(len(arrayNetworkLength)):                                # i = number of cluster nodes
            for y in range(arrayNetworkLength[i]):                              # y = number of cells on each cluster node
                cellSwitchList.append(['s' + str(count), 'node' + str(i + 1), i])
                count += 1
        return(cellSwitchList)

    def hostsSwitchesCell(self, arrayNetworkLength):
        """
            Host switches
        """
        hostCellList = []
        hostSwitchCellList = []
        countCell = 0
        for i in range(len(arrayNetworkLength)):
            for y in range(arrayNetworkLength[i]):
                countHost = 0
                for x in range(self.hostPerCell):
                    hostCellList.append(['h' + str(countCell) + str(countHost), countCell, countHost, \
                            'node' + str(i + 1), i])
                    hostSwitchCellList.append(['hs1' + str(countCell) + str(countHost), countCell, countHost, \
                            'node' + str(i + 1), i])
                    countHost += 1
                countCell += 1
        return(hostCellList, hostSwitchCellList)

    def controller(self):
        """
            Controller
        """
        controllerList = []
        controllerList.append (['c0'])
        return(controllerList)

    def links(self, hostCellList, hostSwitchCellList):
        """
            Links
        """
        """
            Host <-> Host switch
        """
        linksHostHostSwitch = []
        for i in range(len(hostCellList)):
            linksHostHostSwitch.append([hostCellList[i][0], hostSwitchCellList[i][0], hostCellList[i][3]])
        """
            Host switch <-> Host switch (Host to Host)
        """
        linksHostSwitchHostSwitch = []
        for i in range(self.totalCell - 1):
            for j in range(self.totalCell - 1):
                if i <= j:
                    linksHostSwitchHostSwitch.append(['hs1' + str(i) + str(j), 'hs1' + str(j + 1) + str(i), None, None])
                    for y in range(len(hostSwitchCellList)):
                        if linksHostSwitchHostSwitch[-1][0] == hostSwitchCellList[y][0]:
                            linksHostSwitchHostSwitch[-1][2] = hostSwitchCellList[y][3]
                        if linksHostSwitchHostSwitch[-1][1] == hostSwitchCellList[y][0]:
                            linksHostSwitchHostSwitch[-1][3] = hostSwitchCellList[y][3]
        """
            Host Switch <-> Cell Switch
        """
        linksHostCellSwitch = []
        for i in range(len(hostSwitchCellList)):
            linksHostCellSwitch.append([hostSwitchCellList[i][0], 's' + str(hostCellList[i][1]), hostSwitchCellList[i][3]])
        
        return(linksHostHostSwitch, linksHostSwitchHostSwitch, linksHostCellSwitch)
