#!/bin/bash

qtd_container=100
for (( i=4; i <= $qtd_container; ++i ))
do
	lxc-copy -n my-container -N my-container$i
done
lxc-ls
