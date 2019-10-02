#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33maddContainer.sh \e[0m"

## Variables

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`


# Read arguments
if [[ $# -ne 2 ]];then
    echo "Not enough arguments have been provided for the producer. Using the defaults:"
    echo "- Kafka environment --> LOCAL"
    echo "- Container ID --> C01"
    kcenv=LOCAL
    cid="C01"
else
    echo "Producer values:"
    echo "- Kafka environment --> $1"
    echo "- Container ID --> $2"
    kcenv=$1
    cid=$2
fi

# Set environment variables
source ${MAIN_DIR}/scripts/setenv.sh $kcenv

# Run the container producer
# We are running the ContainerProducer.py python script into a python enabled container
# Attached to the same docker_default docker network as the other components
# We also pass to the python producer the Container ID we want to produce
docker run  -e KAFKA_BROKERS=$KAFKA_BROKERS \
            -e KAFKA_APIKEY=$KAFKA_APIKEY \
            -e KAFKA_ENV=$KAFKA_ENV \
            -v ${MAIN_DIR}/itg-tests:/home \
            --network=docker_default \
            --rm \
            -ti ibmcase/python bash \
            -c "cd /home/ContainersPython && export PYTHONPATH=/home && python ContainerProducer.py $cid"
