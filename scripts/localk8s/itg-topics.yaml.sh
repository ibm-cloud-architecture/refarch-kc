#!/bin/bash
SCRIPTLOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Extract list of topics from kafka-topics ConfigMap resource (assumes
# keys end with the string 'Topic')
TOPICS=`cat $SCRIPTLOC/itg-kafka-topics-configmap.yaml | grep 'Topic:' | cut -d':' -f2`

# Note: topics must also be valid k8s resource names, otherwise they will
# need to be converted (eg. lowercased) and specified via the 'topicName'
# spec in the KafkaTopic CR.
echo -n "" > $SCRIPTLOC/itg-topics.yaml
for TOPIC in $TOPICS; do
    cat $SCRIPTLOC/topics.yaml.template | sed -e"s#  name: \$#  name: ${TOPIC}#" >> itg-topics.yaml
    echo "---" >> $SCRIPTLOC/itg-topics.yaml
done
