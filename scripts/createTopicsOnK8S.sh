echo "Create topics for the Reefer container solutions on event streams on premise"
ns="event-streams"
zooksvc="event-streams-ibm-es-zookeeper-fixed-ip-svc-0"

echo "Kafka pod name is..."
kpof=$(kubectl get pods -n $ns| grep kafka | awk '{print $1;}'| head -1)
if [[ -z $kpof ]]
then
  echo "Kafka not installed on your kubernetes cluster"
  exit
else
  echo "Use this pod: $kpof"
fi

echo "Zookeeper svc name is..."
zooksvc=$(kubectl get svc -n $ns | grep zoo | awk '{print $1;}' | head -1)
if [[ -z $zooksvc ]]
then
  echo "Zookeeper not installed on your kubernetes cluster"
  exit
else
 echo "Use this zookeeper: $zooksvc"
fi

echo "Get topic list from kafka pod"
kubectl exec  -n $ns  -ti $kpof -- bash -c "/opt/kafka/bin/kafka-topics.sh --list --zookeeper $zooksvc:2181" > topics

createTopic(){
    bc=$(tail -n+2 topics | grep  $1)
    echo $bc
    if [ -z "$bc" ]
    then
        echo "create " $1
        kubectl exec -n $ns  -ti $kpof   -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper $zooksvc:2181 --replication-factor 1 --partitions 1 --topic $1"
    else
        echo $1 " topic already created"
    fi
}

createTopic "bluewater-container"
createTopic "bluewater-ship"
createTopic "bluewater-problem"
createTopic "orders"
createTopic "rejected-orders"
createTopic "allocated-orders"
createTopic "errors"
createTopic "containers"
createTopic "container-anomaly-retry"
createTopic "container-anomaly-dead"
createTopic "reefer-telemetry"
createTopic "order-commands"

rm topics
