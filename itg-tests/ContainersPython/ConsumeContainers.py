import os,sys
from kafka.KcConsumer import KafkaConsumer

print(" @@@ Excuting script: ConsumeContainers.py")

# Try to read the Kafka broker from the environment variables
try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("[ERROR] - The KAFKA_BROKERS environment variable needs to be set.")
    exit(1)

# Try to read the Kafka API key from the environment variables
try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")

# Try to read the Kafka environment from the environment variables
try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    KAFKA_ENV='LOCAL'

# Default values
CID = "c_1"
TOPIC_NAME="containers"

# Parse arguments to get the container ID to poll for
def parseArguments():
    print("The arguments for the script are: " , str(sys.argv))
    if len(sys.argv) != 2:
        print("[ERROR] - Need to have at least one argument container ID")
        exit(1)
    CID = sys.argv[1]
    print("The Kafka environment is: " + KAFKA_ENV)
    print("The Kafka brokers are: " + KAFKA_BROKERS)
    print("The Kafka API key is: " + KAFKA_APIKEY)
    return CID

if __name__ == '__main__':
    CID = parseArguments()
    consumer = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,TOPIC_NAME)
    consumer.prepareConsumer()
    consumer.pollNextEvent(CID,'containerID')
    consumer.close()