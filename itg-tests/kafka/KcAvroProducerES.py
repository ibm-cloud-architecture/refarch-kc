import json,os
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroProducer

class KafkaProducer:

    def __init__(self,kafka_env = 'LOCAL',kafka_brokers = "",kafka_apikey = "",schema_registry_url = ""):
        self.kafka_env = kafka_env
        self.kafka_brokers = kafka_brokers
        self.kafka_apikey = kafka_apikey
        self.schema_registry_url = schema_registry_url

    def prepareProducer(self,groupID = "pythonproducers",key_schema = "", value_schema = ""):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
                'schema.registry.url': self.schema_registry_url,
                'group.id': groupID
        }
        # We need this test as local kafka does not expect SSL protocol.
        if (self.kafka_env != 'LOCAL'):
            options['security.protocol'] = 'SASL_SSL'
            options['sasl.mechanisms'] = 'PLAIN'
            options['sasl.username'] = 'token'
            options['sasl.password'] = self.kafka_apikey
        if (self.kafka_env == 'OCP'):
            options['ssl.ca.location'] = os.environ['PEM_CERT']
            options['schema.registry.ssl.ca.location'] = os.environ['PEM_CERT']
        print("--- This is the configuration for the producer: ---")
        print(options)
        print("---------------------------------------------------")
        self.producer = AvroProducer(options,default_key_schema=key_schema,default_value_schema=value_schema)

    def delivery_report(self,err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('[ERROR] - Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def publishEvent(self, topicName, value, key):
        # Important: value DOES NOT come in JSON format from ContainerAvroProducer.py. Therefore, we must convert it to JSON format first
        self.producer.produce(topic=topicName,value=json.loads(value),key=json.loads(key), callback=self.delivery_report)
        self.producer.flush()