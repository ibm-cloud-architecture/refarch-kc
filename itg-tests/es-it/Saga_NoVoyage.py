# End to end happy path to test the minimum set of Reefer Container Shipment reference application components

###################
##### IMPORTS #####
###################
import unittest, os, json, time, requests, random
from kafka.KcProducer import KafkaProducer
from kafka.KcConsumer import KafkaConsumer

##############################
##### READ ENV VARIABLES #####
##############################
try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
except KeyError:
    print("The KAFKA_BROKERS environment variable needs to be set.")
    exit(1)

# Try to read the Kafka environment from the environment variables
try:
    KAFKA_ENV = os.environ['KAFKA_ENV']
except KeyError:
    KAFKA_ENV='LOCAL'

# Try to read the Kafka API key from the environment variables
try:
    KAFKA_APIKEY = os.environ['KAFKA_APIKEY']
except KeyError:
    print("The KAFKA_APIKEY environment variable not set... assume local deployment")
    KAFKA_APIKEY=''

# Try to read the container microservice url
try:
    CONTAINER_SPRING_MS = os.environ['CONTAINER_SPRING_MS']
except KeyError:
    print("The CONTAINER_SPRING_MS environment variable not set... assume local deployment")
    CONTAINER_SPRING_MS="springcontainerms:8080"

# Try to read the voyage microservice url
try:
    VOYAGE_MS = os.environ['VOYAGE_MS']
except KeyError:
    print("The VOYAGE_MS environment variable not set... assume local deployment")
    VOYAGE_MS="voyages:3000"

# Try to read the order command microservice url
try:
    ORDER_CMD_MS = os.environ['ORDER_CMD_MS']
except KeyError:
    print("The ORDER_CMD_MS environment variable not set... assume local deployment")
    ORDER_CMD_MS="ordercmd:9080"

try:
    ORDER_QUERY_MS = os.environ['ORDER_QUERY_MS']
except KeyError:
    print("The ORDER_QUERY_MS environment variable not set... assume local deployment")
    ORDER_QUERY_MS="orderquery:9080"

try:
    ORDERS_TOPIC = os.environ['ITGTESTS_ORDERS_TOPIC']
except KeyError:
    print("The ITGTESTS_ORDERS_TOPIC environment variable not set... assume local deployment")
    ORDERS_TOPIC="orders"

try:
    ORDER_COMMANDS_TOPIC = os.environ['ITGTESTS_ORDER_COMMANDS_TOPIC']
except KeyError:
    print("The ITGTESTS_ORDER_COMMANDS_TOPIC environment variable not set... assume local deployment")
    ORDER_COMMANDS_TOPIC="orderCommands"

try:
    CONTAINERS_TOPIC = os.environ['ITGTESTS_CONTAINERS_TOPIC']
except KeyError:
    print("The ITGTESTS_CONTAINERS_TOPIC environment variable not set... assume local deployment")
    CONTAINERS_TOPIC="containers"

ORDER_ID=""
CONTAINER_ID=str(random.randrange(10000))

#####################
##### UNIT TEST #####
#####################
class E2EHappyPath(unittest.TestCase):

    def test1_createContainer(self):
        print('-------------------------------')
        print('-- [TEST] : Create container --')
        print('-------------------------------\n')

        print("1 - Load the container event from json file")
        # Open file to read
        f = open('../data/containerCreateEvent.json','r')
        # Load the container from file
        new_container = json.load(f)
        # Verify we have read a container
        self.assertIsNotNone(new_container)
        # Provide the timestamp for the creation time of the container/event
        new_container['timestamp'] = int(time.time())
        # Verify the container has a valid timestamp
        self.assertGreater(new_container['timestamp'],0)
        # Provide the container ID
        new_container['containerID'] = CONTAINER_ID
        new_container['payload']['containerID'] = CONTAINER_ID
        # Setting capacity big enough so that it can not be carried in any of the existing voyages
        new_container['payload']['capacity'] = 50000
        print("Container event to be sent:")
        print(json.dumps(new_container, indent=4, sort_keys=True))
        # Close file
        f.close()
        print("Done\n")

        print("2 - Post container event into the containers topic")
        # Create a KafkaProducer object to interact with Kafka/Event Streams
        kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
        # Verify we have a KafkaProducer object
        self.assertIsNotNone(kp)
        kp.prepareProducer("ProduceContainerPython")
        # Verify the producer has been created
        self.assertIsNotNone(kp.producer)
        # Publish the create container event
        kp.publishEvent(CONTAINERS_TOPIC,new_container,"containerID")
        print("Done\n")

        print("Sleeping for 5 secs\n")
        time.sleep(5)

        print("3 - Read container event from the containers topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,CONTAINERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        read_container = kc.pollNextEventByKey(CONTAINER_ID)
        # A container event object is read
        self.assertIsNotNone(read_container)
        print("This is the container event read:")
        print(json.dumps(read_container, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")
        
        print("4 - Compare events")
        # Verify new container event sent and container event read from the topic are the same
        self.assertEqual(sorted(new_container.items()),sorted(read_container.items()))
        print("Done\n")

        print("5 - Read container object from the container microservice's API endpoint")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/containers")
        # Verify we get a response
        self.assertIsNotNone(response)
        # Load containers from the response
        json_data = json.loads(response.text)
        # Verify we get at least one container back
        self.assertGreater(len(json_data['content']),0)
        # Get latest container
        api_container = json_data['content'][len(json_data['content'])-1]
        # Verify we have a container
        self.assertIsNotNone(api_container)
        print("This is the API container object")
        print(json.dumps(api_container, indent=4, sort_keys=True))
        print("Done\n")

        print("6 - Read expected empty container from json file")
        # Open file to read
        f2 = open('../data/containerEmptyEvent.json','r')
        # Load the expected container object
        expected_container = json.load(f2)
        # Verify we have a container
        self.assertIsNotNone(expected_container)
        # For simplicity, we will not work out timestamps
        expected_container['createdAt'] = api_container['createdAt']
        expected_container['updatedAt'] = api_container['updatedAt']
        # Assign the containerID
        expected_container['id'] = CONTAINER_ID
        # Setting the capacity
        expected_container['capacity'] = 50000
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f2.close()
        print("Done\n")

        print("7 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(api_container.items()))
        print("Done\n")
    
    def test2_createOrder(self):
        print('-----------------------------')
        print('--- [TEST] : Create order ---')
        print('-----------------------------\n')

        # We must use the global scope variable as this value will be used throughout the entire test
        global ORDER_ID

        print("1 - Load the order request from json")
        # Open file to read
        f = open('../data/FreshProductOrder.json','r')
        # Load the order to be sent
        order = json.load(f)
        # Setting appropriate quantity for the order
        # so that it fits into the container created in test1
        # but can not fit into any existing voyage
        order['quantity'] = 50000
        # Close the file
        f.close()
        print("Done\n")
        
        print("2 - Create order by POST to order microservice's API endpoint")
        res = requests.post("http://" + ORDER_CMD_MS + "/orders",json=order)
        # Get the request response as a JSON object
        orderCommand = json.loads(res.text)
        # Grab the orderID from the JSON object
        ORDER_ID = orderCommand['orderID']
        print("The order ID for the order created is: {}".format(ORDER_ID))
        # Verify ORDER_ID is not None
        self.assertIsNotNone(ORDER_ID)
        # Verify ORDER_ID is not an empty string
        self.assertNotEqual(str(ORDER_ID),"")
        print("Done\n")

        print("Sleeping for 5 secs\n")
        time.sleep(10)

        print("3 - Make sure a new order command event was delivered into the orderCommands topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDER_COMMANDS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        order_command = kc.pollNextEventByKey(ORDER_ID)
        # Verify an order command event object is read
        self.assertIsNotNone(order_command)
        # Removing the timestamp from the comparison since we can't know what time exactly it was created at 
        order_command['timestampMillis'] = ""
        print("This is the order command event read from the topic:")
        print(json.dumps(order_command, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("4 - Load the expected order command event from json file")
        # Open file to read
        f = open('../data/orderCommandEvent.json','r')
        # Load expected order command event
        expected_order_command = json.load(f)
        # Verify we have read a container
        self.assertIsNotNone(expected_order_command)
        # Assign the orderID
        expected_order_command['payload']['orderID'] = ORDER_ID
        # Setting the quantity appropriately
        expected_order_command['payload']['quantity'] = 50000
        print("The expected order command event is:")
        print(json.dumps(expected_order_command, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("5 - Verify order command event")
        # Verify order command event read from the topic is as expected
        self.assertEqual(sorted(expected_order_command.items()),sorted(order_command.items()))
        print("Done\n")

        print("Sleeping for 5 secs\n")
        time.sleep(10)

        print("6 - Make sure a new order event was delivered into the orders topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        order = kc.pollNextEventByKey(ORDER_ID)
        # Verify an order command event object is read
        self.assertIsNotNone(order)
        # Removing the timestamp from the comparison since we can't know what time exactly it was created at 
        order['timestampMillis'] = ""
        print("This is the order event read from the topic:")
        print(json.dumps(order, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("7 - Load the expected order event from json file")
        # Open file to read
        f = open('../data/orderCreatedEvent.json','r')
        # Load expected order event
        expected_order = json.load(f)
        # Verify we have read a container
        self.assertIsNotNone(expected_order)
        # Assign orderID
        expected_order['payload']['orderID'] = ORDER_ID
        # Setting quantity appropriately
        expected_order['payload']['quantity'] = 50000
        print("The expected order event is:")
        print(json.dumps(expected_order, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("8 - Verify order event")
        # Verify order event read from the topic is as expected
        self.assertEqual(sorted(expected_order.items()),sorted(order.items()))
        print("Done\n")

    def test3_containerAllocated(self):
        print('------------------------------------')
        print('--- [TEST] : Container Allocated ---')
        print('------------------------------------\n')

        print("1 - Load the expected container assigned to order event on the containers topic from its json files")
        # Open file to read
        f_container = open('../data/containerAssignedToOrderEvent.json','r')
        # Load the expected container
        expected_container = json.load(f_container)
        # Verify we have read the files
        self.assertIsNotNone(expected_container)
        # Prepare expected container assigned to order event with the containerID and orderID
        expected_container['containerID'] = CONTAINER_ID
        expected_container['payload']['orderID'] = ORDER_ID
        expected_container['payload']['containerID'] = CONTAINER_ID
        print("The expected container assigned to order event is:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f_container.close()
        print("Done\n")

        print("2 - Read container assigned to order event from the containers topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,CONTAINERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        container_event = kc.pollNextEventByKey(CONTAINER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        container_event['timestamp'] = ""
        print("This is the container assigned to order event read from the containers topic:")
        print(json.dumps(container_event, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify container assigned to order event")
        # Verify container assigned to order event read from the topic is as expected
        self.assertEqual(sorted(expected_container.items()),sorted(container_event.items()))
        print("Done\n")
        
        print("4 - Load the expected container allocated event on the order topic from its json files")
        # Open file to read
        f_order = open('../data/orderContainerAllocatedEvent.json','r')
        # Load the expected container allocated event
        expected_container_allocated = json.load(f_order)
        # Verify we have read the files
        self.assertIsNotNone(expected_container_allocated)
        # Prepare expected container allocated event with the appropriate orderID and containerID
        expected_container_allocated['orderID'] = ORDER_ID
        expected_container_allocated['payload']['orderID'] = ORDER_ID
        expected_container_allocated['payload']['containerID'] = CONTAINER_ID
        print("The expected container allocated event is:")
        print(json.dumps(expected_container_allocated, indent=4, sort_keys=True))
        # Close the file
        f_order.close()
        print("Done\n")

        print("5 - Read container allocated event from the oder topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        container_allocated = kc.pollNextEventByKey(ORDER_ID)
        # Remove timestamp as it is not important for integrations tests and would be hard to calculate
        container_allocated['timestamp'] = ""
        print("This is the event read from the order topic:")
        print(json.dumps(container_allocated, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("6 - Verify container allocated event")
        # Verify container allocated event read from the topic is as expected
        self.assertEqual(sorted(expected_container_allocated.items()),sorted(container_allocated.items()))
        print("Done\n")


    def test4_voyageNotFound(self):
        print('---------------------------------')
        print('--- [TEST] : Voyage Not Found ---')
        print('---------------------------------\n')

        print("1 - Load the expected voyageNotFound event on the orders topic from its json files")
        # Open file to read
        f = open('../data/voyageNotFoundEvent.json','r')
        # Load the expected event
        expected_event = json.load(f)
        # Verify we have read the file
        self.assertIsNotNone(expected_event)
        # Prepare expected event with the orderID
        expected_event['payload']['orderID'] = ORDER_ID
        print("The expected ContainerNotFound event is:")
        print(json.dumps(expected_event, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Read the VoyageNotFound event from the orders topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        voyage_event = kc.pollNextEventByKey(ORDER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        voyage_event['timestamp'] = ""
        print("This is the ContainerNotFound event read from the orders topic:")
        print(json.dumps(voyage_event, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify VoyageNotFound expected event and read event")
        # Verify ContainerNotFound event read from the topic is as expected
        self.assertEqual(sorted(expected_event.items()),sorted(voyage_event.items()))
        print("Done\n")


    def test5_orderRejected(self):
        print('-------------------------------')
        print('--- [TEST] : Order Rejected ---')
        print('-------------------------------\n')

        print("1 - Load the expected OrderRejected event on the orders topic from its json files")
        # Open file to read
        f = open('../data/orderRejectedNoVoyageEvent.json','r')
        # Load the expected OrderRejected
        expected_order = json.load(f)
        # Verify we have read the files
        self.assertIsNotNone(expected_order)
        # Prepare expected OrderRejected event with the orderID and containerID
        expected_order['payload']['orderID'] = ORDER_ID
        expected_order['payload']['containerID'] = CONTAINER_ID
        print("The expected OrderRejected event is:")
        print(json.dumps(expected_order, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Read OrderRejected event from the orders topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        order_event = kc.pollNextEventByKey(ORDER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        order_event['timestampMillis'] = ""
        print("This is the OrderRejected event read from the orders topic:")
        print(json.dumps(order_event, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify OrderRejected event")
        # Verify OrderRejected event read from the orders topic is as expected
        self.assertEqual(sorted(expected_order.items()),sorted(order_event.items()))
        print("Done\n")


    def test6_orderRejectedREST(self):
        print('------------------------------------')
        print('--- [TEST] : Order Rejected REST ---')
        print('------------------------------------\n')

        print("1 - Load the expected resulting order from order command MS")
        # Open file to read
        f_order_command = open('../data/orderRejectedNoVoyageRESTCommand.json','r')
        # Load the expected order
        expected_order_command = json.load(f_order_command)
        # Verify we have read the file
        self.assertIsNotNone(expected_order_command)
        # Prepare expected order with orderID and containerID
        expected_order_command['orderID'] = ORDER_ID
        expected_order_command['reeferID'] = CONTAINER_ID
        print("The expected resulting order is:")
        print(json.dumps(expected_order_command, indent=4, sort_keys=True))
        # Close the file
        f_order_command.close()
        print("Done\n")
        
        print("2 - Read order from the order command microservice's API endpoint")
        response = requests.get("http://" + ORDER_CMD_MS + "/orders/" + ORDER_ID)
        # Verify we get a response
        self.assertIsNotNone(response)
        # Load the order from the API's response
        order_command = json.loads(response.text)
        print("This is the order from the order command microservice's API")
        print(json.dumps(order_command, indent=4, sort_keys=True))
        print("Done\n")

        print("3 - Verify order")
        # Verify order from the order command API's endpoint is as expected
        self.assertEqual(sorted(expected_order_command.items()),sorted(order_command.items()))
        print("Done\n")

        print("4 - Load the expected resulting order from order query MS")
        # Open file to read
        f_order_query = open('../data/orderRejectedNoVoyageRESTQuery.json','r')
        # Load the expected order
        expected_order_query = json.load(f_order_query)
        # Verify we have read the file
        self.assertIsNotNone(expected_order_query)
        # Prepare expected order with orderID and containerID
        expected_order_query['orderID'] = ORDER_ID
        expected_order_query['containerID'] = CONTAINER_ID
        print("The expected resulting order is:")
        print(json.dumps(expected_order_query, indent=4, sort_keys=True))
        # Close the file
        f_order_query.close()
        print("Done\n")
        
        print("5 - Read order from the order query microservice's API endpoint")
        response = requests.get("http://" + ORDER_QUERY_MS + "/orders/" + ORDER_ID)
        # Verify we get a response
        self.assertIsNotNone(response)
        # Load the order from the order query API's response
        order_query = json.loads(response.text)
        print("This is the order from the order query microservice's API")
        print(json.dumps(order_query, indent=4, sort_keys=True))
        print("Done\n")

        print("6 - Verify order")
        # Verify order from the order query microservice API's is as expected
        self.assertEqual(sorted(expected_order_query.items()),sorted(order_query.items()))
        print("Done\n")



    def test7_containerUnassignedREST(self):
        print('------------------------------------------')
        print('--- [TEST] : Container Unassigned REST ---')
        print('------------------------------------------\n')


        print("1 - Read container object from the container microservice's API endpoint")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/containers")
        # Verify we get a response
        self.assertIsNotNone(response)
        # Get the containers from the response
        json_data = json.loads(response.text)
        # Verify we get at least one container back
        self.assertGreater(len(json_data['content']),0)
        # Get the latest container
        api_container = json_data['content'][len(json_data['content'])-1]
        # For simplicity, we will not work out timestamps
        api_container['createdAt'] = ""
        api_container['updatedAt'] = ""
        print("This is the API container object")
        print(json.dumps(api_container, indent=4, sort_keys=True))
        print("Done\n")

        print("2 - Read expected empty container from json file")
        # Open file to read
        f = open('../data/containerEmptyEvent.json','r')
        # Load the expected loaded container
        expected_empty_container = json.load(f)
        # Verify we have a read a container object
        self.assertIsNotNone(expected_empty_container)
        # Fill in the container ID
        expected_empty_container['id'] = CONTAINER_ID
        # Setting appropriate capacity
        expected_empty_container['capacity'] = 50000
        print("This is the expected container object:")
        print(json.dumps(expected_empty_container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("3 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_empty_container.items()),sorted(api_container.items()))
        print("Done\n")


################
##### MAIN #####
################
if __name__ == '__main__':
    unittest.main()