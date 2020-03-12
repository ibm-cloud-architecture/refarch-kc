#!/usr/bin/env bash

# Script we are executing
echo -e " \e[32m@@@ Excuting script: \e[1;33mE2EHappyPath.sh \e[0m"

## Variables

# Get the absolute path for this file
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Get the absolute path for the refarch-kc project
MAIN_DIR=`echo ${SCRIPTPATH} | sed 's/\(.*refarch-kc\).*/\1/g'`

SETENV="${MAIN_DIR}/scripts/setenv.sh"

# Get what option the user wants to launch
if [[ "$1" != "LOCAL" && "$1" != "OCP" && "$1" != "IBMCLOUD" || $# -eq 0 ]];then
    echo -e "\e[31m [ERROR] - Specify which environment to run the integration test against: E2EHappyPath.sh [ LOCAL | OCP ]\e[0m"
    exit 1
else
    # Read the option to launch
    ENV=$1
fi

# Check if the ibmcase/python docker image exists
EXISTS="$(docker images | awk '{print $1 ":" $2}' | grep ibmcase-python:test)"
if [ -z "${EXISTS}" ]
then
    echo -e "The ibmcase/python docker image does not exist. Creating such image..."
    docker build -f ${MAIN_DIR}/docker/docker-python-tools -t ibmcase-python:test ${MAIN_DIR}/docker
fi

#Set environment variables
source ${SETENV} ${ENV}

if [ "OCP" == "${ENV}" ]; then
    add_cert_to_container_command=" -e PEM_CERT=/certs/${PEM_FILE} -v ${CA_LOCATION}:/certs"
fi

docker run  -v ${MAIN_DIR}:/refarch-kc \
            --network=docker_default \
            ${add_cert_to_container_command} \
            --rm \
            -ti ibmcase-python:test bash \
            -c "cd /refarch-kc/itg-tests/es-it && \
                source /refarch-kc/scripts/setenv.sh ${ENV} && \
                export PYTHONPATH=\${PYTHONPATH}:/refarch-kc/itg-tests && \
                touch /tmp/results.txt && \
                echo '******************************************' && \
                echo '******************************************' && \
                echo '**********   E2E Happy Path   ************' && \
                echo '******************************************' && \
                echo '******************************************' && \
                python E2EHappyPath.py && source /tmp/E2EHappyPath.properties && \
                echo '******************************************' && \
                echo '******************************************' && \
                echo '*********   Saga No Container   **********' && \
                echo '******************************************' && \
                echo '******************************************' && \
                python Saga_NoContainer.py && \
                echo '******************************************' && \
                echo '******************************************' && \
                echo '**********   Saga No Voyage   ************' && \
                echo '******************************************' && \
                echo '******************************************' && \
                python Saga_NoVoyage.py && source /tmp/SagaNoVoyage.properties && \
                echo '******************************************' && \
                echo '******************************************' && \
                echo '**********   Order Rejected   ************' && \
                echo '******************************************' && \
                echo '******************************************' && \
                python OrderRejection.py && \
                echo '******************************************' && \
                echo '******************************************' && \
                echo '*********   Container Anomaly   **********' && \
                echo '******************************************' && \
                echo '******************************************' && \
                python ContainerAnomaly.py && \
                echo '****************************************************' && \
                echo '****************************************************' && \
                echo '*********   Retry and Dead Letter Queue   **********' && \
                echo '****************************************************' && \
                echo '****************************************************' && \
                python ContainerAnomalyDlq.py && \
                echo && echo 'END RESULTS:' && echo && \
                cat /tmp/results.txt"