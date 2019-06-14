import os, time, json, sys
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
    print('Create order')
    data = {"orderID": id, 
        "productID": "FreshFoodItg", 
        "customerID": "Customer007",
        "quantity": 180, 
        "pickupAddress": {"street": "astreet","city": "Oakland","country":"USA","state":"CA","zipcode": "95000"},
        "destinationAddress": {"street": "bstreet","city": "Beijing","country":"China","state":"NE","zipcode": "09000"},
        "pickupDate": "2019-05-25",
        "expectedDeliveryDate": "2019-06-25"}
    containerEvent = {"orderID": id,"timestamp": int(time.time()),"type":"OrderCreated","payload": data}
    return containerEvent

def parseArguments():
    if len(sys.argv) == 2:
        OID = sys.argv[1]
    else:
        OID = "itg-Ord02"
    print("The arguments are: " , str(sys.argv))
    return OID

if __name__ == '__main__':
    OID=parseArguments()
    evt = createOrder(OID)
    print(evt)
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
    kp.prepareProducer("OrderProducerPython")
    kp.publishEvent('orders',evt,"orderID")
