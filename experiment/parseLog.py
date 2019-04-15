#!/usr/bin/python2

import os
import re
import itertools as it

def parseFile(path):
    """
        create directories to store files correctly
    """
    files = (file for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file)))
    for file in files:
        print file
        with open(path + file, 'r') as file:
            lines = file.readlines()
            totalLines = len(lines)
            """
                getting break points
            """
            for i, line in enumerate(lines):
                if line.startswith('        -- cluster_nodes:'):
                    clusterNode = 'clusterNode-' + re.split(':', line.rstrip())[1]
                elif line.strip() == '-- FATTREE --': 
                    topologyFtLine, topologyFt = i, 'FatTree'
                elif line.strip() == '-- DCELL --':
                    topologyDcLine, topologyDc = i, 'DCell'
                elif line.startswith('        -- total_pod:'):
                    pod = 'pod-' + re.split(':', line.rstrip())[1]
                elif line.startswith('        -- total_cell:'):
                    cell = 'cell-' + re.split(':', line.rstrip())[1]
            counter = it.count(start = topologyFtLine + 1)
            for line in it.islice(lines, topologyFtLine + 1, totalLines): 
                i = next(counter)
                if line.strip() == '--<RemoteSSHLink>--':
                    linkSSHFtMcLine, linkSSHFtMc = i, 'RemoteSSHLink'
                    mininetFtMcLine, mininetFtMc = i - 1, 'MininetCluster'
                    break 
            counter = it.count(start =  linkSSHFtMcLine + 1)
            for line in it.islice(lines, linkSSHFtMcLine + 1, totalLines): 
                i = next(counter)
                if line.strip() == '--<RemoteGRELink>--':
                    linkGREFtMcLine, linkGREFtMc = i, 'RemoteGRELink'
                    break
            counter = it.count(start =  linkGREFtMcLine + 1)
            for line in it.islice(lines, linkGREFtMcLine + 1, totalLines):
                i = next(counter)
                if line.strip() == '-<MaxiNet>-':
                    mininetFtMnLine, mininetFtMn = i, 'MaxiNet'
                    break

            counter = it.count(start = topologyDcLine + 1)
            for line in it.islice(lines, topologyDcLine + 1, totalLines):
                i = next(counter)
                if line.strip() == '--<RemoteSSHLink>--':
                    linkSSHDcMcLine, linkSSHDcMc = i, 'RemoteSSHLink'
                    mininetDcMcLine, mininetDcMc = i - 1, 'MininetCluster'
                    break
            counter = it.count(start =  linkSSHDcMcLine + 1)
            for line in it.islice(lines, linkSSHDcMcLine + 1, totalLines):
                i = next(counter)
                if line.strip() == '--<RemoteGRELink>--':
                    linkGREDcMcLine, linkGREDcMc = i, 'RemoteGRELink'
                    break
            counter = it.count(start =  linkGREDcMcLine + 1)
            for line in it.islice(lines, linkGREDcMcLine + 1, totalLines):
                i = next(counter)
                if line.strip() == '-<MaxiNet>-':
                    mininetDcMnLine, mininetDcMn = i, 'MaxiNet'
                    break
            """
                getting data using breaking points
            """
            """
                FatTree - MininetCluster - RemoteSSHLink
            """
            dataFtMcSSHList = []
            for line in it.islice(lines, linkSSHFtMcLine + 1, linkGREFtMcLine - 1):
                dataFtMcSSHList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyFt + '_' + mininetFtMc + '_' + linkSSHFtMc + '_' \
                    + pod + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataFtMcSSHList)
            """
                FatTree - MininetCluster - RemoteGRELink
            """
            dataFtMcGREList = []
            for line in it.islice(lines, linkGREFtMcLine + 1, mininetFtMnLine):
                dataFtMcGREList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyFt + '_' + mininetFtMc + '_' + linkGREFtMc + '_' \
                    + pod + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataFtMcGREList)
            """
                FatTree - MaxiNet
            """
            dataFtMnList = []
            for line in it.islice(lines, mininetFtMnLine + 1, topologyDcLine):
                dataFtMnList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyFt + '_' + mininetFtMn + '_' \
                    + pod + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataFtMnList)

            """
                DCell - MininetCluster - RemoteSSHLink
            """
            dataDcMcSSHList = []
            for line in it.islice(lines, linkSSHDcMcLine + 1, linkGREDcMcLine - 1):
                dataDcMcSSHList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyDc + '_' + mininetDcMc + '_' + linkSSHDcMc + '_' \
                    + cell + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataDcMcSSHList)
            """
                DCell - MininetCluster - RemoteGRELink
            """
            dataDcMcGREList = []
            for line in it.islice(lines, linkGREDcMcLine + 1, mininetDcMnLine):
                dataDcMcGREList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyDc + '_' + mininetDcMc + '_' + linkGREDcMc + '_' \
                    + cell + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataDcMcGREList)
            """
                DCell - MaxiNet
            """
            dataDcMnList = []
            for line in it.islice(lines, mininetDcMnLine + 1, totalLines):
                dataDcMnList.append(line.strip())
            fileName = path + 'parse/' + clusterNode + '_' + topologyDc + '_' + mininetDcMn + '_' \
                    + cell + '_' + file.name[17:-4] + '.log'
            writeToFile(fileName, 'w', dataDcMnList)
        file.close()

def parseTotalRAMProcess(path):
    """
        getting total RAM and process data from all files and creating total data files
    """
    memProcSumList = []
    writeToFileName = path + 'memProcSumList.log'
    files = (file for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file)))
    for file in files:
        useFile = False
        with open(path + file, 'r') as file:
            fullFileName = file.name
            fullFileNameSplitted = fullFileName.split('_')
            clusterLength =  fullFileNameSplitted[0].split('-')[1]
            topologyType = fullFileNameSplitted[1]
            mininetTemp = fullFileNameSplitted[2]
            if mininetTemp == 'MaxiNet':
                mininet = 'MN'
                topologyLength = fullFileNameSplitted[3].split('-')[1]
                useFile = True
            elif mininetTemp == 'MininetCluster':
                if fullFileNameSplitted[3] == 'RemoteGRELink':
                    mininet = 'MC'
                    topologyLength = fullFileNameSplitted[4].split('-')[1]
                    useFile = True

            if useFile:            
                lines = file.readlines()
                memSum = 0
                procSum = 0
                for line in lines:
                    if line.strip().endswith('X') or line.strip().endswith('Y') or line.strip().endswith('local') or \
                            line.strip().endswith('remote'):
                        if int(line.split(',')[1]) > 0:
                            memSum = memSum + int(line.split(',')[1])
                        elif int(line.split(',')[2]) > 0:
                            memSum = memSum + int(line.split(',')[2])
                        elif int(line.split(',')[3]) > 0:
                            memSum = memSum + int(line.split(',')[3])
                        procSum = procSum + int(line.split(',')[4]) + int(line.split(',')[5]) + int(line.split(',')[6])
                    else:
                        if int(line.split(',')[1]) > 0:
                            memSum = memSum + int(line.split(',')[1])
                        elif int(line.split(',')[2]) > 0:
                            memSum = memSum + int(line.split(',')[2])
                        procSum = procSum + int(line.split(',')[3]) + int(line.split(',')[4])
                data = clusterLength + ',' + topologyType + ',' + mininet + ',' + topologyLength + ',' + \
                        str(memSum) + ',' + str(procSum) + '\n'
                writeToFile(writeToFileName, 'a', data) 
        file.close()

def parseTotalRAMProcessScenarios(path):
    """
        creating scenarios consolidated data
    """
    writeToFileFatTree = path + 'memProcSumListScenariosFatTree.log'
    writeToFileDCell = path + 'memProcSumListScenariosDCell.log'

    line = 'cenario,tamanhoCluster,tipoTopologia,mininet,tamanhoTopologia,memoria,processos\n'
    
    writeToFile(writeToFileFatTree, 'a', line)
    writeToFile(writeToFileDCell, 'a', line)
    
    fileName = path + 'memProcSumList.log'

    with open(fileName, 'r') as file:
        lines = file.readlines()
        for line in lines:
            
            writeLineFatTree = False
            writeLineDCell = False
            
            if line.startswith('2,FatTree,MN,4'):
                lineFatTree = '1,' + line
                writeLineFatTree = True
            elif line.startswith('2,FatTree,MC,4'):
                lineFatTree = '2,' + line
                writeLineFatTree = True
            elif line.startswith('2,FatTree,MN,12'):
                lineFatTree = '3,' + line 
                writeLineFatTree = True
            elif line.startswith('2,FatTree,MC,12'):
                lineFatTree = '4,' + line 
                writeLineFatTree = True
            elif line.startswith('4,FatTree,MN,4'):
                lineFatTree = '5,' + line 
                writeLineFatTree = True
            elif line.startswith('4,FatTree,MC,4'):
                lineFatTree = '6,' + line 
                writeLineFatTree = True
            elif line.startswith('4,FatTree,MN,12'):
                lineFatTree = '7,' + line 
                writeLineFatTree = True
            elif line.startswith('4,FatTree,MC,12'):
                lineFatTree = '8,' + line 
                writeLineFatTree = True
            
            elif line.startswith('2,DCell,MN,4'):
                lineDCell = '1,' + line
                writeLineDCell = True
            elif line.startswith('2,DCell,MC,4'):
                lineDCell = '2,' + line
                writeLineDCell = True
            elif line.startswith('2,DCell,MN,12'):
                lineDCell = '3,' + line
                writeLineDCell = True
            elif line.startswith('2,DCell,MC,12'):
                lineDCell = '4,' + line
                writeLineDCell = True
            elif line.startswith('4,DCell,MN,4'):
                lineDCell = '5,' + line
                writeLineDCell = True
            elif line.startswith('4,DCell,MC,4'):
                lineDCell = '6,' + line
                writeLineDCell = True
            elif line.startswith('4,DCell,MN,12'):
                lineDCell = '7,' + line
                writeLineDCell = True
            elif line.startswith('4,DCell,MC,12'):
                lineDCell = '8,' + line
                writeLineDCell = True

            if writeLineFatTree:
                writeToFile(writeToFileFatTree, 'a', lineFatTree)
            elif writeLineDCell:
                writeToFile(writeToFileDCell, 'a', lineDCell)

        file.close()

def parseFileByMeasurement(path):
    """
        getting data by measurement points
    """
    files = (file for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file)))
    for file in files:
        with open(path + file, 'r') as file:
            fullFileName = file.name
            fileName = file.name.rsplit('_', 1)[0]
            lines = file.readlines()
            for line in lines:
                if line.strip().endswith('topology'):
                    writeToFile(fileName + '_topology.log', 'a', line)
                elif line.strip().endswith('controller'):
                    writeToFile(fileName + '_controller.log', 'a', line)
                elif line.strip().endswith('coreSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1': 
                        writeToFile(fileName + '_node1-coreSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-coreSwitch.log', 'a', line)
                elif line.strip().endswith('aggregateSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-aggregateSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-aggregateSwitch.log', 'a', line)
                elif line.strip().endswith('edgeSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-edgeSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-edgeSwitch.log', 'a', line)
                elif line.strip().endswith('host'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-host.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-host.log', 'a', line)
                elif line.strip().endswith('linkHostEdge'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-linkHostEdge.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-linkHostEdge.log', 'a', line)
                elif line.strip().endswith('linkEdgeAggregate'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-linkEdgeAggregate.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-linkEdgeAggregate.log', 'a', line)
                elif line.strip().endswith('linkAggregateCore-local-local'):
                    writeToFile(fileName + '_linkAggregateCore-local-local.log', 'a', line)
                elif line.strip().endswith('linkAggregateCore-local-remote'):
                    writeToFile(fileName + '_linkAggregateCore-local-remote.log', 'a', line)
                elif line.strip().endswith('linkAggregateCore-remote-local'):
                    writeToFile(fileName + '_linkAggregateCore-remote-local.log', 'a', line)
                elif line.strip().endswith('linkAggregateCore-remoteX-remoteX'):
                    writeToFile(fileName + '_linkAggregateCore-remoteX-remoteX.log', 'a', line)
                elif line.strip().endswith('linkAggregateCore-remoteX-remoteY'):
                    writeToFile(fileName + '_linkAggregateCore-remoteX-remoteY.log', 'a', line)
                elif line.strip().endswith('start'):
                    writeToFile(fileName + '_start.log', 'a', line)
                elif line.strip().endswith('MaxiNetFrontendServer'):
                    writeToFile(fileName + '_MaxiNetFrontendServer.log', 'a', line)
                elif line.strip().endswith('MaxiNetWorker'):
                    writeToFile(fileName + '_MaxiNetWorker.log', 'a', line)
                elif line.strip().endswith('cellSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-cellSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-cellSwitch.log', 'a', line)
                elif line.strip().endswith('hostCell'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-hostCell.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-hostCell.log', 'a', line)
                elif line.strip().endswith('hostSwitchCell'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-hostSwitchCell.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-hostSwitchCell.log', 'a', line)
                elif line.strip().endswith('linkHostHostSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-linkHostHostSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-linkHostHostSwitch.log', 'a', line)
                elif line.strip().endswith('linkHostCellSwitch'):
                    if re.split(',', line.rstrip())[5] == 'node1':
                        writeToFile(fileName + '_node1-linkHostCellSwitch.log', 'a', line)
                    else:
                        writeToFile(fileName + '_nodeX-linkHostCellSwitch.log', 'a', line)
                elif line.strip().endswith('linkHostSwitchHostSwitch-local-local'):
                    writeToFile(fileName + '_linkHostSwitchHostSwitch-local-local.log', 'a', line)
                elif line.strip().endswith('linkHostSwitchHostSwitch-local-remote'):
                    writeToFile(fileName + '_linkHostSwitchHostSwitch-local-remote.log', 'a', line)
                elif line.strip().endswith('linkHostSwitchHostSwitch-remoteX-remoteX'):
                    writeToFile(fileName + '_linkHostSwitchHostSwitch-remoteX-remoteX.log', 'a', line)
                elif line.strip().endswith('linkHostSwitchHostSwitch-remoteX-remoteY'):
                    writeToFile(fileName + '_linkHostSwitchHostSwitch-remoteX-remoteY.log', 'a', line)
        file.close()
        os.remove(fullFileName)
    """
        creating files headers
    """
    files = (file for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file)))
    for file in files:
        with open(path + file, 'r') as file:
            fileName = file.name
            content = file.name.rsplit('_', 1)[1][:-4]
            if content in ('controller', 'topology', 'node1-coreSwitch', 'node1-aggregateSwitch', 'node1-edgeSwitch', \
                    'node1-host', 'node1-linkHostEdge', 'node1-linkEdgeAggregate', 'start', 'MaxiNetFrontendServer', \
                    'MaxiNetWorker', 'node1-cellSwitch', 'node1-hostCell', 'node1-hostSwitchCell', \
                    'node1-linkHostCellSwitch', 'node1-linkHostHostSwitch', 'nodeX-aggregateSwitch', 'nodeX-cellSwitch', \
                    'nodeX-coreSwitch', 'nodeX-edgeSwitch', 'nodeX-host', 'nodeX-hostCell', 'nodeX-hostSwitchCell', \
                    'nodeX-linkEdgeAggregate', 'nodeX-linkHostCellSwitch', 'nodeX-linkHostEdge', 'nodeX-linkHostHostSwitch'):
                averageTime, averageLocalMemory, averageRemoteMemory = 0, 0, 0
                lines = file.readlines()
                os.remove(fileName)
                counter = it.count(start = 1)
                for line in lines:
                    averageTime = averageTime + float(re.split(',', line.rstrip())[0])
                    averageLocalMemory = averageLocalMemory + int(re.split(',', line.rstrip())[1])
                    averageRemoteMemory = averageRemoteMemory + int(re.split(',', line.rstrip())[2])
                    count = next(counter)
                averageTime = averageTime / count
                averageLocalMemory = averageLocalMemory / count
                averageRemoteMemory = averageRemoteMemory / count
                #header = 'averageTime,averageLocalMemory,averageRemoteMemory,time,localMemory,remoteMemory,localProcesses,remoteProcesses,clusterNode,amount,description\n'
                #writeToFile(fileName, 'a', header)
                for line in lines:
                    line = str(averageTime) + ',' + str(averageLocalMemory) + ',' + str(averageRemoteMemory) + ',' + line
                    writeToFile(fileName, 'a', line)    
            elif content in ('linkAggregateCore-local-local', 'linkAggregateCore-local-remote', \
                    'linkAggregateCore-remoteX-remoteX', 'linkAggregateCore-remoteX-remoteY', \
                    'linkAggregateCore-remote-local', 'linkHostSwitchHostSwitch-local-local', \
                    'linkHostSwitchHostSwitch-local-remote', 'linkHostSwitchHostSwitch-remoteX-remoteX', \
                    'linkHostSwitchHostSwitch-remoteX-remoteY'):
                averageTime, averageLocalMemory, averageRemoteMemory1, averageRemoteMemory2 = 0, 0, 0, 0
                lines = file.readlines()
                os.remove(fileName)
                counter = it.count(start = 1)
                for line in lines:
                    averageTime = averageTime + float(re.split(',', line.rstrip())[0])
                    averageLocalMemory = averageLocalMemory + int(re.split(',', line.rstrip())[1])
                    averageRemoteMemory1 = averageRemoteMemory1 + int(re.split(',', line.rstrip())[2])
                    averageRemoteMemory2 = averageRemoteMemory2 + int(re.split(',', line.rstrip())[3])
                    count = next(counter)
                averageTime = averageTime / count
                averageLocalMemory = averageLocalMemory / count
                averageRemoteMemory1 = averageRemoteMemory1 / count
                averageRemoteMemory2 = averageRemoteMemory2 / count
                #header = 'averageTime,averageLocalMemory,averageRemoteMemory1,averageRemoteMemory2,time,localMemory,remoteMemory1,remoteMemory2,localProcesses,remoteProcesses1,remoteProcesses2,clusterNode1,clusterNode2,amount,description\n'
                #writeToFile(fileName, 'a', header)
                for line in lines:
                    line = str(averageTime) + ',' + str(averageLocalMemory) + ',' + str(averageRemoteMemory1) + ',' + \
                            str(averageRemoteMemory2) + ',' + line
                    writeToFile(fileName, 'a', line)
        file.close()

    """
        joining related files
    """
    """
        FatTree - MininetCluster - node1
    """
    files = (file for file in os.listdir(path)
        if os.path.isfile(os.path.join(path, file)))
    for file in files:
        with open(path + file, 'r') as file:
            originalFileName = file.name
            fileName = str(file.name.rsplit('_', 1)[0]) + '_data.log' 
            content = file.name.rsplit('_', 1)[1][:-4]
            if content in ('controller', 'topology', 'node1-coreSwitch', 'node1-aggregateSwitch', 'node1-edgeSwitch', \
                    'node1-host', 'node1-linkHostEdge', 'node1-linkEdgeAggregate', 'start'):
                lines = file.read()
                writeToFile(fileName, 'a', lines)
            elif content == 'linkAggregateCore-local-local':
                lines = file.readlines()
                for line in lines:
                    lineSplit = re.split(',', line.rstrip())
                    data = ','.join(lineSplit[0:3] + lineSplit[4:7] + lineSplit[8:10] + lineSplit[11:12] + \
                            lineSplit[13:]) + '\n'
                    writeToFile(fileName, 'a', data)
        file.close()
        os.remove(originalFileName)

def writeToFile(fileName, writeType, data):
    """
        writing files
    """
    if writeType == 'w':
        file = open(fileName, writeType)
        for item in data:
            file.write('%s\n' % (item))
        file.close()
    elif writeType == 'a':
        with open(fileName, writeType) as file:
            file.write(data)
        file.close()

if __name__ == '__main__':
    path = './log/'
    parseFile(path)
    path = path + '/parse/'
    ####parseFileByMeasurement(path)
    parseTotalRAMProcess(path)
    parseTotalRAMProcessScenarios(path)
