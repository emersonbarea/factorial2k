#!/usr/bin/python2

import time
import psutil
import paramiko

def getMemLocal(Sleep):
    time.sleep(Sleep)
    memory = psutil.virtual_memory()[4]
    return(memory)

def getMemRemote(Sleep, node):
    time.sleep(Sleep)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(node, username='mininet', password='abc123')
    stdin, stdout, stderr = client.exec_command('echo -e "import psutil\nprint(psutil.virtual_memory()[4])" | python')
    for line in stdout:
        rMem  = line.strip('\n')
    client.close()
    return(int(rMem))

def getTime(Sleep):
    time.sleep(Sleep)
    Time = time.time() - Sleep
    return(Time)
