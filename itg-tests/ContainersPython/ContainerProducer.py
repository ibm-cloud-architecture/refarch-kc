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

def prepareProducer():
    if (KAFKA_ENV == 'LOCAL'):
        options ={
            'bootstrap.servers':  KAFKA_BROKERS,
            'group.id': 'python-container-producer'
        }
    else:
        options = {
            'bootstrap.servers':  KAFKA_BROKERS,
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': 'es-cert.pem',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'group.id': 'python-container-producer',
        }
    return Producer(options)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def publishContainerEvent(eventToSend):
    containerProducer = prepareProducer()
    dataStr = json.dumps(eventToSend)
    containerProducer.produce('containers',key=eventToSend['containerID'],value=dataStr.encode('utf-8'), callback=delivery_report)
    containerProducer.flush()

def createContainer(id):
    print('Create container')
    data = {"containerID": id, 
        "type": "Reefer", 
        "status": "Empty",
        "latitude": 37.80,
        "longitude":  -122.25,
        "capacity": 110, 
        "brand": "itg-brand"}
    containerEvent = {"containerID": id,"timestamp": int(time.time()),"type":"ContainerAdded","payload": data}
    return containerEvent

def parseArguments():
    if len(sys.argv) == 2:
        ID = sys.argv[1]
    else:
        ID = "itg-C02"
    print("The arguments are: " , str(sys.argv))
    return ID

if __name__ == '__main__':
    CID=parseArguments()
    evt = createContainer(CID)
    print(evt)
    publishContainerEvent(evt)
