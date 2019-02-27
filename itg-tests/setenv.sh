#!/bin/bash

if [[ $PWD = */scripts ]]; then
 cd ..
fi
export KAFKA_BROKERS=localhost:9092
export ORDER_CMD_MS=localhost:10080
