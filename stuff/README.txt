mininet-2.2.2-py2.7.egg

	este arquivo é o egg (pacote) Python do Mininet. Dentro dele tem toda estrutura de arquivos Mininet chamados para ser executado pelo
	/usr/local/bin/mn. Alguns arquivos (mn e cluster.py) estão com "print" para mostrar quando passa em cada método.
	Para acessar o conteúdo do arquivo egg, precisar unzip: unzip mininet-2.2.2-py2.7.egg. Dessa forma será criado a estrutura apontada abaixo:

	cd /usr/local/lib/python2.7/dist-packages/
	mkdir teste
	cd teste
	cp ~/mininet-2.2.2-py2.7.egg .
	unzip mininet-2.2.2-py2.7.egg
		EGG-INFO
		mininet
	ls EGG-INFO/scripts/mn			# mn chamado pelo /usr/local/bin/mn
	ls mininet/examples/cluster.py		# cluster.py chamado dentro do mn (import)

Mininet.txt
	tem um exemplo de output do comando 
		mn --topo tree,2,2 --cluster localhost,node2 --placement random
	e também do comando
		mn --topo tree,2,2 --cluster localhost,node2
	nessa ordem.

O arquivo mininet-2.2.2-py2.7.egg deve ser colocado em /usr/local/lib/python2.7/dist-packages/
Se fizer alguma mudança no egg, deverá "zipar" ele novamente com o seguinte procedimento:
	cd /usr/local/lib/python2.7/dist-packages/teste
	zip -r /usr/local/lib/python2.7/dist-packages/mininet-2.2.2-py2.7.egg *
