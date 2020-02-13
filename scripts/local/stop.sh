#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mstop.sh \e[0m"

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

SETENV="${MAIN_DIR}/scripts/setenv.sh"

# Get what option the user wants to stop
if [[ $# -eq 0 ]];then
    echo -e "\e[31m [ERROR] - Specify which option to stop: stop.sh [ BACKEND | SOLUTION | DEV ]\e[0m"
    exit 1
else
    # Read the option to stop
    toStop=$1
    
    # Validate the option to stop
    if [[ "${toStop}" != "BACKEND" ]] && [[ "${toStop}" != "SOLUTION" ]] && [[ "${toStop}" != "DEV" ]] && [[ "${toStop}" != "TELEMETRY" ]]
    then
        echo -e "\e[31m [ERROR] - Specify an appropriate option to stop: stop.sh [ BACKEND | SOLUTION | DEV | TELEMETRY ]\e[0m"
        exit 1
    fi

    # Read environment variables
    source $SETENV LOCAL

    case ${toStop} in
    BACKEND)
        # Stop backend components
        echo -e " \e[32m@@@ Stop backend components\e[39m"
        docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml down
        ;;
    SOLUTION)
        # Stop solution components
        echo -e " \e[32m@@@ Stop solution components\e[39m"
        docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml down
        ;;
    DEV)
        # Stop development components
        echo -e " \e[32m@@@ Stop development components\e[39m"
        docker-compose -f ${MAIN_DIR}/docker/kc-development-compose.yml down
        ;;
    TELEMETRY)
        # Stop anomaly detection components
        echo -e " \e[32m@@@ Stop anomaly detection components\e[39m"
        docker-compose -f ${MAIN_DIR}/docker/kc-development-compose-anomaly.yml down
        ;;
    *)
        echo -e "\e[31m [ERROR] - Specify an appropriate option to stop: stop.sh [ BACKEND | SOLUTION | DEV | TELEMETRY ]\e[0m"
        exit 1
        ;;
    esac
fi

# Script we are executing
echo -e " \e[32m@@@ End script: \e[1;33mstop.sh \e[0m"