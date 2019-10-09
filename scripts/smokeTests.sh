#!/bin/bash

echo "##################################################"
echo "Smoke test the backbone and solution microservices"
echo "##################################################"

if [[ $PWD != */refarch-kc ]]; then
 echo "Run smoke tests from refarch-kc folder"
 exit 1
fi

if [[ $# -ne 1 ]];then
 echo "Usage smokeTest [LOCAL | IBMCLOUD | ICP]"
 exit 1
fi

echo " ====== Local smoke tests to validate all components"
source ./scripts/setenv.sh $1


echo ">>>> 1- Verify kafka runs"

if [[ $KAFKA_ENV == "LOCAL" ]]
then
    docker=$(docker version | grep Server )
    if [[ -z "$docker" ]]
    then
        echo "You need to start docker engine first"
        exit 1
    else
        echo "Docker engine runs... [Good]"
    fi
    rep=$(curl http://$KAFKA_BROKERS 2>&1 | grep reply)
    echo $rep
    if [[ -z "$rep" ]] 
    then
        echo "kafka and zookeeper are not running, let start them and wait 30 seconds"
        cd docker 
        docker-compose -f backbone-compose.yml up 2>backend.logs &
        sleep 30
        cd ..
    else
        echo "Kafka and zookeeper run... [Good]"
    fi
else 
    kafka=$(echo $KAFKA_BROKERS | cut -d',' -f1)
    echo "Test remote kafka: $kafka"
    rep=$(curl http://$kafka 2>&1 | grep reply)
    echo $rep
    if [[ -z "$rep" ]] 
    then
        echo "Kafka remote unreachable ... verify $KAFKA_BROKERS"
        exit 1
    else
        echo "Kafka remote accessible... [Good]"
    fi
fi


echo ">>>> 2- Verify kafka topics"
if [[ $KAFKA_ENV == "LOCAL" ]]
then
    kafka=$(docker ps -a | grep docker_kafka | awk '{print $NF}')
    docker exec  -ti $kafka /bin/bash -c "$KAFKA_INTERNAL_PATH/bin/kafka-topics.sh --list --zookeeper zookeeper1:2181" > topics
else
    topics=$(curl -s -H "X-Auth-Token:$KAFKA_APIKEY" $KAFKA_ADMIN_URL/admin/topics)
    echo $topics
fi

npTopics=$(wc -l topics | awk '{print $1}')
if [[ $npTopics -ge $NB_TOPICS ]]
then
    echo "Kafka topics... [Good]"
else
    echo "Not enough topics, let runs the creation"
    ./scripts/createLocalTopics.sh $1
fi


echo ">>>> 3- Verify the services run"
if [[ $KAFKA_ENV == "LOCAL" ]]
then
    cd docker
    solution=$(docker-compose -f kc-solution-compose.yml ps | grep simulator | grep Up | awk '{ print $1}')
    if [[ $solution != "docker_simulator_1" ]]
    then
        echo "Solution microservices are not running"
        echo "   @@@ Start all solution microservices"
        docker-compose -f kc-solution-compose.yml up 2>&1 1>solution.logs &
    else
        echo "   @@@ all solution microservices are running"
    fi
    cd ..
fi


echo ">>>> 4- Perform tests on each components"

# Arguments are: service name, relative path to the repository, script to call from the repository, name of the attributes used as key
smokeTest(){
  echo "#########################"
  echo "Smoke test for $1 in ../$2
  "
  
  results=$(../$2/scripts/$3 $4 $5 2>&1 | grep $4)
  echo $results
  if [[ -z "$results" ]]
  then
      echo "Test failed or is not perfect for $1"
  else
      echo "Smoke test for $1 works!: $results"
  fi
}

# Create an order for GoodManuf
rep=$(curl http://$ORDER_CMD_MS/orders/byManuf/GoodManuf 2>&1 | grep GoodManuf)
current=$(pwd)
if [[ -z "$rep" ]]
then
  echo "Add an order from Good manuf for testing"
  
  cd  ../refarch-kc-order-ms/order-command-ms/scripts/
  ./createOrder.sh $ORDER_CMD_MS
  cd $current
  echo " "
fi


smokeTest fleetms refarch-kc-ms/fleet-ms testGetFleetNames.sh $FLEET_MS KC-NorthAtlantic
smokeTest voyagesms refarch-kc-ms/voyages-ms testGetVoyages.sh $VOYAGE_MS
smokeTest ordercommandms refarch-kc-order-ms/order-command-ms testGetOrders.sh $ORDER_CMD_MS
smokeTest orderqueryms refarch-kc-order-ms/order-query-ms testGetOrdersGoodManuf.sh $ORDER_QUERY_MS
