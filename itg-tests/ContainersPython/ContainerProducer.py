import os, time, sys
from kafka.KcProducer import KafkaProducer

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


def createContainer(id):
    print('Create container')
    data = {"containerID": id, 
        "type": "Reefer", 
        "status": "Empty",
        "latitude": 37.80,
        "longitude":  -122.25,
        "capacity": 110, 
        "brand": "itg-brand"}
    containerEvent = {"containerID": id,"timestamp": int(time.time()),"type":"ContainerAdded","payload": data}
    return containerEvent

def parseArguments():
    if len(sys.argv) == 2:
        ID = sys.argv[1]
    else:
        ID = "itg-C02"
    print("The arguments are: " , str(sys.argv))
    return ID


if __name__ == '__main__':
    CID=parseArguments()
    evt = createContainer(CID)
    print(evt)
    kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
    kp.prepareProducer("ContainerProducerPython")
    kp.publishEvent('containers',evt,"containerID")
