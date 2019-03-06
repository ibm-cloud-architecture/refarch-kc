import os,json
from confluent_kafka import Consumer, KafkaError, Producer

try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit

# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
orderConsumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'python-orders-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
})
orderConsumer.subscribe(['orders'])

def traceResponse(msg):
    orderStr = msg.value().decode('utf-8')
    print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n\tvalue: {}'
                .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key()), orderStr ))
    return orderStr

def pollNextOrder(orderID):
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