# Validate event sourcing pattern: create new orders to the order microservice end points
# validate the order is added and a order created event was added
# It assumes the event broker (kafka) and all the solution services are running locally (by default)
# If these tests have to run against remote deployed solution the following environment variables are used:
# KAFKA_BROKERS, ORDER_CMD_MS (URL end point for the Command microservice, ORDER_QUERY_MS' for the query ms)
import unittest
import os
import json
import requests
import time

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

try:
    ORDER_CMD_MS = os.environ['ORDER_CMD_MS']
except KeyError:
    ORDER_CMD_MS = "ordercmd:9080"

try:
    ORDER_QUERY_MS = os.environ['ORDER_QUERY_MS']
except:
    ORDER_QUERY_MS = "orderquery:9080"

# listen to orders topic, verify orderCreated event was published
from confluent_kafka import Consumer, KafkaError, Producer

# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
orderConsumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'python-orders-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
})
orderConsumer.subscribe(['orders'])

def pollNextOrder(orderID):
    gotIt = False
    order = {}

    while not gotIt:
        msg = orderConsumer.poll(timeout=10.0)
        if msg is None:
            print("no message")
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n'
                .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key())))
        orderStr = msg.value().decode('utf-8')
        print('@@@ pollNextOrder Received message: {}'.format(orderStr))
        orderEvent = json.loads(orderStr)
        if (orderEvent['payload']['orderID'] == orderID):
            print('@@@@ got the matching order ')
            gotIt = True
    return orderEvent

def getAllOrderedOrderEvents(orderID):
    print("Get all event matching the given orderID")
    orderReloader = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'python-orders-reload',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
    })
    orderReloader.subscribe(['orders'])
    orderEvents = []
    gotAll = False
    while not gotAll:
        msg = orderReloader.poll(timeout=30)
        if msg is None:
            print('Timed out... assume we have all')
            gotAll = True
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            gotAll = True
            continue
        eventAsString = msg.value().decode('utf-8')
        orderEvent = json.loads(eventAsString)
        if (orderEvent['payload']['orderID'] == orderID):
            orderEvents.append(orderEvent)
    orderReloader.close()
    return orderEvents

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def postContainerAllocated(orderID):
    orderProducer = Producer({'bootstrap.servers': KAFKA_BROKERS})
    data = {"timestamp": int(time.time()),"type":"ContainerAllocated","version":"1","payload": {"containerID": "c10","orderID":orderID}}
    dataStr = json.dumps(data)
    orderProducer.produce('orders',dataStr.encode('utf-8'), callback=delivery_report)
    orderProducer.flush()


def getOrderQuery(orderID):
    res = requests.get("http://" + ORDER_QUERY_MS + "/orders/" + orderID)
    print(res.text)
    return json.loads(res.text)

'''
Test the happy path for the state diagram as in 
https://ibm-cloud-architecture.github.io/refarch-kc/design/readme/#shipment-order-lifecycle-and-state-change-events
'''
class TestEventSourcingHappyPath(unittest.TestCase):
    def test_createOrder(self):
        print("1- load the order request from json")
        f = open('../data/FreshProductOrder.json','r')
        order = json.load(f)
        f.close()
        
        # 2- create order by doing a POST on /api/orders of the orders command service
        res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
        orderID=json.loads(res.text)['orderID']
        self.assertIsNotNone(orderID)
        print('@@@@ Post new order -> resp with ID:' + orderID)
        
        # 3- get OrderCreated Event
        print('@@@@ wait for OrderCreated event with ID:' + orderID)
        orderEvent = pollNextOrder(orderID)
        self.assertEqual(orderEvent['type'], "OrderCreated")

        # 4- get next order event, should be assigned to a voyage
        print('@@@@ wait for OrderAssigned event from the voyage service for ' + orderID)
        orderEvent = pollNextOrder(orderID)
        self.assertEqual(orderEvent['type'], "OrderAssigned")
        voyage=orderEvent['payload']
        self.assertIsNotNone(voyage)
        self.assertIsNotNone(voyage['voyageID'])
        # 4.2- Verify voyageId is in the query model 
        time.sleep(10)
        orderQuery = getOrderQuery(orderID)
        voyageID=orderQuery['voyageID']
        self.assertIsNotNone(voyageID)

        # 5- Simulate assignment of the container
        print('@@@@ post container allocation to mockup missing container ms for ' + orderID)
        postContainerAllocated(orderID)
        time.sleep(10)
        orderQuery = getOrderQuery(orderID)
        containerID=orderQuery['containerID']
        self.assertIsNotNone(containerID)
        
        # 6- list all events 
        orderEvents = getAllOrderedOrderEvents(orderID)
        for oe in orderEvents:
            print(oe)
       


if __name__ == '__main__':
    unittest.main()
    orderConsumer.close()