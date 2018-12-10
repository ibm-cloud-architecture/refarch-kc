echo "Create topics for the KC solutions on your local kafka"
ns="greencompute"

echo "Kafka pod name is..."
kpof=$(kubectl get pods -n greencompute| grep kafka | awk '{print $1}')
if [ -z $kpof ]
then
  echo "Kafka not installed locally on your kubernetes cluster"
else 
  echo $kpof
fi

echo "Get topic list"
topics=$(kubectl exec  -ti $kpof -n $ns  -- bash -c "/opt/kafka/bin/kafka-topics.sh --list --zookeeper gc-client-zookeeper-svc.greencompute.svc.cluster.local:2181")

bc=$(echo $topics | grep  "bluewaterContainer")
echo $bc
if [ -z $bc ]
then
  echo "create bluewaterContainer"
else 
  echo "bluewaterContainer topic already created"
fi

bc=$(echo $topics | grep  "bluewaterShip")
echo $bc
if [ -z $bc ]
then
  echo "create bluewaterShip"
  kubectl exec  -ti $kpof -n $ns   -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper gc-client-zookeeper-svc.greencompute.svc.cluster.local:2181 --replication-factor 1 --partitions 1 --topic bluewaterShip"
else 
  echo "bluewaterShip topic already created"
fi

bc=$(echo $topics | grep  "bluewaterProblem")
echo $bc
if [ -z $bc ]
then
  echo "create bluewaterProblem"
  kubectl exec  -ti $kpof -n $ns   -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper gc-client-zookeeper-svc.greencompute.svc.cluster.local:2181 --replication-factor 1 --partitions 1 --topic bluewaterProblem"
else 
  echo "bluewaterProblem topic already created"
fi