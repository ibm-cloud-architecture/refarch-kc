#!/bin/bash
# --network=docker_default
docker run  -e KAFKA_BROKERS=$KAFKA_BROKERS -e KAFKA_APIKEY=$KAFKA_APIKEY -e KAFKA_ENV=$KAFKA_ENV -v $(pwd):/home  -ti ibmcase/pythontools bash
