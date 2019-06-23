#!/bin/bash
export POD_NAME=$(kubectl get pods --namespace greencompute -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=kafkabitmani,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
# get current topics
kubectl exec  -ti $POD_NAME  -n greencompute -- kafka-topics.sh --list --zookeeper kafkabitmani-zookeeper:2181 > topics
createTopic(){
    bc=$(tail -n+2 topics| grep  $1)
    echo $bc
    if [ -z "$bc" ]
    then
        echo "create " $1
        kubectl exec  -ti $POD_NAME  -n greencompute -- kafka-topics.sh --create  --zookeeper kafkabitmani-zookeeper:2181 --replication-factor 1 --partitions 1 --topic $1
    else
        echo $1 " topic already created"
    fi
}

createTopic "bluewaterContainer" 
createTopic "bluewaterShip" 
createTopic "bluewaterProblem" 
createTopic "orders" 
createTopic "errors" 
createTopic "containers" 
createTopic "containerMetrics" 
createTopic "rejected-orders"
createTopic "allocated-orders"
rm topics
