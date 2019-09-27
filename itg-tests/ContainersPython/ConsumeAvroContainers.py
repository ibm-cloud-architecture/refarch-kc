import os,sys
from kafka.KcAvroConsumer import KafkaConsumer

print(" @@@ Excuting script: ConsumeAvroContainers.py")

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

# Try to read the schema registry url from the environment variables
try:
    SCHEMA_REGISTRY_URL = os.environ['SCHEMA_REGISTRY_URL']
except KeyError:
    print("[ERROR] - The SCHEMA_REGISTRY_URL environment variable needs to be set.")
    exit(1)

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
    print("The Avro Schema Registry is at: " + SCHEMA_REGISTRY_URL)
    return CID

if __name__ == '__main__':
    CID = parseArguments()
    consumer = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,TOPIC_NAME,SCHEMA_REGISTRY_URL)
    consumer.prepareConsumer()
    consumer.pollNextEvent(CID,'containerID')
    consumer.close()