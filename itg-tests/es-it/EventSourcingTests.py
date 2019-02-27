# Validate event sourcing pattern: create new orders to the order microservice end points
# validate the order is added and a order created event was added
# It assumes the event broker (kafka) and all the solution services are running locally (by default)
# If these tests have to run against remote deployed solution the following environment variables are used:
import os
KAFKA_BROKERS=os.environ['KAFKA_BROKERS']
ORDER_CMD_MS=os.environ['ORDER_CMD_MS']

# load the order request from json
import json
f = open('../data/FreshProductOrder.json','r')
order = json.load(f)
print(order)

# call create order service
import requests
res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
print(res)
