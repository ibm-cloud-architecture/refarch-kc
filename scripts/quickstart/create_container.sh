
# Make sure a size for the container is provided
if [[ ! $# -eq 1 ]];then
 echo "Usage: sh create_container.sh SIZE"
 exit 1
fi

# Check the size of the container to be created is bigger than 0
if [[ $1 -lt 1 ]];then
  echo "The SIZE for the container must be bigger than 0"
  exit 1
fi

CAPACITY=$1

# Generate a ramdom container ID
RAMDOM=$$
CONTAINER_ID=$(( $(($RAMDOM%8889)) + 1111))

# Make sure we are in the shipping project
oc project shipping
if [[ $? -gt 0 ]]; then
    echo "[ERROR] - An error occurred switching to work with the shipping project"
    exit 1
fi

# Get the Container Management component OpenShift route
CONTAINERS_ROUTE=`oc get route spring-container-ms -o jsonpath="{.spec.host}"`

echo "Creating a new container with ID = ${CONTAINER_ID} and size = ${CAPACITY}"
echo

curl -s --header "Content-Type: application/json" --request POST --data '{"containerID": "'${CONTAINER_ID}'","type": "Reefer","status": "Empty","latitude": 31.4,"longitude": 121.5,"capacity": '${CAPACITY}',"brand": "itgtests-brand"}' http://${CONTAINERS_ROUTE}/containers | jq