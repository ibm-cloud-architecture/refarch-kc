#!/bin/bash

SCRIPT_DIR=$(dirname $0)

if [[ $PWD = */scripts ]]; then
 cd ..
fi

if [[ $# -eq 0 ]];then
  toLaunch="SOLUTION"
else
  toLaunch=$1
fi


SETENV="./scripts/setenv.sh"

if [[ ! -f "$SETENV"  ]]
then
    echo "\e[31m the file setenv.sh not found under scripts folder. Use the setenv.sh.tmpl template\e[0m"
    exit -1
fi

source $SETENV LOCAL

cd docker

if [ "$toLaunch" == "SOLUTION" ] || [ "$toLaunch" == "BACKEND" ]
then
    kafka=$(docker-compose -f backbone-compose.yml ps | grep kafka | grep Up | awk '{ print $1}')
    if [[ $kafka != "docker_kafka1_1" ]]
    then
        echo -e " \e[32m@@@ Start back end\e[39m"
        rm -r kafka1 zookeeper1
        docker-compose -f backbone-compose.yml up 2>backend.logs &
        sleep 15
        cd ..
        ./scripts/createTopics.sh LOCAL
    else
        echo -e "\e[32m@@@ Back end services are running\e[39m"
        docker exec  -ti docker_kafka1_1 /bin/bash -c "/opt/kafka/bin/kafka-topics.sh --list --zookeeper zookeeper1:2181"
    fi
fi


if [[ "$toLaunch" == "SOLUTION" ]]
then
    solution=$(docker-compose -f kc-solution-compose.yml ps | grep simulator | grep Up | awk '{ print $1}')
    if [[ $solution != "docker_simulator_1" ]]
    then
        echo -e "\e[32m@@@ Start all solution microservices\e[39m"
        docker-compose -f kc-solution-compose.yml up 2>&1 1>solution.logs &
    else
        echo -e "\e[32m@@@ all solution microservices are running\e[39m"
    fi
fi