# Make sure we are in the shipping project
oc project shipping
if [[ $? -gt 0 ]]; then
    echo "[ERROR] - An error occurred switching to work with the shipping project"
    exit 1
fi

# Get the routes for each of the KContainer components involved
UI_ROUTE=`oc get route kc-ui -o jsonpath="{.spec.host}"`
ORDER_COMMAND_ROUTE=`oc get route order-command-ms -o jsonpath="{.spec.host}"`
ORDER_QUERY_ROUTE=`oc get route order-query-ms -o jsonpath="{.spec.host}"`
CONTAINERS_ROUTE=`oc get route spring-container-ms -o jsonpath="{.spec.host}"`
VOYAGES_ROUTE=`oc get route voyages-ms -o jsonpath="{.spec.host}"`

# Set up the endpoints
UI_ENDPOINT="${UI_ROUTE}/api/orders/GoodManuf"
ORDER_COMMAND_ENDPOINT="${ORDER_COMMAND_ROUTE}/orders"
ORDER_QUERY_ENDPOINT="${ORDER_QUERY_ROUTE}/orders"
CONTAINERS_ENDPOINT="${CONTAINERS_ROUTE}/containers"
VOYAGES_ENDPOINT="${VOYAGES_ROUTE}/voyage"

echo "These are the endpoints for each of the KContainer components"
echo "-------------------------------------------------------------"
echo "* User Interface --> ${UI_ENDPOINT}"
echo "* Order Command  --> ${ORDER_COMMAND_ENDPOINT}"
echo "* Order Query    --> ${ORDER_QUERY_ENDPOINT}"
echo "* Containers     --> ${CONTAINERS_ENDPOINT}"
echo "* Voyages        --> ${VOYAGES_ENDPOINT}"


function get_state() {
    # Print out the state for each of the components
    echo
    echo "These are the states for each of the KContainer components at `date`"
    echo "---------------------------------------------------------------------------------------"
    echo "User Interface:"
    curl -s ${UI_ENDPOINT} | jq
    echo
    echo "Order Command:"
    curl -s ${ORDER_COMMAND_ENDPOINT} | jq
    echo
    echo "Order Query:"
    curl -s ${ORDER_QUERY_ENDPOINT} | jq
    echo
    echo "Containers:"
    curl -s ${CONTAINERS_ENDPOINT} | jq .content
    echo
    echo "Voyages:"
    curl -s ${VOYAGES_ENDPOINT} | jq
    echo
}

while true
do
    echo
    read -rsp $'Press any key to get the state for each of the KContainer components\n' -n1 key
    get_state
done