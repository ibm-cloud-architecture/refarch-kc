'''
Trace container events to validate, events are published
'''
import sys,os
import time,json
import signal,asyncio
from confluent_kafka import KafkaError, Consumer

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")

TOPIC_NAME = "containers"

def parseArguments():
    if len(sys.argv) <= 1:
        print("Set the number of container ID to send and the event type")
    NB_EVENTS = int(sys.argv[1])
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
            'ssl.ca.location': '/etc/ssl/certs',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'api.version.request': True,
            'broker.version.fallback': '0.10.2.1',
            'log.connection.close' : False,
             'client.id': 'kafka-python-container-test-producer',
        }
    return Producer( producer_options)

def sendContainerEvent(producer,eventType,idx):
    for i in range(0,idx,1):
        cid = "c_" + str(i)
        data = {"timestamp": int(time.time()),
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
        producer.produce(TOPIC_NAME,dataStr.encode('utf-8'), callback=delivery_report)
    producer.flush()

if __name__ == '__main__':
    parseArguments()
    producer=prepareProducer()
    sendContainerEvent(producer,EVT_TYPE,NB_EVENTS)