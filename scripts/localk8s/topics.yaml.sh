#!/bin/bash
SCRIPTLOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TOPICS="bluewater-container
bluewater-ship
bluewater-problem
orders
order-commands
rejected-orders
allocated-orders
errors
containers
reefer-telemetry
container-anomaly-retry
container-anomaly-dead"

# Note: topics must also be valid k8s resource names, otherwise they will
# need to be converted (eg. lowercased) and specified via the 'topicName'
# spec in the KafkaTopic CR.
echo -n "" > $SCRIPTLOC/topics.yaml
for TOPIC in $TOPICS; do
    cat $SCRIPTLOC/topics.yaml.template | sed -e"s#  name: \$#  name: ${TOPIC}#" >> topics.yaml
    echo "---" >> $SCRIPTLOC/topics.yaml
done
