#!/bin/bash
if [[ $# -eq 2 ]];then
    kcenv=LOCAL
    cid="C02"
else
    kcenv=$1
    cid=$2
fi
source ../../scripts/setenv.sh $kcenv 
docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY -e KAFKA_ENV=$KAFKA_ENV -v $(pwd)/..:/home --network=docker_default -ti ibmcase/python bash -c "cd /home/ContainersPython && export PYTHONPATH=/home && python ConsumeContainers.py $cid"