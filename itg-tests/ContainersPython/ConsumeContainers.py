import os,sys
from kafka.KcConsumer import KafkaConsumer

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

CID = "c_1"
TOPIC_NAME="containers"

def parseArguments():
    if len(sys.argv) != 2:
        print("Need to have at least one argument container ID")
        exit(1)
    CID = sys.argv[1]
    print("The arguments are: " , str(sys.argv))
    print(KAFKA_ENV)
    print(KAFKA_BROKERS)
    print(KAFKA_APIKEY)

if __name__ == '__main__':
    parseArguments()
    consumer = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,TOPIC_NAME)
    consumer.prepareConsumer()
    consumer.pollNextEvent(CID,'containerID')
    consumer.close()