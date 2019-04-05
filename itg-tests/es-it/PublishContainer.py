'''
Publish container events for managing the life cycle of container
'''
import sys,os, signal
import time,json
import signal,asyncio
from confluent_kafka import KafkaError, Producer

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    print("The KAFKA_ENV environment variable not set... assume local deployment")
    KAFKA_ENV = "LOCAL"

try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")
    KAFKA_ENV = "LOCAL"


try:
    CA_LOCATION = os.environ['CA_LOCATION']
except KeyError:
    print("The CA_LOCATION environment variable not set... assume NO SSL")
    CA_LOCATION = "/etc/ssl/certs"

CID="C_1"
EVT_TYPE = "ContainerAdded"
TOPIC_NAME = "containers"
producer = {}

def parseArguments():
    if len(sys.argv) <= 1:
        print("Usage containerID eventType")
        exit(1)
    CID= sys.argv[1]
    EVT_TYPE = sys.argv[2]
    print("The arguments are: " , str(sys.argv))

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def prepareProducer():
    producer_options = {
            'bootstrap.servers':  KAFKA_BROKERS,
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': CA_LOCATION,
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'api.version.request': True,
            'log.connection.close' : False,
            'client.id': 'kafka-python-container-test-producer',
    }
    print(producer_options)
    return Producer( producer_options)

def sendContainerEvent(producer,eventType,cid):
    tstamp = int(time.time())
    data = {"timestamp": tstamp,
        "type": eventType,
        "version":"1",
        "containerID": cid,
        "payload": {"containerID": cid, 
                    "type": "Reefer",
                    "status": "atDock",
                    "city": "Oakland",
                    "brand": "brand-reefer",
                    "capacity": 100}}
    dataStr = json.dumps(data)
    try:
        producer.produce(TOPIC_NAME,timestamp=tstamp,key=cid.encode('utf-8'),value=dataStr.encode('utf-8'), callback=delivery_report)
    except Exception as err:
        print('Failed sending message {0}'.format(dataStr))
        print(err)
    producer.flush()

def signal_handler(sig,frame):
    producer.close()
    sys.exit(0)

if __name__ == '__main__':
    parseArguments()
    producer=prepareProducer()
    try:
        sendContainerEvent(producer,EVT_TYPE,CID)
    except KeyboardInterrupt:
        producer.close()
        sys.exit(0)