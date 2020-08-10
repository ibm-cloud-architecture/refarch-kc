import json, os
from confluent_kafka import KafkaError, Producer

class KafkaProducer:

    def __init__(self,kafka_env = 'LOCAL',kafka_brokers = "",kafka_user = "", kafka_password = ""):
        self.kafka_env = kafka_env
        self.kafka_brokers = kafka_brokers
        self.kafka_user = kafka_user
        self.kafka_password = kafka_password

    def prepareProducer(self,groupID = "pythonproducers"):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
                'group.id': groupID
        }
        # We need this test as local kafka does not expect SSL protocol.
        if (self.kafka_env != 'LOCAL'):
            options['security.protocol'] = 'SASL_SSL'
            options['sasl.mechanisms'] = 'PLAIN'
            options['sasl.username'] = self.kafka_user
            options['sasl.password'] = self.kafka_password
        if (self.kafka_env == 'OCP'):
            options['sasl.mechanisms'] = 'SCRAM-SHA-512'
            options['ssl.ca.location'] = os.environ['PEM_CERT']
        
        # Printing out producer config for debugging purposes        
        print("[KafkaConsumer] - This is the configuration for the consumer:")
        print("[KafkaConsumer] - -------------------------------------------")
        print('[KafkaConsumer] - Bootstrap Server:  {}'.format(options['bootstrap.servers']))
        if (self.kafka_env != 'LOCAL'):
            # Obfuscate password
            if (len(self.kafka_password) > 3):
                obfuscated_password = self.kafka_password[0] + "*****" + self.kafka_password[len(self.kafka_password)-1]
            else:
                obfuscated_password = "*******"
            print('[KafkaConsumer] - Security Protocol: {}'.format(options['security.protocol']))
            print('[KafkaConsumer] - SASL Mechanism:    {}'.format(options['sasl.mechanisms']))
            print('[KafkaConsumer] - SASL Username:     {}'.format(options['sasl.username']))
            print('[KafkaConsumer] - SASL Password:     {}'.format(obfuscated_password))
            if (self.kafka_env == 'OCP'): 
                print('[KafkaConsumer] - SSL CA Location:   {}'.format(options['ssl.ca.location']))
        print("[KafkaConsumer] - -------------------------------------------")

        # Creating the producer
        self.producer = Producer(options)

    def delivery_report(self,err, msg):
        # Called once for each message produced to indicate delivery result. Triggered by poll() or flush().
        if err is not None:
            print('[ERROR] - [KafkaProducer] - Message delivery failed: {}'.format(err))
        else:
            print('[KafkaProducer] - Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def publishEvent(self, topicName, eventToSend, keyName):
        dataStr = json.dumps(eventToSend)
        self.producer.produce(topicName,key=eventToSend[keyName],value=dataStr.encode('utf-8'), callback=self.delivery_report)
        self.producer.flush()