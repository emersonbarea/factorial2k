#!/bin/bash

node=<node_number>

function welcome() {
    printf 'This script will configure:\n - hostname: node'$node'\n - eth1 address: 10.0.0.'$node
}

function ask() {
    printf '\nDo you really want to continue? ([y]/n) '
    read question
    if [ "$question" != "" ] && [ "$question" != "Y" ] && [ "$question" != "y" ] \
        && [ "$question" != "N" ] && [ "$question" != "n" ]; then
            printf '\e[1;31m%-6s\e[m' 'error: Press only Y|y or N|n'
            ask;
    fi
}

function configure_node() {
    # Setting hostname
    hostnamectl set-hostname node$node;
    # Setting eth1 configuration in /etc/network/interfaces
    echo $'\nallow-hotplug eth1\niface eth1 inet static\naddress 10.0.0.'$node$'\nnetmask 255.255.255.0' >> /etc/network/interfaces;
    reboot;
}

welcome;
ask;
if [ "$question" = "" ] || [ "$question" = "Y" ] || [ "$question" = "y" ] ; then
    configure_node;
fi
