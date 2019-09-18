#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mstop.sh \e[0m"


# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

# Read environment variables
source ${MAIN_DIR}/scripts/setenv.sh LOCAL

# Stop the soltion components (i.e. microservices)
echo "Stopping the solution components"
docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml  down

sleep 15

# Stop the backbone components
echo "Stopping the backbone components"
docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml  down

# Script we are executing
echo -e " \e[32m@@@ End script: \e[1;33mstop.sh \e[0m"