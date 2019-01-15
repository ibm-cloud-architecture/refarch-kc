#!/bin/bash
kafka=$(docker ps -a | grep docker_kafka | awk '{print $NF}')
if [ -z "$kafka" ]
then
  echo "Kafka docker is not running"
fi
echo $kafka
# get current topics
docker exec  -ti $kafka /bin/bash -c "kafka-topics --list --zookeeper zookeeper1:2181" > topics
createTopic(){
    bc=$(tail -n+2 $2 | grep  $1)
    echo $bc
    if [ -z "$bc" ]
    then
        echo "create " $1
        docker exec -ti docker_kafka1_1  /bin/bash -c "kafka-topics --create  --zookeeper zookeeper1:2181 --replication-factor 1 --partitions 1 --topic $1"
    else 
        echo $1 " topic already created"
    fi
}

createTopic "bluewaterContainer" topics
createTopic "bluewaterShip" topics
createTopic "bluewaterProblem" topics
createTopic "orders" topics
