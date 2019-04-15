dataFrame <- read.csv('/home/tocha/clusterNode-4_FatTree_MininetCluster_RemoteGRELink_pod-8_data.log')
boxplot(timeb~description,data=dataFrame, main="Tempo por Função", xlab="Função", ylab="Tempo [s]") 
#ggplot(dataFrame, aes(x=description, y=timeb)) + geom_boxplot()



df <- read.csv('/home/tocha/clusterNode-4_FatTree_MininetCluster_RemoteGRELink_pod-8_data.log')

df$instancias <- factor(df$description, levels = c("topology","controller","host","edgeSwitch","aggregateSwitch","coreSwitch","linkHostEdge","linkEdgeAggregate","linkAggregateCore-local-local","start"))

p <- ggplot(df, aes(x = instancias, y = timeb)) +  geom_boxplot()

p <- p + scale_x_discrete(name="Função") + scale_y_continuous(name="Tempo [s]")

p + theme(text = element_text(size=25.5))

p