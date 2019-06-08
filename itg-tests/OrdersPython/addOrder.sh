#!/bin/bash
if [[ $# -eq 0 ]];then
    kcenv=LOCAL
else
    kcenv=$1
fi
source ../../scripts/setenv.sh $kcenv
# 
docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY -e KAFKA_ENV=$KAFKA_ENV -v $(pwd)/..:/home --network=docker_default -ti ibmcase/python bash -c "cd /home/OrdersPython && export PYTHONPATH=/home && python OrderProducer.py $2"