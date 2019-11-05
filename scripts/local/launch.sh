#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mlaunch.sh \e[0m"

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

SETENV="${MAIN_DIR}/scripts/setenv.sh"

# Checking if the setenv.sh file exist for reading environment variables
if [[ ! -f "$SETENV"  ]]
then
    echo -e "\e[31m [ERROR] - The file setenv.sh not found under the scripts folder (${MAIN_DIR}/scripts) - Use the setenv.sh.tmpl template to create your setenv.sh file.\e[0m"
    exit 1
fi

# Get what option the user wants to launch
if [[ $# -eq 0 ]];then
    echo -e "\e[31m [ERROR] - Specify which option to launch: launch.sh [ BACKEND | SOLUTION | ITGTESTS ]\e[0m"
    exit 1
else
    # Read the option to launch
    toLaunch=$1

    # Validate the option to launch
    if [[ "${toLaunch}" != "BACKEND" ]] && [[ "${toLaunch}" != "SOLUTION" ]] && [[ "${toLaunch}" != "ITGTESTS" ]]
    then
        echo -e "\e[31m [ERROR] - Specify an appropriate option to launch: launch.sh [ BACKEND | SOLUTION | ITGTESTS ]\e[0m"
        exit 1
    fi

    # Read environment variables for LOCAL
    source $SETENV LOCAL

    case ${toLaunch} in
    BACKEND)
        # Launch backend components
        kafka=$(docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml ps | grep kafka | grep Up | awk '{ print $1}')
        if [[ $kafka != "docker_kafka1_1" ]]
        then
            echo -e " \e[32m@@@ Start back end\e[39m"
            rm -r kafka1 zookeeper1
            # Launching the backbone components in detached mode so that the output is cleaner
            # To see the logs execute either:
            # 1. docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml logs
            # 2. docker logs <docker_container_id>
            docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml up -d
            sleep 15
            ${MAIN_DIR}/scripts/createTopics.sh LOCAL
        else
            echo -e "\e[32m@@@ Back end services are running. These are the kafka topics: \e[39m"
            docker exec -ti docker_kafka1_1 /bin/bash -c "/opt/kafka/bin/kafka-topics.sh --list --zookeeper zookeeper1:2181"
        fi
        ;;
    SOLUTION)
        # Launch solution
        solution=$(docker-compose -f kc-solution-compose.yml ps | grep simulator | grep Up | awk '{ print $1}')
        if [[ $solution != "docker_simulator_1" ]]
        then
            echo -e "\e[32m@@@ Start all solution microservices\e[39m"
            # Launching the solution components in detached mode so that the output is cleaner
            # To see the logs execute either:
            # 1. docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml logs
            # 2. docker logs <docker_container_id>
            docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml up -d
        else
            echo -e "\e[32m@@@ all solution microservices are running\e[39m"
        fi
        ;;
    ITGTESTS)
        # Launch itgtests components
        echo -e " \e[32m@@@ Start itgtests components\e[39m"
        MICROSERVICES="kcontainer-order-command-ms
            kcontainer-order-query-ms
            kcontainer-voyages-ms
            kcontainer-spring-container-ms"
        # Check if we already have the docker images built
        for microservice in ${MICROSERVICES}
        do
            echo -e "Building the ${microservice}:test docker image..."
            case ${microservice} in
            kcontainer-order-command-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-order-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-order-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                docker build -f ${MAIN_DIR}/../refarch-kc-order-ms/order-command-ms/Dockerfile.multistage -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-order-ms/order-command-ms/
                echo -e "Done"
                ;;
            kcontainer-order-query-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-order-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-order-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                docker build -f ${MAIN_DIR}/../refarch-kc-order-ms/order-query-ms/Dockerfile.multistage -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-order-ms/order-query-ms/
                echo -e "Done"
                ;;
            kcontainer-voyages-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                docker build -f ${MAIN_DIR}/../refarch-kc-ms/voyages-ms/Dockerfile -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-ms/voyages-ms/
                echo -e "Done"
                ;;
            kcontainer-spring-container-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-container-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-container-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                docker build -f ${MAIN_DIR}/../refarch-kc-container-ms/SpringContainerMS/Dockerfile-local -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-container-ms/SpringContainerMS/
                echo -e "Done"
                ;;
            *)
                echo -e "\e[31m[ERROR] - ${microservice} is incorrect.\e[0m"
                exit 1
                ;;
            esac
        done

        echo -e "\e[32m@@@ Start all solution microservices\e[39m"
        # Launching the solution components in detached mode so that the output is cleaner
        # To see the logs execute either:
        # 1. docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml logs
        # 2. docker logs <docker_container_id>
        docker-compose -f ${MAIN_DIR}/docker/itg-tests-compose.yml up -d
        echo -e "\e[32m@@@ all itgtest components are running\e[39m"
        ;;
    *)
        echo -e "\e[31m [ERROR] - Specify an appropriate option to launch: launch.sh [ BACKEND | SOLUTION | ITGTESTS ]\e[0m"
        exit 1
        ;;
    esac
fi

# Script we are executing
echo -e " \e[32m@@@ End script: \e[1;33mlaunch.sh \e[0m"
