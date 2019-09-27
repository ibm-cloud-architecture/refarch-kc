import os, time, json, sys
from kafka.KcProducer import KafkaProducer

print(" @@@ Excuting script: OrderProducer.py")

# Try to read the Kafka broker from the environment variables
try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("[ERROR] - The KAFKA_BROKERS environment variable needs to be set.")
    exit(1)

# Try to read the Kafka API key from the environment variables   
try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")

# Try to read the Kafka environment from the environment variables
try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    KAFKA_ENV='LOCAL'

# Default values
ID = "o_1"
TOPIC_NAME="orders"

def createOrder(id):
    print('Creating order...', end ='')
    data = {"orderID": id, 
        "productID": "FreshFoodItg", 
        "customerID": "Customer007",
        "quantity": 180, 
        "pickupAddress": {"street": "astreet","city": "Oakland","country":"USA","state":"CA","zipcode": "95000"},
        "destinationAddress": {"street": "bstreet","city": "Beijing","country":"China","state":"NE","zipcode": "09000"},
        "pickupDate": "2019-05-25",
        "expectedDeliveryDate": "2019-06-25"}
    containerEvent = {"orderID": id,"timestamp": int(time.time()),"type":"OrderCreated","payload": data}
    print("DONE")
    return containerEvent

# Parse arguments to get the Order ID
def parseArguments():
    print("The arguments for the script are: " , str(sys.argv))
    if len(sys.argv) == 2:
        ID = sys.argv[1]
    return ID

if __name__ == '__main__':
    OID = parseArguments()
    evt = createOrder(OID)
    print("Order event to be published:")
    print(evt)
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
    kp.prepareProducer("OrderProducerPython")
    kp.publishEvent(TOPIC_NAME,evt,"orderID")
