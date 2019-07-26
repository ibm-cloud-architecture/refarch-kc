#!/bin/bash
if [[ $PWD != */refarch-kc ]]; then
 echo "Run stop.sh from refarch-kc"
 exit 1
fi


source ../../scripts/setenv.sh LOCAL
cd docker
docker-compose -f kc-solution-compose.yml  down
sleep 15
docker-compose -f backbone-compose.yml  down