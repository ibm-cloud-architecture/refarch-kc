# Validate event sourcing pattern: create new orders to the order microservice end points
# validate the order is added and a order created event was added
# It assumes the event broker (kafka) and all the solution services are running locally (by default)
# If these tests have to run against remote deployed solution the following environment variables are used:
import unittest
import os
import json
import requests
import time
import OrderConsumer

try:
    ORDER_CMD_MS = os.environ['ORDER_CMD_MS']
except KeyError:
    ORDER_CMD_MS = "ordercmd:9080"

def orderCommand(order):
    res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
    return json.loads(res.text)


class TestEventSourcingHappyPath(unittest.TestCase):
    def test_createCancellableOrder(self):
        print("Create a cancellable order")
        # 1- load the order request from json
        f = open('../data/FreshProductCancellableOrder.json','r')
        order = json.load(f)
        f.close()

        # 2- create order by doing a POST on /api/orders of the orders command service
        orderRep=orderCommand(order)
        orderID=orderRep['orderID']
        self.assertIsNotNone(orderID)
        print('@@@@ Post new order -> resp with ID:' + orderID)
        
        # 3- Get order create event
        print('@@@@ wait for OrderCreated event with ID:' + orderID)
        orderEvent = OrderConsumer.pollNextOrder(orderID)
        self.assertEqual(orderEvent['type'], "OrderCreated")

        # 4- get next order event, should be order cancelled to a voyage
        print('@@@@ wait for OrderCancelled event from the voyage service for ' + orderID)
        orderEvent = OrderConsumer.pollNextOrder(orderID)
        self.assertEqual(orderEvent['type'], "OrderCancelled")


if __name__ == '__main__':
    unittest.main()
    