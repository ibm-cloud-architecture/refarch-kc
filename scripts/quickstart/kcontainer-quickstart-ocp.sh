#!/bin/bash

##################
### PARAMETERS ###
##################

# Username and Password for an OpenShift user with cluster-admin privileges.
# cluster-admin privileges are required as this script deploys operators to
# watch all namespaces.
OCP_ADMIN_USER=${OCP_ADMIN_USER:=admin}
OCP_ADMIN_PASSWORD=${OCP_ADMIN_PASSWORD:=admin}

###################################
### DO NOT EDIT BELOW THIS LINE ###
###################################
### EDIT AT YOUR OWN RISK      ####
###################################

#################################################
### UTILITY FUNCTION FOR Open Liberty LOGGING ###
### Usage: oc logs <pod_name> | ol_logs
#################################################
alias ol_logs="jq '.ibm_datetime + \" \" + .loglevel + \"\\t\" + \" \" + .message' -r"

function install_operator() {
### function will create an operator subscription to the openshift-operators
###          namespace for CR use in all namespaces
### parameters:
### $1 - operator name
### $2 - operator channel
### $3 - operator catalog source
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: ${1}
  namespace: openshift-operators
spec:
  channel: ${2}
  name: ${1}
  source: $3
  sourceNamespace: openshift-marketplace
EOF
}


############
### MAIN ###
############

### Login
# Make sure we don't have more than 1 argument
if [[ $# -gt 1 ]];then
 echo "Usage: sh kcontainer-quickstart-ocp.sh [--skip-login]"
 exit 1
fi

# Check the argument is what we expect
if [[ $# -eq 1 ]];then
  if [[ "$1" == "--skip-login" ]]; then
    echo "Checking if you are logged into OpenShift..."
    oc whoami
    if [[ $? -gt 0 ]]; then
      echo "[ERROR] - An error occurred while checking if you are logged into OpenShift"
      exit 1
    fi
    echo "OK"
    SKIP_LOGIN="true"
  else
    echo "Usage: sh kcontainer-quickstart-ocp.sh [--skip-login]"
    exit 1
  fi
fi

# Log in if we need to
if [ -z $SKIP_LOGIN ]; then
  oc login -u ${OCP_ADMIN_USER} -p ${OCP_ADMIN_PASSWORD}
  if [[ $? -gt 0 ]]; then
    echo "[ERROR] - An error occurred while logging into OpenShift"
    exit 1
  fi
fi

git clone https://github.com/ibm-cloud-architecture/refarch-kc-gitops.git

cd refarch-kc-gitops/environments

### INSTALL Strimzi OPERATOR
### More info available via `oc describe packagemanifests strimzi-kafka-operator -n openshift-marketplace`

### Strimzi operator version stability appears to be not so stable, so this will
### specify the latest manually verified operator version for a given OCP version
### instead of just the default "stable" stream.
STRIMZI_OPERATOR_VERSION="strimzi-0.20.x"
OCP_VERSION=$(oc version -o json | jq -r ".openshiftVersion")

case ${OCP_VERSION} in
  4.4.*)
    echo "OpenShift v4.4.X detected. Installing 'strimzi-0.19.x'..."
    STRIMZI_OPERATOR_VERSION="strimzi-0.19.x"
    ;;
  4.5.*)
    echo "OpenShift v4.5.X detected. Installing 'strimzi-0.20.x'..."
    STRIMZI_OPERATOR_VERSION="strimzi-0.20.x"
    ;;
  *)
    STRIMZI_OPERATOR_VERSION="stable"
    ;;
esac

install_operator "strimzi-kafka-operator" "${STRIMZI_OPERATOR_VERSION}" "community-operators"

### INSTALL Appsody OPERATOR
### More info available via `oc describe packagemanifests appsody-operator-certified -n openshift-marketplace`
install_operator "appsody-operator-certified" "beta" "certified-operators"

### INSTALL OpenLiberty OPERATOR
### More info available via `oc describe packagemanifests open-liberty-certified -n openshift-marketplace`
install_operator "open-liberty-certified" "beta" "certified-operators"

###TODO### Alternate implementation for `oc wait --for=condition=AtLatestKnown subscription/__operator_subscription__ --timeout 300s`
for operator in strimzi-kafka-operator appsody-operator-certified open-liberty-certified
do
  counter=0
  desired_state="AtLatestKnown"
  until [[ ("$(oc get -o json -n openshift-operators subscription ${operator} | jq -r .status.state)" == "${desired_state}") || ( ${counter} == 60 ) ]]
  do
    echo Waiting for ${operator} operator to be deployed...
    ((counter++))
    sleep 5
  done
done

### CREATE PROJECT & KAFKA INFRASTRUCTURE
oc apply -k dev/infrastructure/

oc project shipping

oc adm policy add-scc-to-user anyuid -z kcontainer-runtime -n shipping

echo Waiting for Kafka cluster to be available...
oc wait --for=condition=ready kafka my-cluster --timeout "-1s" -n shipping

### DEPLOY APPLICATION MICROSERVICES
oc apply -k dev/

### WAIT FOR MICROSERVICE DEPLOYMENTS TO BECOME AVAILABLE
echo Waiting for application microservices to be available...
sleep 10
oc wait --for=condition=available deploy -l app.kubernetes.io/part-of=refarch-kc --timeout "-1s" -n shipping

### GET ROUTE FOR USER INTERFACE MICROSERVICE
echo "User Interface Microservice is available via http://$(oc get route kc-ui -o jsonpath='{.status.ingress[0].host}')"

### MANUAL STEP ### Send order event via browser
echo Login to the browser UI with \"eddie@email.com\" / \"Eddie\" and submit an order via the \"Initiate Orders\" tab
# read -rsp $'Press any key to continue once an order has been submitted...\n' -n1 key

### Track kafka record via kafka-console-consumer and `oc rsh`
# echo "Checking ORDER-COMMANDS topic for Kafka records produced by the order-command microservice..."
# oc rsh my-cluster-kafka-0 bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --from-beginning --timeout-ms 10000 --topic order-commands

# echo "Checking ORDERS topic for Kafka records produced by the order-command microservice..."
# oc rsh my-cluster-kafka-0 bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --from-beginning --timeout-ms 10000 --topic orders
