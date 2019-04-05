#!/bin/bash
# --network=docker_default
if [[ $# -eq 0 ]];then
  echo "Usage IBMCLOUD | ICP | LOCAL"
  exit 1
fi
. ../scripts/setenv.sh

docker run  -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY -e KAFKA_ENV=$KAFKA_ENV -e CA_LOCATION=$CA_LOCATION -v $(pwd):/home  -ti ibmcase/pythontools bash
