import os, time, json, sys
from confluent_kafka import KafkaError, Producer

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

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def prepareProducer():
    if (KAFKA_ENV == 'LOCAL'):
        options ={
            'bootstrap.servers':  KAFKA_BROKERS,
            'group.id': 'python-orders-producer'
        }
    else:
        options = {
            'bootstrap.servers':  KAFKA_BROKERS,
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': 'es-cert.pem',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'group.id': 'python-orders-producer',
        }
    return Producer(options)

def publishOrderEvent(eventToSend):
    orderProducer = prepareProducer()
    dataStr = json.dumps(eventToSend)
    orderProducer.produce('orders',key=eventToSend['orderID'],value=dataStr.encode('utf-8'), callback=delivery_report)
    orderProducer.flush()

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
    publishOrderEvent(evt)
