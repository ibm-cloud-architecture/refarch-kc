# Validate event sourcing pattern: create new orders to the order microservice end points
# validate the order is added and a order created event was added
# It assumes the event broker (kafka) and all the solution services are running locally (by default)
# If these tests have to run against remote deployed solution the following environment variables are used:
import unittest
import os
import json
import requests

KAFKA_BROKERS=os.environ['KAFKA_BROKERS']
ORDER_CMD_MS=os.environ['ORDER_CMD_MS']

# listen to orders topic, verify orderCreated event was published
from confluent_kafka import Consumer, KafkaError
orderConsumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'pyth-orders',
    'auto.offset.reset': 'earliest'
})
orderConsumer.subscribe(['orders'])

def pollFirstOrder():
    gotIt = False
    order = {}
    while not gotIt:
        msg = orderConsumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        order = msg.value().decode('utf-8')
        print('Received message: {}'.format(order))
        gotIt = True
    return json.loads(order)
   
class TestEventSourcingHappyPath(unittest.TestCase):
    def test_createOrder(self):
        # 1- load the order request from json
        f = open('../data/FreshProductOrder.json','r')
        order = json.load(f)
        # 2- call create order service
        res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
        self.assertIsNotNone(json.loads(res.text)['orderID'])
        # 3- get OrderCreated Event
        orderEvent = pollFirstOrder()
        print(orderEvent)
        self.assertEquals(orderEvent['type'], "OrderCreated")
        self.assertEquals(orderEvent['orderID'],)

        


if __name__ == '__main__':
    unittest.main()
    orderConsumer.close()