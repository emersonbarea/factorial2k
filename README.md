You need a basic and fresh Ubuntu 18.04.1 Server LTS (Bionic Beaver) installation.

```
git clone https://github.com/emersonbarea/factorial2k.git

chmod 755 factorial2k/install.sh

cd factorial2k

sudo ./install.sh
```
This will update/upgrade Ubuntu, install (Mininet 2.2.2, Network Prototype Simulator (NPS) and MaxiNet) and configure (network, user, hostname and SSH keys) all you need. You only need to tell how many nodes your cluster has.

At the end of the script will be created other scripts to configure each cluster node. You only have to run each script on the corresponding node.
