#!/bin/bash


if [[ $# -ne 1 ]];then
 echo "Usage smokeTest [LOCAL | MINIKUBE | IBMCLOUD | ICP]"
 exit 1
fi

source ./scripts/setenv.sh $1

kafka=$(docker ps -a | grep docker_kafka | awk '{print $NF}')
if [ -z "$kafka" ]
then
  echo "Kafka docker is not running"
  exit 1
fi


# get current topics
if [[ $KAFKA_ENV == "LOCAL"  ]]
then
    docker exec  -ti $kafka /bin/bash -c "$KAFKA_INTERNAL_PATH/bin/kafka-topics.sh --list --zookeeper zookeeper1:2181" > topics
else
    export POD_NAME=$(kubectl get pods --namespace $KC_NAMESPACE -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=kafkabitmani,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    # get current topics
    kubectl exec  -ti $POD_NAME  -n $KC_NAMESPACE -- kafka-topics.sh --list --zookeeper kafkabitmani-zookeeper:2181 > topics
fi

createTopic(){
    bc=$(tail -n+2 topics| grep  $1)
    echo $bc
    if [ -z "$bc" ]
    then
        echo "create " $1
        if [[ $KAFKA_ENV == "LOCAL"  ]]
        then
            docker exec -ti docker_kafka1_1  /bin/bash -c "$KAFKA_INTERNAL_PATH/bin/kafka-topics.sh --create  --zookeeper zookeeper1:2181 --replication-factor 1 --partitions 1 --topic $1"
        else
            kubectl exec  -ti $POD_NAME  -n $KC_NAMESPACE -- kafka-topics.sh --create  --zookeeper kafkabitmani-zookeeper:2181 --replication-factor 1 --partitions 1 --topic $1
        fi
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




