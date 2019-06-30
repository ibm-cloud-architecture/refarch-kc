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
KEY_NAME = "containerID"
KEY_VALUE = "1"

def parseArguments():
    global KEY_VALUE
    if len(sys.argv) <= 1:
        print("usage container ID to receive")
    KEY_VALUE = sys.argv[1]
    print("The arguments are: " , str(sys.argv))

kafkaConsumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'python-orders-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
})
kafkaConsumer.subscribe([TOPIC_NAME])

def pollNextEvent(aKey):
    print('Start to listen to events')
    gotIt = False
    while not gotIt:
        msg = kafkaConsumer.poll(timeout=10.0)
        if msg is None:
            print("no message")
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        print('@@@ pollNextEvent {} partition: [{}] at offset {} with key {}:\n'
                .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key())))
        msgAsStr = msg.value().decode('utf-8')
        print('@@@ pollNextEvent Received message: {}'.format(msgAsStr))
        eventAsJson = json.loads(msgAsStr)
        if (eventAsJson['payload'][KEY_NAME] == aKey):
            print('@@@@ got the matching expected key ')
            gotIt = True
    return eventAsJson



if __name__ == '__main__':
    parseArguments()
    pollNextEvent(KEY_VALUE)
    kafkaConsumer.close()
