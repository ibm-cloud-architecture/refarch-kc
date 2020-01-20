import json,os
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


class KafkaConsumer:

    def __init__(self, kafka_env = 'LOCAL', kafka_brokers = "", kafka_apikey = "", topic_name = "", schema_registry_url = "", autocommit = True):
        self.kafka_env = kafka_env
        self.kafka_brokers = kafka_brokers
        self.kafka_apikey = kafka_apikey
        self.topic_name = topic_name
        self.schema_registry_url = schema_registry_url 
        self.kafka_auto_commit = autocommit

    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    def prepareConsumer(self, groupID = "pythonconsumers"):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
                'group.id': groupID,
                'auto.offset.reset': 'earliest',
                'schema.registry.url': self.schema_registry_url,
                'enable.auto.commit': self.kafka_auto_commit,
        }
        if (self.kafka_env != 'LOCAL' and self.kafka_env != 'MINIKUBE'):
            options['security.protocol'] = 'SASL_SSL'
            options['sasl.mechanisms'] = 'PLAIN'
            options['sasl.username'] = 'token'
            options['sasl.password'] = self.kafka_apikey
        if (self.kafka_env == 'OCP'):
            options['ssl.ca.location'] = os.environ['PEM_CERT']
            options['schema.registry.ssl.ca.location'] = os.environ['PEM_CERT']
        print("This is the configuration for the consumer:")
        print(options)
        self.consumer = AvroConsumer(options)
        self.consumer.subscribe([self.topic_name])
    
    def traceResponse(self, msg):
        print('@@@ pollNextOrder {} partition: [{}] at offset {} with key {}:\n\tvalue: {}'
                    .format(msg.topic(), msg.partition(), msg.offset(), msg.key(), msg.value() ))

    def pollNextEvent(self, keyID, keyname):
        gotIt = False
        while not gotIt:
            try:
                msg = self.consumer.poll(timeout=10.0)
            except SerializerError as e:
                print("Message deserialization failed for {}: {}".format(msg, e))
                break
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                if ("PARTITION_EOF" in msg.error()):
                    gotIt= True
                continue
            self.traceResponse(msg)
            if (msg.key()[keyname] == keyID):
                gotIt = True
    
    def close(self):
        self.consumer.close()