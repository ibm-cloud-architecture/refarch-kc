import os, time, sys, json
from kafka.KcAvroProducer import KafkaProducer
from utils.avroEDAUtils import getContainerEventSchema, getContainerKeySchema

print(" @@@ Executing script: ProduceAvroContainer.py")

####################### READ ENV VARIABLES #######################
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

# Try to read the data schemas location from the environment variables
try:
    DATA_SCHEMAS = os.environ['DATA_SCHEMAS']
except KeyError:
    print("[ERROR] - The DATA_SCHEMAS environment variable needs to be set.")
    exit(1)


####################### VARIABLES #######################
ID = "c01"
TOPIC_NAME="test"

####################### Functions #######################
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
    global TOPIC_NAME, ID
    print("The arguments for the script are: " , str(sys.argv))
    if len(sys.argv) == 3:
        ID = sys.argv[1]
        TOPIC_NAME = sys.argv[2]
    else:
        print("[ERROR] - The ProduceAvroContainer.py script expects two arguments: The container ID and the topic to send the container event to.")
        exit(1)


####################### MAIN #######################
if __name__ == '__main__':
    # Get the Container ID
    parseArguments()
    # Get the avro schemas for the container key and value
    container_event_value_schema = getContainerEventSchema(DATA_SCHEMAS)
    container_event_key_schema = getContainerKeySchema(DATA_SCHEMAS)
    # Create the container event and key to send
    container_event = createContainer(ID)
    print("--- Container event to be published: ---")
    print(json.loads(container_event))
    print("----------------------------------------")
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,SCHEMA_REGISTRY_URL)
    kp.prepareProducer("ProduceAvroContainerPython",container_event_key_schema,container_event_value_schema)
    kp.publishEvent(TOPIC_NAME,container_event,"containerID")
