echo "Create topics for the KC solutions on your local kafka"
ns="browncompute"

echo "Kafka pod name is..."
kpof=$(kubectl get pods -n browncompute| grep kafka | awk '{print $1}')
if [ -z $kpof ]
then
  echo "Kafka not installed locally on your kubernetes cluster"
else 
  echo $kpof
fi

echo "Get topic list"
docker exec  -ti $kafka /bin/bash -c "kafka-topics --list --zookeeper zookeeper1:2181" > topics

createTopic(){
    bc=$(tail -n+2 $2 | grep  $1)
    echo $bc
    if [ -z "$bc" ]
    then
        echo "create " $1
        kubectl exec  -ti $kpof -n $ns   -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper gc-client-zookeeper-svc.greencompute.svc.cluster.local:2181 --replication-factor 1 --partitions 1 --topic $1"
  else 
        echo $1 " topic already created"
    fi
}
createTopic "bluewaterContainer" topics
createTopic "bluewaterShip" topics
createTopic "bluewaterProblem" topics
createTopic "orders" topics
createTopic "errors" topics
createTopic "containers" topics
createTopic "containerMetrics" topics