#!/usr/bin/env bash

# Script we are executing
echo -e "\e[32m@@@ Excuting script: \e[1;33mCreateTopics.sh \e[0m"

# Help
if [[ $# -ne 1 ]];then
 echo "Usage smokeTest [LOCAL | MINIKUBE | IBMCLOUD | ICP]"
 exit 1
fi

### Functions

createTopic(){
    if [ ! -z "$1" ]
    then
        if [[ $KAFKA_ENV == "LOCAL"  ]]
        then
            docker exec -ti docker_kafka1_1  /bin/bash -c "$KAFKA_INTERNAL_PATH/bin/kafka-topics.sh --create  --zookeeper zookeeper1:2181 --replication-factor 1 --partitions 1 --topic $1"
        else
            kubectl exec  -ti $POD_NAME  -n $KC_NAMESPACE -- kafka-topics.sh --create  --zookeeper kafkabitmani-zookeeper:2181 --replication-factor 1 --partitions 1 --topic $1
        fi
    else
        echo -e "\e[31m[ERROR] - Topic $1 is incorrect.\e[0m"
    fi
}

### Variables

ALL="allocated-orders
bluewater-container
bluewater-problem
bluewater-ship
containers
order-commands
container-anomaly-retry
container-anomaly-dead
errors
orders
reefer-telemetry
rejected-orders"

### Script

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

# Read environment variables
source ${MAIN_DIR}/scripts/setenv.sh $1

kafka=$(docker ps -a | grep docker_kafka | awk '{print $NF}')
if [ -z "$kafka" ]
then
    echo "\e[31m [ERROR] - Kafka docker is not running.\e[0m"
    exit 1
fi

# get current topics
if [[ $KAFKA_ENV == "LOCAL"  ]]
then
    # The kafka-topics.sh --list command returns a list of the Kafka topics already created. However, this list comes with an ASCII Control Code carriage return (^M, ctrl+v or '\r')
    # which, despite being a non-printable character, is taken into account by the uniq command to remove duplicates later on.
    # This character can be removed by executing the dos2unix command. However, this utility might not be available in every laptop.
    # Therefore we are going to use tr -d '\r' instead
    ALREADY_CREATED=$(docker exec  -ti $kafka /bin/bash -c "$KAFKA_INTERNAL_PATH/bin/kafka-topics.sh --list --zookeeper zookeeper1:2181" | tr -d '\r')
    # There are other alternative such as sed. Using sed 's/.$//g' we are removing the last character of every line which should be that carriage return character.
    # However, if for any reason there is no such character we would have a bug.
    # Other option, that I could not get to work, is the one described here: https://www.cyberciti.biz/faq/unix-linux-sed-ascii-control-codes-nonprintable/

else
    export POD_NAME=$(kubectl get pods --namespace $KC_NAMESPACE -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=kafkabitmani,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
    # The sed 's/'$(echo "\015")'//g' is to emulate the dos2unix command in order to remove the ^M character returned at the end of each line by the kafka-topics.sh script
    ALREADY_CREATED=$(kubectl exec  -ti $POD_NAME  -n $KC_NAMESPACE -- kafka-topics.sh --list --zookeeper kafkabitmani-zookeeper:2181 | tr -d '\r')
fi

echo "These are the topics already created:"
echo "${ALREADY_CREATED}"
echo

# Calculate topics to be created:
# 1. Append all topics with topics already created
ALL_AND_ALREADY_CREATED="${ALL}
${ALREADY_CREATED}"

# 2. Select non-duplicate topics from the list above
TO_BE_CREATED=$(echo "${ALL_AND_ALREADY_CREATED}" | sort | uniq -u)

echo "These are the topics to be created:"
echo "${TO_BE_CREATED}"
echo

# Create non-existing topics
if [ -z "${TO_BE_CREATED}" ]
then
    echo "No new topics to be created"
else
    for topic in ${TO_BE_CREATED}
    do
        createTopic "${topic}"
    done
    echo "All topics created"
fi

# Script we are executing
echo -e " \e[32m@@@ End script: \e[1;33mCreateTopics.sh \e[0m"
