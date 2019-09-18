#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mrunOrderConsumer.sh \e[0m"

## Variables

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

# Read arguments
if [[ $# -ne 2 ]];then
    echo "Not enough arguments have been provided for the order consumer. Using the defaults:"
    echo "- Kafka environment --> LOCAL"
    echo "- Order ID --> o_1"
    kcenv=LOCAL
    oid="o_1"
else
    echo "Consumer values:"
    echo "- Kafka environment --> $1"
    echo "- Order ID --> $2"
    kcenv=$1
    oid=$2
fi

# Set environment variables
source ${MAIN_DIR}/scripts/setenv.sh $kcenv

# Random name for the Docker container
UPPER_LIMIT=9999
NAME=$(($RANDOM%UPPER_LIMIT))

# Run the container consumer
# We are running the OrderConsumer.py python script into a python enabled container
# Attached to the same docker_default docker network as the other components
# We also pass to the python consumer the Order ID we want it to consume
docker run  -e KAFKA_BROKERS=$KAFKA_BROKERS \
            -e KAFKA_APIKEY=$KAFKA_APIKEY \
            -e KAFKA_ENV=$KAFKA_ENV  \
            -v ${MAIN_DIR}/itg-tests:/home \
            --name $NAME \
            -ti ibmcase/python bash \
            -c "cd /home/OrdersPython && export PYTHONPATH=/home && python OrderConsumer.py $oid"

# Remove the container
docker rm $NAME > /dev/null