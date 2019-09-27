import os, time, sys
sys.path.append("/data_schemas")
from kafka.KcAvroProducer import KafkaProducer
from utils.avroEDAUtils import getContainerEventSchema, getContainerKeySchema
import json

print(" @@@ Excuting script: ContainerAvroProducer.py")

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
   containerEvent = {"containerID": id,"timestamp": int(time.time()),"type": "ContainerAdded","payload": data}
   print("DONE")
   return json.dumps(containerEvent)

# Parse arguments to get the Container ID
def parseArguments():
    print("The arguments for the script are: " , str(sys.argv))
    if len(sys.argv) == 2:
        ID = sys.argv[1]
    return ID

if __name__ == '__main__':
    # Get the Container ID
    CID = parseArguments()
    # Get the avro schemas for the container key and value
    container_event_value_schema = getContainerEventSchema("/data_schemas/")
    container_event_key_schema = getContainerKeySchema("/data_schemas/")
    # Create the container event and key to send
    container_event = createContainer(CID)
    print("--- Container event to be published: ---")
    print(json.loads(container_event))
    print("----------------------------------------")
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,SCHEMA_REGISTRY_URL)
    kp.prepareProducer("ContainerProducerPython",container_event_key_schema,container_event_value_schema)
    kp.publishEvent(TOPIC_NAME,container_event,"containerID")
