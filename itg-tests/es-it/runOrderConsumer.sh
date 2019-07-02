#!/bin/bash
echo "#################################"
echo "## Event Sourcing              ##"
echo "What happen to order ---- test"


if [[ $# -ne 2 ]];then
    echo "Usage: Need two arguments:  runOrderConsumer.sh [LOCAL | MINIKUBE | IBMCLOUD | ICP] anOrderID"
    exit
else
    kcenv=$1
    oid=$2
fi
source ../../scripts/setenv.sh $kcenv 
docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY -e KAFKA_ENV=$KAFKA_ENV  -v $(pwd)/..:/home --network=docker_default -ti ibmcase/python bash -c "cd /home/es-it && export PYTHONPATH=/home && python ../OrdersPython/OrderConsumer.py $oid"