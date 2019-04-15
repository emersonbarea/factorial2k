#!/bin/bash

lxc-start my-container

qtd_container=100
for (( i=2; i <= $qtd_container; ++i ))
do
	lxc-start my-container$i
done
lxc-ls
