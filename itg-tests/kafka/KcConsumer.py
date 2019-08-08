import json
from confluent_kafka import Consumer, KafkaError


class KafkaConsumer:

    def __init__(self, kafka_env = 'LOCAL', kafka_brokers = "", kafka_apikey = "", topic_name = "",autocommit = True):
        self.kafka_env = kafka_env
        self.kafka_brokers = kafka_brokers
        self.kafka_apikey = kafka_apikey
        self.topic_name = topic_name
        self.kafka_auto_commit = autocommit

    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    def prepareConsumer(self, groupID = "pythonconsumers"):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
                'group.id': groupID,
                 'auto.offset.reset': 'earliest',
                'enable.auto.commit': self.kafka_auto_commit,
        }
        if (self.kafka_env != 'LOCAL' and self.kafka_env != 'MINIKUBE'):
            options['security.protocol'] = 'SASL_SSL'
            options['sasl.mechanisms'] = 'PLAIN'
            options['sasl.username'] = 'token'
            options['sasl.password'] = self.kafka_apikey
        if (self.kafka_env == 'ICP'):
            options['ssl.ca.location'] = 'es-cert.pem'
        print(options)
        self.consumer = Consumer(options)
        self.consumer.subscribe([self.topic_name])
    
    def traceResponse(self, msg):
        msgStr = msg.value().decode('utf-8')
        print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n\tvalue: {}'
                    .format(msg.topic(), msg.partition(), msg.offset(), str(msg.key()), msgStr ))
        return msgStr

    def pollNextEvent(self, keyID, keyname):
        gotIt = False
        anEvent = {}
        while not gotIt:
            msg = self.consumer.poll(timeout=10.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                if ("PARTITION_EOF" in msg.error()):
                    gotIt= True
                continue
            msgStr = self.traceResponse(msg)
            anEvent = json.loads(msgStr)
            if (anEvent["payload"][keyname] == keyID):
                gotIt = True
        return anEvent
    
    def close(self):
        self.consumer.close()