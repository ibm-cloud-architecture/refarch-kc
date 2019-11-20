import json, os
from confluent_kafka import KafkaError, Producer

class KafkaProducer:

    def __init__(self,kafka_env = 'LOCAL',kafka_brokers = "",kafka_apikey = ""):
        self.kafka_env = kafka_env
        self.kafka_brokers = kafka_brokers
        self.kafka_apikey = kafka_apikey

    def prepareProducer(self,groupID = "pythonproducers"):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
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
        print("[KafkaProducer] - This is the configuration for the producer:")
        print('[KafkaProducer] - {}'.format(options))
        self.producer = Producer(options)

    def delivery_report(self,err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('[ERROR] - [KafkaProducer] - Message delivery failed: {}'.format(err))
        else:
            print('[KafkaProducer] - Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def publishEvent(self, topicName, eventToSend, keyName):
        dataStr = json.dumps(eventToSend)
        self.producer.produce(topicName,key=eventToSend[keyName],value=dataStr.encode('utf-8'), callback=self.delivery_report)
        self.producer.flush()