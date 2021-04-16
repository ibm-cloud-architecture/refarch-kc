import json, os
from confluent_kafka import KafkaError, Producer

class KafkaProducer:

    def __init__(self):
        self.kafka_brokers = os.environ['KAFKA_BROKERS']
        self.kafka_user = os.environ['KAFKA_USER']
        self.kafka_password = os.environ['KAFKA_PASSWORD']
        self.security_protocol = os.environ['SECURITY_PROTOCOL']

    def prepareProducer(self,groupID = "pythonproducers"):
        options ={
                'bootstrap.servers':  self.kafka_brokers,
                'group.id': groupID,
                'security.protocol': self.security_protocol
        }
        if ( self.security_protocol == 'SASL_PLAINTEXT' or self.security_protocol == 'SASL_SSL'):
            options['sasl.username'] = self.kafka_user
            options['sasl.password'] = self.kafka_password
            options['sasl.mechanisms'] = os.environ['SASL_MECHANISM']
        if (os.environ['PEM_CERT']!=""):
            options['ssl.ca.location'] = os.environ['PEM_CERT']

        # Printing out producer config for debugging purposes
        print("[KafkaProducer] - This is the configuration for the producer:")
        print("[KafkaProducer] - -------------------------------------------")
        print('[KafkaProducer] - Bootstrap Server:  {}'.format(options['bootstrap.servers']))
        print('[KafkaProducer] - Security Protocol: {}'.format(options['security.protocol']))
        if (self.security_protocol == 'SASL_PLAINTEXT' or self.security_protocol == 'SASL_SSL'):
            # Obfuscate password
            if (len(self.kafka_password) > 3):
                obfuscated_password = self.kafka_password[0] + "*****" + self.kafka_password[len(self.kafka_password)-1]
            else:
                obfuscated_password = "*******"
            print('[KafkaProducer] - SASL Mechanism:    {}'.format(options['sasl.mechanisms']))
            print('[KafkaProducer] - SASL Username:     {}'.format(options['sasl.username']))
            print('[KafkaProducer] - SASL Password:     {}'.format(obfuscated_password))
            if (options['ssl.ca.location']!=""):
                print('[KafkaProducer] - SSL CA Location:   {}'.format(options['ssl.ca.location']))
        print("[KafkaProducer] - -------------------------------------------")

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
