#!/bin/bash
SCRIPTLOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# This script will modify the Kafka topic configuration to use topics prefixed 'itg-'
# before running the tests, and then reset the topics when finished.

# Delete old integration job, if it exists
kubectl delete -f $SCRIPTLOC/../../itg-tests/es-it/ReeferItgTests.yaml -n shipping

# Deploy integration Kafka topics
kubectl apply -f $SCRIPTLOC/itg-kafka-topics-configmap.yaml -n shipping
kubectl apply -f $SCRIPTLOC/itg-topics.yaml -n kafka

# Configure BPM to use mockup instance
kubectl apply -f $SCRIPTLOC/itg-bpm-configmap.yaml -n shipping

# Restart services so that they are configured with the new topic names
kubectl scale deployment --replicas=0 -n shipping --all
kubectl scale deployment --replicas=1 -n shipping --all

# Wait for services to restart
kubectl rollout status -n shipping deployment springcontainerms-deployment
kubectl rollout status -n shipping deployment fleetms-deployment
kubectl rollout status -n shipping deployment kc-ui-deployment
kubectl rollout status -n shipping deployment ordercommandms-deployment
kubectl rollout status -n shipping deployment orderqueryms-deployment
kubectl rollout status -n shipping deployment voyagesms-deployment

# Deploy integration tests job
sed -e's#value: "IBMCLOUD#value: "LOCAL#' $SCRIPTLOC/../../itg-tests/es-it/ReeferItgTests.yaml > $SCRIPTLOC/../../itg-tests/es-it/ReeferItgTests.yaml.local
kubectl apply -f $SCRIPTLOC/../../itg-tests/es-it/ReeferItgTests.yaml.local -n shipping

# Wait for job pod to be ready (ie. job has started running)
# This will take seconds, unless the image needs pulling from a remote registry.
kubectl wait --for=condition=ready pod -l job-name=reefer-itgtests-job -n shipping --timeout 180s

# Follow the job log
kubectl logs job/reefer-itgtests-job -n shipping -f

# Wait for job completion (just in case network is interrupted while following log)
kubectl wait --for=condition=complete job reefer-itgtests-job -n shipping --timeout 600s

# Deploy normal Kafka topics
kubectl apply -f $SCRIPTLOC/kafka-topics-configmap.yaml -n shipping

# Restore BPM config
kubectl apply -f $SCRIPTLOC/bpm-configmap.yaml -n shipping

# Restart services so that they are configured with the new topic names
kubectl scale deployment --replicas=0 -n shipping --all
kubectl scale deployment --replicas=1 -n shipping --all

# Wait for services to restart
kubectl rollout status -n shipping deployment springcontainerms-deployment
kubectl rollout status -n shipping deployment fleetms-deployment
kubectl rollout status -n shipping deployment kc-ui-deployment
kubectl rollout status -n shipping deployment ordercommandms-deployment
kubectl rollout status -n shipping deployment orderqueryms-deployment
kubectl rollout status -n shipping deployment voyagesms-deployment
