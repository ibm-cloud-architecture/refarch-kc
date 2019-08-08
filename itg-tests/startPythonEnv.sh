#!/bin/bash
# --network=docker_default
if [[ $# -eq 0 ]];then
  echo "Usage IBMCLOUD | ICP | MINIKUBE | LOCAL"
  exit 1
fi
source ../scripts/setenv.sh $1

network=docker_default 
if [[ $KAFKA_ENV == "MINIKUBE" ]]
then
   network=none 
fi

echo "docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY \
-e KAFKA_ENV=$KAFKA_ENV -e CA_LOCATION=$CA_LOCATION \
 --network=$network -v $(pwd):/home  -it ibmcase/python bash "

docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY \
-e KAFKA_ENV=$KAFKA_ENV -e CA_LOCATION=$CA_LOCATION \
 -e ORDER_CMD_MS=$ORDER_CMD_MS -e ORDER_QUERY_MS=$ORDER_QUERY_MS \
 --network=$network -v $(pwd):/home  -it ibmcase/python bash 
