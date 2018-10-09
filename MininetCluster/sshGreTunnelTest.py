#!/usr/bin/python

from mininet.examples.cluster import RemoteSSHLink, RemoteGRELink, RemoteHost
from mininet.net import Mininet
import os
import time

def qtdRodadas():
    try:
        varQtdRodadas=int(raw_input('Quantidade de rodadas iPerf3: '))
        return varQtdRodadas
    except:
        print('Apenas numeros...')
        qtdRodadas()

def perf(Link, Log):
  
    net = Mininet( host=RemoteHost, link=Link )

    h1 = net.addHost( 'h1', ip='20.0.0.1' )
    h2 = net.addHost( 'h2', ip='20.0.0.2', server='node2' )
    
    net.addLink( h1, h2 )
    
    net.start()
    
    #net.pingAll()
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    h2.cmd('iperf3 -s -f m &')
    time.sleep(2)
    
    h1.cmd('iperf3 -c 20.0.0.2 -f m >> %s' % (Log))
    time.sleep(10)
    
    net.stop()


def average(Log, qtdRodadas):

    resultArray = []

    with open(Log) as openedFile:
        lines = openedFile.readlines()

        # para todas linhas do arquivo, faca
        for line in lines:
            # se existir a palavra 'receiver' na linha, faca
            if 'receiver' in line:
                #cria uma lista temporaria para colocar os valores da linha
                tempLine = []
                #faz split da linha pegando apenas os campos nao vazio
                for c in line.split(' '):
                    if (c != ''):
                        tempLine.append(c)
                #coloca o valor da vazao no array
                resultArray.append(tempLine[6])

    #calcula a media da vazao e imprime
    soma = 0
    for i in resultArray:
        soma = soma + float(i)
    print('Vazao media no %s: %s Mbps' % (Log, soma/qtdRodadas))


if __name__ == '__main__':

    connectionType = ['SSH','GRE']
    qtdRodadas = qtdRodadas()

    # processamento principal
    for varConnectionType in connectionType:
        
        # RemoteSSHLink, RemoteGRELink
        Link = 'Remote' + varConnectionType + 'Link'
        # LogSSH.txt, LogGRE.txt
        Log = 'log/log' + varConnectionType + '.txt'

        # apagando os arquivos de log antigos
        os.system('rm %s 2> /dev/null' % (Log))

        for varQtdRodadas in range(0,qtdRodadas):
            perf(eval(Link), Log)

        # calcula e imprime as medias
        average(Log, qtdRodadas)
