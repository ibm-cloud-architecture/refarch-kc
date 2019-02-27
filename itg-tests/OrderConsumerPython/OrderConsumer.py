# Trace orders in kafka orders topic
from confluent_kafka import Consumer, KafkaError


c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pyth-orders',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['orders'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()