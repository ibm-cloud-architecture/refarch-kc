# Validate CQRS pattern: create new order to the order microservice end points
# validate the order is added and a order created event was added
# It assumes the event broker (kafka) and all the solution services are running
# If these tests have to run against remote deployed solution the following environment variables are used:
# KAFKA_BROKERS, ORDER_CMD_MS (URL end point for the Command microservice, ORDER_QUERY_MS' for the query ms)
import unittest
import os
import json
import requests
import time

try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    KAFKA_ENV='LOCAL'


try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    KAFKA_APIKEY='nokey'


try:
    ORDER_CMD_MS = os.environ['ORDER_CMD_MS']
except KeyError:
    ORDER_CMD_MS = "ordercmd:9080"

try:
    ORDER_QUERY_MS = os.environ['ORDER_QUERY_MS']
except:
    ORDER_QUERY_MS = "orderquery:9080"

# listen to orders topic, verify orderCreated event was published
from kafka.KcConsumer import KafkaConsumer
TOPIC_NAME = 'orders'

orderConsumer = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,TOPIC_NAME,False)
orderConsumer.prepareConsumer()

def pollNextOrder(orderid):
    return orderConsumer.pollNextEvent(orderid,'orderID')

class TestEventSourcingHappyPath(unittest.TestCase):
    def test_createOrder(self):
        print("1- load the order request from json")
        f = open('../data/FreshProductOrder.json','r')
        order = json.load(f)
        f.close()
        
        print("2- create order by doing a POST on /api/orders of the orders command service")
        res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
        orderID=json.loads(res.text)['orderID']
        self.assertIsNotNone(orderID)
        print('@@@@ Post new order -> resp with ID:' + orderID)
        
        print("3- get OrderCreated Event")
        print('@@@@ wait for OrderCreated event with ID:' + orderID)
        orderEvent = pollNextOrder(orderID)
        self.assertEqual(orderEvent['type'], "OrderCreated")

        print("4- Use the query part to see the updated records on the read model")
        manuf = orderEvent['payload']['customerID']
        res = requests.get("http://" + ORDER_QUERY_MS + "/orders/byManuf/" + manuf)
        print(res.text)
        orders=json.loads(res.text)
        found = False
        for order in orders:
            if order['orderID'] == orderID:
                found = True
        self.assertEqual(found, True)

if __name__ == '__main__':
    unittest.main()
    orderConsumer.close()