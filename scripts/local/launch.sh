#!/usr/bin/env bash

# Script we are executing
echo -e "---------------------------------------------"
echo -e "--  Executing script: \e[1;33mlaunch.sh \e[0m"
echo -e "---------------------------------------------"

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

# Get the environment configuration file
SETENV="${MAIN_DIR}/scripts/setenv.sh"

# Checking if the setenv.sh file exist for reading environment variables
if [[ ! -f "$SETENV"  ]]
then
    echo -e "\e[31m [ERROR] - The file setenv.sh not found under the scripts folder (${MAIN_DIR}/scripts) - Use the setenv.sh.tmpl template to create your setenv.sh file.\e[0m"
    exit 1
fi

# Get what option the user wants to launch
if [[ $# -eq 0 ]];then
    echo -e "\e[31m [ERROR] - Specify which option to launch: launch.sh [ BACKEND | DEV | TELEMETRY ]\e[0m"
    exit 1
else
    # Read the option to launch
    toLaunch=$1

    # Validate the option to launch
    if [[ "${toLaunch}" != "BACKEND" ]] && [[ "${toLaunch}" != "DEV" ]] && [[ "${toLaunch}" != "TELEMETRY" ]]
    then
        echo -e "\e[31m [ERROR] - Specify an appropriate option to launch: launch.sh [ BACKEND | DEV | TELEMETRY ]\e[0m"
        exit 1
    fi

    # Read environment variables
    source $SETENV

    case ${toLaunch} in
    BACKEND)
        # Launch backend components
        kafka=$(docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml ps | grep kafka | grep Up | awk '{ print $1}')
        if [[ $kafka != "docker_kafka_1" ]]
        then
            echo -e "\e[32mStarting backend components\e[39m"
            # Removing previous kafka and zookeeper data
            rm -rf ${MAIN_DIR}/docker/kafka-data ${MAIN_DIR}/docker/zookeeper-data
            # Launching the backbone components in detached mode so that the output is cleaner
            # To see the logs execute either:
            # 1. docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml logs
            # 2. docker logs <docker_container_id>
            docker-compose -f ${MAIN_DIR}/docker/backbone-compose.yml up -d
            sleep 15
            ${MAIN_DIR}/scripts/createTopics.sh LOCAL
        else
            echo -e "\e[32mBackend services are already running.\e[39m These are the kafka topics:"
            docker exec -ti docker_kafka_1 /bin/bash -c "/opt/kafka/bin/kafka-topics.sh --list --zookeeper zookeeper:2181"
        fi
        ;;
    DEV)
        # Launch itgtests components
        echo -e "\e[32mStarting development components\e[39m"
        MICROSERVICES="kcontainer-ui
            kcontainer-order-command-ms
            kcontainer-order-query-ms
            kcontainer-voyages-ms
            kcontainer-spring-container-ms"
            # Not yet refactored
            #kcontainer-fleet-ms"

        # Check Appsody is installed
        echo "This is the path for appsody binaries: "
        which appsody
        if [ $? -eq 1 ]; then
            echo -e "\e[31m [ERROR] - Appsody binaries could not be found. Please, install appsody first.\e[0m" 
            exit 1
        fi

        # Check if we already have the docker images built
        for microservice in ${MICROSERVICES}
        do
            echo -e "\e[1;33mBuilding the ${microservice}:test docker image...\e[39m"
            case ${microservice} in
            kcontainer-ui)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-ui" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-ui for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                # Not an Appsody application yet
                # pushd ${MAIN_DIR}/../refarch-kc-ui/
                # appsody build -t ibmcase/${microservice}:test
                # popd
                # echo -e "Done"
                docker build -f ${MAIN_DIR}/../refarch-kc-ui/Dockerfile -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-ui/
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the Docker image for ${microservice}\e[0m"
                    exit 1
                else
                    echo -e "Done"
                fi
                ;;
            kcontainer-fleet-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                # Not an Appsody application yet
                # pushd ${MAIN_DIR}/../refarch-kc-ms/fleet-ms/
                # appsody build -t ibmcase/${microservice}:test
                # popd
                # echo -e "Done"
                docker build -f ${MAIN_DIR}/../refarch-kc-ms/fleet-ms/Dockerfile.multistage -t ibmcase/${microservice}:test ${MAIN_DIR}/../refarch-kc-ms/fleet-ms/
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the Docker image for ${microservice}\e[0m"
                    exit 1
                else
                    echo -e "Done"
                fi
                ;;
            kcontainer-order-command-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-order-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-order-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                pushd ${MAIN_DIR}/../refarch-kc-order-ms/order-command-ms/
                appsody build -t ibmcase/${microservice}:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            kcontainer-order-query-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-order-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-order-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                pushd ${MAIN_DIR}/../refarch-kc-order-ms/order-query-ms/
                appsody build -t ibmcase/${microservice}:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            kcontainer-voyages-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                pushd ${MAIN_DIR}/../refarch-kc-ms/voyages-ms/
                appsody build -t ibmcase/${microservice}:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            kcontainer-spring-container-ms)
                if [ ! -d "${MAIN_DIR}/../refarch-kc-container-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-container-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                pushd ${MAIN_DIR}/../refarch-kc-container-ms/
                appsody build -t ibmcase/${microservice}:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            *)
                echo -e "\e[31m[ERROR] - ${microservice} is incorrect.\e[0m"
                exit 1
                ;;
            esac
        done

        echo -e "\e[32mStarting all solution microservices\e[39m"
        # Launching the solution components in detached mode so that the output is cleaner
        # To see the logs execute either:
        # 1. docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml logs
        # 2. docker logs <docker_container_id>
        docker-compose -f ${MAIN_DIR}/docker/kc-development-compose.yml up -d
        ;;
    TELEMETRY)
        # Launch anomaly detection from telemetries use case's components
        # Check that appsody is installed
        echo "This is the path for appsody binaries: "
        which appsody
        if [ $? -eq 1 ]; then
            echo -e "\e[31m [ERROR] - Appsody binaries could not be found. Please, install appsody first.\e[0m" 
            exit 1
        fi

        echo -e "\e[32mBuilding all telemetry components\e[39m"
        MICROSERVICES="kcontainer-spring-container-ms
            kcontainer-reefer-ml"
        # Check if we already have the docker images built
        for microservice in ${MICROSERVICES}
        do
            case ${microservice} in
            kcontainer-spring-container-ms)
                echo -e "\e[1;33mBuilding the ${microservice}:test docker image...\e[0m"
                if [ ! -d "${MAIN_DIR}/../refarch-kc-container-ms" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-kc-container-ms for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi
                pushd ${MAIN_DIR}/../refarch-kc-container-ms/
                appsody build -t ibmcase/${microservice}:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            kcontainer-reefer-ml)
                echo -e "\e[1;33mBuilding the ${microservice}-scoringmp:test docker image...\e[0m"
                if [ ! -d "${MAIN_DIR}/../refarch-reefer-ml" ]; then
                    echo -e "\e[31m[ERROR] - The repository ${MAIN_DIR}/../refarch-reefer-ml for ${microservice} does not exist.\e[0m"
                    echo -e "\e[31m[ERROR] - Please, clone that repository first.\e[0m"
                    exit 1
                fi

                pushd ${MAIN_DIR}/../refarch-reefer-ml/scoring-mp/
                appsody build -t ibmcase/${microservice}-scoringmp:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}-scoringmp\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi

                echo -e "\e[1;33mBuilding the ${microservice}-flask-simulator:test docker image...\e[0m"

                pushd ${MAIN_DIR}/../refarch-reefer-ml/simulator
                appsody build -t ibmcase/${microservice}-flask-simulator:test
                if [[ $? -ne 0 ]]
                then 
                    echo -e "\e[31m[ERROR] - A problem occurred building the docker image for ${microservice}-flask-simulator\e[0m"
                    exit 1
                else
                    popd
                    echo -e "Done"
                fi
                ;;
            *)
                echo -e "\e[31m[ERROR] - ${microservice} is incorrect.\e[0m"
                exit 1
                ;;
            esac
        done

        echo -e "\e[32mStarting all telemetry microservices\e[39m"
        # Launching the solution components in detached mode so that the output is cleaner
        # To see the logs execute either:
        # 1. docker-compose -f ${MAIN_DIR}/docker/kc-solution-compose.yml logs
        # 2. docker logs <docker_container_id>
        docker-compose -f ${MAIN_DIR}/docker/kc-development-compose-anomaly.yml up -d
        echo -e "\e[32mAll telemetry components are running\e[39m"
        ;;
    *)
        echo -e "\e[31m [ERROR] - Specify an appropriate option to launch: launch.sh [ BACKEND | DEV | TELEMETRY ]\e[0m"
        exit 1
        ;;
    esac
fi

# Script we are executing
echo -e "---------------------------------------------"
echo -e "--  End script: \e[1;33mlaunch.sh \e[0m"
echo -e "---------------------------------------------"
