#!/bin/bash

# Factorial 2^k install script for Ubuntu 18.04.1 Server LTS (Bionic Beaver)
# Emerson Barea (emerson.barea@gmail.com)

function welcome() {
    printf '\n%s\n' 'This script creates the complete environment for Factorial 2^k experiments.
                   Some requirements must be met:
                   - Ubuntu 18.04.1 Server LTS (Bionic Beaver)
                   - 2 NICs (1 for administration and 2 for communication between cluster nodes)
                   - Internet access
                   - Initial user with "sudo" rights
                   Note: the user "mininet" will be created, so it should not exist previously.'
}

function qtd_hosts() {
    printf '\n%s' 'Answer: how many cluster nodes will be created? (only number. Ex.: 3): '
    read var_qtd_hosts

    # testing if "var_qtd_hosts" is a number
    re='^[0-9]+$'
    if ! [[ $var_qtd_hosts =~ $re ]] ; then
        printf '\e[1;31m%-6s\e[m' 'error: Write only numbers'
        qtd_hosts;
    fi
}

function install_packages() {
    function app_mininet() {
        printf '\n%s' '- Mininet ([y]/n): '
        read var_app_mininet

        # testing if "var_app_mininet" is y or n
        if [ "$var_app_mininet" != "" ] && [ "$var_app_mininet" != "Y" ] && [ "$var_app_mininet" != "y" ] \
        && [ "$var_app_mininet" != "N" ] && [ "$var_app_mininet" != "n" ]; then
            printf '\e[1;31m%-6s\e[m' 'error: Press only Y|y or N|n'
            app_mininet;
        fi
    }
    function app_nps() {
        printf '%s' '- Network Prototype Simulator (NPS) ([y]/n): '
        read var_app_nps

        # testing if "var_app_nps" is y or n
        if [ "$var_app_nps" != "" ] && [ "$var_app_nps" != "Y" ] && [ "$var_app_nps" != "y" ] \
        && [ "$var_app_nps" != "N" ] && [ "$var_app_nps" != "n" ]; then
            printf '\e[1;31m%-6s\e[m' 'error: Press only Y|y or N|n'
            app_nps;
        fi
    }
    function app_maxinet() {
        printf '%s' '- MaxiNet ([y]/n): '
        read var_app_maxinet

        # testing if "app_maxinet" is y or n
        if [ "$var_app_maxinet" != "" ] && [ "$var_app_maxinet" != "Y" ] && [ "$var_app_maxinet" != "y" ] \
        && [ "$var_app_maxinet" != "N" ] && [ "$var_app_maxinet" != "n" ]; then
            printf '\e[1;31m%-6s\e[m' 'error: Press only Y|y or N|n'
            app_maxinet;
        fi
    }
    printf '\n%s' 'What application do you want to install?'
    app_mininet;
    app_nps;
    app_maxinet;
}

function update_SO_install_packages() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Initiating SO update and package install...'
    printf '\e[1;33m%-6s\e[m\n' 'Please, confirm if you computer has internet connectivity.'
    apt update
    apt install language-pack-pt -y
    apt upgrade -y
    apt install git vim htop ethtool sysfsutils python-pip python3-pip ifupdown mc strace tcpdump netcat nmap python-scapy whois -y
}

function network_configuration() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Configuring network interface...'
    printf '\e[1;33m%-6s\e[m\n' 'Removing Netplan, erasing any previus configuration and renaming NIC interfaces to "eth0" and "eth1".'
    apt autoremove netplan netplan.io nplan -y
    sed -i -- 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"/g' /etc/default/grub
    grub-mkconfig -o /boot/grub/grub.cfg
    printf '\e[1;33m%-6s\e[m\n' 'eth0 will be configured to DHCP client after reboot'
    echo $'auto lo\niface lo inet loopback\n\nallow-hotplug eth0\niface eth0 inet dhcp' > /etc/network/interfaces
    printf '\n%s\n' 'showing /etc/network/interfaces'
    cat /etc/network/interfaces
}

function user() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Creating "mininet" user...'
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous "mininet" user data.'
    userdel -r mininet											# apaga usuario mininet previamente cadastrado
    useradd -m -p $(mkpasswd -m sha-512 -S saltsalt -s <<< abc123) -s /bin/bash mininet			# cria usuario mininet
    printf '\e[1;32m%-6s\e[m\n' 'USERNAME:mininet'
    printf '\e[1;32m%-6s\e[m\n' 'PASSWORD:abc123'
    printf '\e[1;33m%-6s\e[m\n' 'Putting user "mininet" to sudoers'
    echo 'mininet     ALL=NOPASSWD: ALL' >> /etc/sudoers						# coloca usuario mininet no sudo
    
}

function hosts_file() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Creating "hosts" file...'
    sed -i -- 's/preserve_hostname: false/preserve_hostname: true/g' /etc/cloud/cloud.cfg		# tornando hostname configurado pelo usuário permanente
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    cp /dev/null /etc/hosts										# limpa arquivo hosts
    echo 127.0.0.1	localhost.localdomain	localhost > /etc/hosts					# cadastra loopback no arquivo hosts
    for ((i=1; i<=$var_qtd_hosts; i++)); do echo 10.0.0.$i    node$i >> /etc/hosts; done
    printf '\n%s\n' 'showing /etc/hosts'
    cat /etc/hosts
}

function ssh_file() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Configuring SSH...'
    sed -i -- 's/#AllowAgentForwarding yes/AllowAgentForwarding yes/g' /etc/ssh/sshd_config
    sed -i -- 's/#AllowTcpForwarding yes/AllowTcpForwarding yes/g' /etc/ssh/sshd_config
    sed -i -- 's/#PermitTunnel no/PermitTunnel yes/g' /etc/ssh/sshd_config
    
    printf '\n\e[1;33m%-6s\e[m\n' 'Creating and exchanging SSH key for "mininet" user'
    sudo -u mininet ssh-keygen -t rsa -N "" -f /home/mininet/.ssh/id_rsa               			# gerando a chave ssh do usuário mininet

    printf '\n\e[1;33m%-6s\e[m\n' 'Adding the mininet user key in the authorized_keys'
    for (( c=1; c<=$var_qtd_hosts; c++ )); do sudo -u mininet cat /home/mininet/.ssh/id_rsa.pub | \
          sudo -u mininet tee --append /home/mininet/.ssh/authorized_keys; done                        	# adicionando a chave do usuário mininet no authorized_keys (var_qtd_hosts)

    printf '\n\e[1;33m%-6s\e[m\n' 'Changing hostnames keys in authorized_keys'
    for i in $(cat -n /home/mininet/.ssh/authorized_keys | awk '{print $1}'); \
          do sed -Ei "${i}s/@.*/@node$i/" /home/mininet/.ssh/authorized_keys; done            		# mudando todos nomes de hosts do arquivo para "node" para facilitar modificação abaixo

    sudo -u mininet chmod 755 /home/mininet/.ssh/authorized_keys
    echo $'Host *\nStrictHostKeyChecking no' | sudo -u mininet tee --append /home/mininet/.ssh/config   # configurando ssh para não verificar fingerprint
    sudo -u mininet chmod 400 /home/mininet/.ssh/config
    printf '\n%s\n' 'showing /home/mininet/.ssh/authorized_keys'
    cat /home/mininet/.ssh/authorized_keys
}

function node_file() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Creating configuration file for all cluster nodes ...'
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $FACTORIAL2K_DIR/nodes									# apagando os arquivos de configuracao previos
    mkdir -p $FACTORIAL2K_DIR/nodes
    for ((i=1; i<=$var_qtd_hosts; i++)); do echo "hostnamectl set-hostname node"$i"; echo \
          '\nallow-hotplug eth1\niface eth1 inet static\naddress 10.0.0.$i\nnetmask 255.255.255.0' \
          >> /etc/network/interfaces; reboot" >> $FACTORIAL2K_DIR/nodes/node$i.sh; chmod 755 $FACTORIAL2K_DIR/nodes/node$i.sh; done
    printf '\n%s\n' 'showing nodes file'
    cat $FACTORIAL2K_DIR/nodes/node*.sh
}

function install_app_mininet() {
    printf '\n\e[1;33m%-6s\e[m\n' '-- Installing Mininet 2.2.2 ...'
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $BUILD_DIR/mininet
    printf '\e[1;33m%-6s%s\e[m\n' 'Installing Mininet in ' $BUILD_DIR/mininet
    git clone git://github.com/mininet/mininet $BUILD_DIR/mininet
    cd $BUILD_DIR/mininet
    git checkout -b 2.2.2 2.2.2
    printf '\n\e[1;33m%-6s\e[m\n' 'Fixing iproute Mininet issue (using iproute2)'
    sed -i -- 's/iproute/iproute2/g' $BUILD_DIR/mininet/util/install.sh
    $BUILD_DIR/mininet/util/install.sh -a
    printf '\n\e[1;33m%-6s\e[m\n' 'Testing Mininet'
    mn --test pingall
}

function install_app_nps() {
    printf '\n\e[1;32m%-6s\e[m\n' '-- Installing Network Prototype Simulator (NPS) ...'
    printf '\n\e[1;33m%-6s\e[m\n' 'Resolving requirements'
    apt install python-networkx python-matplotlib python-paramiko -y
    apt install cmake default-jdk git ant libgl1-mesa-dev freeglut3-dev libgstreamer1.0-dev libgstreamermm-1.0-dev libwebkitgtk-dev -y
    apt autoremove -y
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $BUILD_DIR/nps
    printf '\e[1;33m%-6s%s\e[m\n' 'Installing NPS in ' $BUILD_DIR/nps
    git clone git://github.com/ARCCN/nps $BUILD_DIR/nps
    cp $BUILD_DIR/nps/config/services.py $BUILD_DIR/mininet
    cp $BUILD_DIR/nps/config/services.py $BUILD_DIR/mininet/build/lib.linux-x86_64-2.7/mininet

    printf '\e[1;33m%-6s%s\e[m\n' 'Installing METIS in ' $BUILD_DIR/metis
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $BUILD_DIR/metis-5.1.0*
    wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz -P $BUILD_DIR
    tar -xvzf $BUILD_DIR/metis-5.1.0.tar.gz -C $BUILD_DIR
    cd $BUILD_DIR/metis-5.1.0
    make config shared=1
    make
    make install
    ldconfig

    printf '\e[1;33m%-6s%s\e[m\n' 'Installing FloodLight in ' $BUILD_DIR/floodlight
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $BUILD_DIR/floodlight*
    wget https://github.com/floodlight/floodlight/archive/v0.90.tar.gz -P $BUILD_DIR
    tar -xvzf $BUILD_DIR/v0.90.tar.gz -C $BUILD_DIR
    cd $BUILD_DIR/floodlight-0.90
    ant

    printf '\e[1;33m%-6s%s\e[m\n' 'Installing FloodLight in ' $BUILD_DIR/floodlight
    sudo -H pip install --upgrade --force-reinstall -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 wxPython

    printf '\e[1;33m%-6s%s\e[m\n' 'Creating node list in ' $BUILD_DIR/nps/config/nodelist.txt
    cp /dev/null $BUILD_DIR/nps/config/nodelist.txt
    for ((i=2; i<=$var_qtd_hosts; i++)); do echo "10.0.0."$i" node"$i" mininet eth1 10.0.0.1 6633" >> $BUILD_DIR/nps/config/nodelist.txt; done
    cat $BUILD_DIR/nps/config/nodelist.txt

    printf '\e[1;33m%-6s%s\e[m\n' 'Creating clusternode MininetScripts directory in ' $BUILD_DIR/nps/clusternode/MininetScripts/
    mkdir -p $BUILD_DIR/nps/clusternode/MininetScripts/

# AINDA NÃO TERMINADO

}

function install_app_maxinet() {
    printf '\n\e[1;32m%-6s\e[m\n' '-- Installing MaxiNet ...'
    printf '\n\e[1;33m%-6s\e[m\n' 'Resolving requirements'
    sudo -H pip install --upgrade --force-reinstall -U Pyro4
    printf '\e[1;33m%-6s\e[m\n' 'Erasing all previous configuration.'
    rm -rf $BUILD_DIR/maxinet
    git clone git://github.com/MaxiNet/MaxiNet.git $BUILD_DIR/MaxiNet
    cd $BUILD_DIR/MaxiNet
    git checkout v1.2
    make install
    cp $BUILD_DIR/MaxiNet/share/MaxiNet-cfg-sample /etc/MaxiNet.cfg
    printf '\e[1;33m%-6s\e[m\n' 'Configuring MaxiNet config file.'
    sed -i -- 's/password = HalloWelt/password = abc123/g' /etc/MaxiNet.cfg
    sed -i -- 's/controller = 192.168.123.1:6633/controller = node1:6633/g' /etc/MaxiNet.cfg
    sed -i -- 's/logLevel = INFO/logLevel = ERROR/g' /etc/MaxiNet.cfg
    sed -i -- 's/sshuser = root/sshuser = mininet/g' /etc/MaxiNet.cfg
    sed -i -- 's/usesudo = False/usesudo = True/g' /etc/MaxiNet.cfg
    sed -i -- 's/ip = 192.168.123.1/ip = node1/g' /etc/MaxiNet.cfg
    sed -i -- 19,'$d' /etc/MaxiNet.cfg
    for ((i=2; i<=$var_qtd_hosts; i++)); do echo '[node'$i$'] \nip = node'$i$' \nshare = 1\n' >> /etc/MaxiNet.cfg; done
    cat /etc/MaxiNet.cfg    
}

# set up build directory
BUILD_DIR=/home/mininet
FACTORIAL2K_DIR=$BUILD_DIR/factorial2k

welcome;
qtd_hosts;
install_packages;
update_SO_install_packages;
network_configuration;
user;
hosts_file;
ssh_file;
node_file;
if [ "$var_app_mininet" = "" ] || [ "$var_app_mininet" = "Y" ] || [ "$var_app_mininet" = "y" ] ; then
    install_app_mininet;
fi
if [ "$var_app_nps" = "" ] || [ "$var_app_nps" = "Y" ] || [ "$var_app_nps" = "y" ] ; then
    install_app_nps;
fi
if [ "$var_app_maxinet" = "" ] || [ "$var_app_maxinet" = "Y" ] || [ "$var_app_maxinet" = "y" ] ; then
    install_app_maxinet;
fi

printf '\n\e[1;32m%-6s\e[m\n' ' ------------ FINISHED ------------ '
printf '\n%s\n' 'Please, look for any trouble during installation process.' \
                'You requested installation of the following applications:' \
	        
if [ "$var_app_mininet" = "" ] || [ "$var_app_mininet" = "Y" ] || [ "$var_app_mininet" = "y" ] ; then
    printf '%s\n%s\n' ' - Mininet 2.2.2' ' - Mininet Cluster'
fi
if [ "$var_app_nps" = "" ] || [ "$var_app_nps" = "Y" ] || [ "$var_app_nps" = "y" ] ; then
    printf '%s\n' ' - Network Prototype Simulator (NPS)'
fi
if [ "$var_app_maxinet" = "" ] || [ "$var_app_maxinet" = "Y" ] || [ "$var_app_maxinet" = "y" ] ; then
    printf '%s\n' ' - MaxiNet 1.2'
fi

printf '\n%s\n' 'All programs were installed in '$BUILD_DIR
printf '\n\e[1;32m%-6s\n%s\n%s\e[m\n' 'From now you need to use only the username and password below:' \
                                    'USERNAME: mininet' \
                                    'PASSWORD: abc123'
printf '\n%s%d%s\n%s%s%s\n%s\n' 'Please, shutdown the VM, make ' $((var_qtd_hosts-1)) ' clones, start all of them, ' \
                                'execute nodes configuration script stored in ' $FACTORIAL2K_DIR '/nodes/ (node1.sh, node2.sh ...) ' \
                                'at the correspondent VM (clone) to finish network configuration.'
