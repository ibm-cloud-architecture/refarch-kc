import os,json,sys
from confluent_kafka import Consumer, KafkaError

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")

CID = "c_1"
TOPIC_NAME="containers"

def parseArguments():
    if len(sys.argv) != 2:
        print("Need to have at least one argument container ID")
        exit(1)
    CID = sys.argv[1]
    print("The arguments are: " , str(sys.argv))

def prepareConsumer():
    options = {
            'bootstrap.servers':  KAFKA_BROKERS,
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': 'es-cert.pem',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'group.id': 'kafka-python-container-test-consumer',
        }
    return Consumer(options)

def traceResponse(msg):
    containerAsStr = msg.value().decode('utf-8')
    print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n\tvalue: {}'
                .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key()), containerAsStr ))
    return containerAsStr

def pollNextContainer(consumer,cid):
    gotIt = False
    containerEvent = {}
    while not gotIt:
        msg = consumer.poll(timeout=10.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            if ("PARTITION_EOF" in msg.error()):
                gotIt= True
            continue
        containerAsStr = traceResponse(msg)
        containerEvent = json.loads(containerAsStr)
        if (containerEvent['payload']['containerID'] == cid):
            gotIt = True
    return containerEvent

if __name__ == '__main__':
    parseArguments()
    consumer = prepareConsumer()
    consumer.subscribe([TOPIC_NAME])
    pollNextContainer(consumer,CID)
    consumer.close()
