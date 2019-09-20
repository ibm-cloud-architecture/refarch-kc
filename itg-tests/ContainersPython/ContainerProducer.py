import os, time, sys
from kafka.KcProducer import KafkaProducer

print(" @@@ Excuting script: ContainerProducer.py")

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
ID = "c_1"
TOPIC_NAME="containers"

# Create a default container
def createContainer(id):
    print('Creating container...', end ='')
    data = {"containerID": id, 
        "type": "Reefer", 
        "status": "Empty",
        "latitude": 37.80,
        "longitude":  -122.25,
        "capacity": 110, 
        "brand": "itg-brand"}
    containerEvent = {"containerID": id,"timestamp": int(time.time()),"type":"ContainerAdded","payload": data}
    print("DONE")
    return containerEvent

# Parse arguments to get the Container ID
def parseArguments():
    print("The arguments for the script are: " , str(sys.argv))
    if len(sys.argv) == 2:
        ID = sys.argv[1]
    return ID


if __name__ == '__main__':
    CID = parseArguments()
    evt = createContainer(CID)
    print("Container event to be published:")
    print(evt)
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
    kp.prepareProducer("ContainerProducerPython")
    kp.publishEvent(TOPIC_NAME,evt,"containerID")
