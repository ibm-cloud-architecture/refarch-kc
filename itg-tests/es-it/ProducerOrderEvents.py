'''
Produce a set of events representing a full life cycle of the happy path.
'''

import os, time, json, sys
import datetime
from kafka.KcProducer import KafkaProducer 

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit
    
try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")

try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    KAFKA_ENV='LOCAL'

def createOrder(id):
    print('Create order for '+ id)
    data = {"orderID": id, 
        "productID": "FreshFoodItg", 
        "customerID": "Customer007",
        "quantity": 180, 
        "pickupAddress": {"street": "astreet","city": "Oakland","country":"USA","state":"CA","zipcode": "95000"},
        "destinationAddress": {"street": "bstreet","city": "Beijing","country":"China","state":"NE","zipcode": "09000"},
        "pickupDate": "2019-05-25",
        "expectedDeliveryDate": "2019-06-25"}
    d = datetime.datetime(2019, 4, 13,10,0,14)
    evt = {"orderID": id,"timestamp": int(datetime.datetime.timestamp(d)),"type":"OrderCreated","payload": data}
    return evt

def orderBooked(id):
    data = {"orderID": id, 
        "productID": "FreshFoodItg", 
        "customerID": "Customer007",
        "quantity": 180, 
        "pickupAddress": {"street": "astreet","city": "Oakland","country":"USA","state":"CA","zipcode": "95000"},
        "destinationAddress": {"street": "bstreet","city": "Beijing","country":"China","state":"NE","zipcode": "09000"},
        "pickupDate": "2019-05-25",
        "expectedDeliveryDate": "2019-06-25"}
    d = datetime.datetime(2019, 4, 15,8,30,0)
    evt = {"orderID": id,"timestamp": int(datetime.datetime.timestamp(d)),"type":"OrderBooked","payload": data}
    return evt

def voyageAssigned(id):
    data = {"orderID": id, 
            "voyageID": "voyage21"}
    d = datetime.datetime(2019, 4, 15,8,35,0)
    evt = {"orderID": id,"timestamp": int(datetime.datetime.timestamp(d)),"type":"OrderAssigned","payload": data}
    return evt

def containerAllocated(id):
    data = {"orderID": id, 
            "containerID": "c13"}
    d = datetime.datetime(2019, 4, 16,9,10,0)
    evt = {"orderID": id,"timestamp": int(datetime.datetime.timestamp(d)),"type":"ContainerAllocated","payload": data}
    return evt

def fullContainerVoyageReady(id):
    data = {"orderID": id, 
            "containerID": "c13"}
    d = datetime.datetime(2019, 5, 15,14,30,0)
    evt = {"orderID": id,"timestamp": int(datetime.datetime.timestamp(d)),"type":"FullContainerVoyageReady","payload": data}
    return evt

def parseArguments():
    if len(sys.argv) == 2:
        OID = sys.argv[1]
    else:
        OID = "itg-Ord02"
    print("The arguments are: " , str(sys.argv))
    return OID

if __name__ == '__main__':
    OID=parseArguments()
    print("Generate events for " + OID)
    print(KAFKA_ENV) 
    print(KAFKA_BROKERS)
    evt = createOrder(OID)
    print("\t 1- CreateOrder:" + json.dumps(evt))
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
    kp.prepareProducer("OrderProducerPython")
    kp.publishEvent('orders',evt,"orderID")
    
    evt = orderBooked(OID)
    print("\t 2- Producer accept the offer so now the order is booked:" + json.dumps(evt))
    kp.publishEvent('orders',evt,"orderID")

    evt = voyageAssigned(OID)
    print("\t 3- Voyage is assigned to order:" + json.dumps(evt))
    kp.publishEvent('orders',evt,"orderID")

    evt = containerAllocated(OID)
    print("\t 4- Allocate Reefer to order:" + json.dumps(evt))
    kp.publishEvent('orders',evt,"orderID")


    evt = fullContainerVoyageReady(OID)
    print("\t 5- Reefer loaded with goods ready for Voyage:" + json.dumps(evt))
    kp.publishEvent('orders',evt,"orderID")