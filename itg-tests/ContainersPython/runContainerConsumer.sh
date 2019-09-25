#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mrunContainerConsumer.sh \e[0m"

## Variables

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

# Read arguments
if [[ $# -ne 2 ]];then
    echo "Not enough arguments have been provided for the consumer. Using the defaults:"
    echo "- Kafka environment --> LOCAL"
    echo "- Container ID --> c_1"
    kcenv=LOCAL
    cid="c_1"
else
    echo "Consumer values:"
    echo "- Kafka environment --> $1"
    echo "- Container ID --> $2"
    kcenv=$1
    cid=$2
fi

# Check if the ibmcase/python docker image exists
EXISTS="$(docker images | grep ibmcase/python)"
if [ -z "${EXISTS}" ]
then
    echo -e "The ibmcase/python docker image does not exist. Creating such image..."
    docker build -f ${MAIN_DIR}/docker/docker-python-tools -t ibmcase/python ${MAIN_DIR}/docker
fi

# Set environment variables
source ${MAIN_DIR}/scripts/setenv.sh $kcenv

# Run the container consumer
# We are running the ConsumeContainer.py python script into a python enabled container
# Attached to the same docker_default docker network as the other components
# We also pass to the python consumer the Container ID we want it to poll for
docker run  -e KAFKA_BROKERS=$KAFKA_BROKERS \
            -e KAFKA_APIKEY=$KAFKA_APIKEY \
            -e KAFKA_ENV=$KAFKA_ENV \
            -v ${MAIN_DIR}/itg-tests:/home \
            --network=docker_default \
            --rm \
            -ti ibmcase/python bash \
            -c "cd /home/ContainersPython && export PYTHONPATH=/home && python ConsumeContainers.py $cid"