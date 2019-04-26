import os,json,sys
from confluent_kafka import Consumer, KafkaError, Producer

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

TOPIC_NAME='orders'
OID = ''

def parseArguments():
    if len(sys.argv) != 2:
        print("Need to have at least one argument order ID")
        exit(1)
    OID = sys.argv[1]
    print("The arguments are: " , str(sys.argv))

# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
def prepareConsumer():
    if (KAFKA_ENV == 'LOCAL'):
        options ={
            'bootstrap.servers':  KAFKA_BROKERS,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'group.id': 'kafka-python-container-test-consumer'
        }
    else:
        options = {
            'bootstrap.servers':  KAFKA_BROKERS,
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': 'es-cert.pem',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': 'token',
            'sasl.password': KAFKA_APIKEY,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'group.id': 'python-orders-consume',
        }
    return Consumer(options)

def traceResponse(msg):
    orderStr = msg.value().decode('utf-8')
    print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n\tvalue: {}'
                .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key()), orderStr ))
    return orderStr

def pollNextOrder(orderConsumer,orderID):
    gotIt = False
    orderEvent = {}
    while not gotIt:
        msg = orderConsumer.poll(timeout=10.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        orderStr = traceResponse(msg)
        orderEvent = json.loads(orderStr)
        if (orderEvent['payload']['orderID'] == orderID):
            gotIt = True
    return orderEvent

if __name__ == '__main__':
    parseArguments()
    orderConsumer = prepareConsumer()
    orderConsumer.subscribe([TOPIC_NAME])
    pollNextOrder(orderConsumer,OID)
    orderConsumer.close()