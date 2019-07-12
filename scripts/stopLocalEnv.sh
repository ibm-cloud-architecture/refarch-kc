#!/bin/bash
if [[ $PWD != */refarch-kc ]]; then
 echo "Run stopLocalEnv from refarch-kc"
 exit 1
fi

if [[ $# -ne 1 ]];then
 echo "Usage stopLocalEnv [ LOCAL | MINIKUBE ]"
 exit 1
fi

if [[ $1 == "LOCAL" ]]
then
  cd docker
  docker-compose -f kc-solution-compose.yml down
  sleep 15
  docker-compose -f backbone-compose.yml down
fi