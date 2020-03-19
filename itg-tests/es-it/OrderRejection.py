# Order Rejection test case of Reefer Container Shipment reference application components

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
    ORDER_COMMANDS_TOPIC="order-commands"

try:
    CONTAINERS_TOPIC = os.environ['ITGTESTS_CONTAINERS_TOPIC']
except KeyError:
    print("The ITGTESTS_CONTAINERS_TOPIC environment variable not set... assume local deployment")
    CONTAINERS_TOPIC="containers"

try:
    CONTAINER_ID = os.environ['SagaNoVoyage_CONTAINER_ID']
except KeyError:
    print("The SagaNoVoyage_CONTAINER_ID environment variable not set.")

ORDER_ID=""

number_of_tests = 0
number_of_test_failed = 0
results_file=None

#####################
##### UNIT TEST #####
#####################
class OrderRejection(unittest.TestCase):

    ########################################## Reporting ############################################
    @classmethod
    def setUpClass(cls):
        global results_file
        results_file = open("/tmp/results.txt","a")
        results_file.write('TEST CASE - ' + cls.__name__ + '\n')
        results_file.write('-----------------------------------\n')

    def setUp(self):
        global number_of_tests
        number_of_tests += 1
        results_file.write(self.id().split('.')[2])

    def tearDown(self):
        global number_of_test_failed
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        ok = not error and not failure
        if not ok:
            results_file.write('...FAILED\n')
            number_of_test_failed += 1
        else:
            results_file.write('...OK\n')

    @classmethod
    def tearDownClass(cls):
        global results_file
        results_file.write('-----------------------------------\n')
        results_file.write('PASSED: ' + str(number_of_tests) + '\n')
        results_file.write('FAILED: ' + str(number_of_test_failed) + '\n\n')
        results_file.close()

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    #################################################################################################

    def test1_createOrder(self):
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

        print("3 - Make sure a new order command event was delivered into the order-commands topic")
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
        print("The expected order event is:")
        print(json.dumps(expected_order, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("8 - Verify order event")
        # Verify order event read from the topic is as expected
        self.assertEqual(sorted(expected_order.items()),sorted(order.items()))
        print("Done\n")

    def test2_containerAllocated(self):
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
        ### Again, for this scenario, we fill up the expected container ID with the actual container ID allocated
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


    def test3_voyageAssigned(self):
        print('--------------------------------')
        print('--- [TEST] : Voyage Assigned ---')
        print('--------------------------------\n')

        print("1 - Load the expected voyage assigned event on the order topic from its json files")
        # Open file to read
        f_voyage = open('../data/orderVoyageAssignedEvent.json','r')
        # Load the expected voyage assigned event
        expected_voyage_assigned = json.load(f_voyage)
        # Verify we have read the files
        self.assertIsNotNone(expected_voyage_assigned)
        # Prepare expected voyage assigned event with orderID
        expected_voyage_assigned['payload']['orderID'] = ORDER_ID
        print("The expected voyage assigned event is:")
        print(json.dumps(expected_voyage_assigned, indent=4, sort_keys=True))
        # Close the file
        f_voyage.close()
        print("Done\n")

        print("2 - Read voyage assigned from oder topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        voyage_assigned = kc.pollNextEventByKey(ORDER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        voyage_assigned['timestamp'] = ""
        print("This is the event read from the order topic:")
        print(json.dumps(voyage_assigned, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify voyage assigned event")
        # Verify voyage assigned event read from the topic is as expected
        self.assertEqual(sorted(expected_voyage_assigned.items()),sorted(voyage_assigned.items()))
        print("Done\n")


    def test4_orderAssignedREST(self):
        print('------------------------------------')
        print('--- [TEST] : Order Assigned REST ---')
        print('------------------------------------\n')

        print("1 - Load the expected resulting order for Order Command")
        # Open file to read
        f_order_command = open('../data/orderRESTOrderCommand.json','r')
        # Load the expected order command
        expected_order_command = json.load(f_order_command)
        # Verify we have read the file
        self.assertIsNotNone(expected_order_command)
        # Prepare expected container allocated event with orderID and containerID
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

        print("4 - Load the expected resulting order for Order Query")
        # Open file to read
        f_order_query = open('../data/orderRESTOrderQuery.json','r')
        # Load the expected order object for the order query microservice
        expected_order_query = json.load(f_order_query)
        # Verify we have read the file
        self.assertIsNotNone(expected_order_query)
        # Prepare expected container allocated event with orderID and containerID
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
        print("This is the order from the order command microservice's API")
        print(json.dumps(order_query, indent=4, sort_keys=True))
        print("Done\n")

        print("6 - Verify order")
        # Verify order from the order query microservice API's is as expected
        self.assertEqual(sorted(expected_order_query.items()),sorted(order_query.items()))
        print("Done\n")


    def test5_orderRejected(self):
        print('-------------------------------')
        print('--- [TEST] : Order Rejected ---')
        print('-------------------------------\n')

        print("1 - Reject order by POST to order microservice's API endpoint")
        res = requests.post("http://" + ORDER_CMD_MS + "/orders/reject/" + ORDER_ID)
        # Verify the post request has been successful
        self.assertEqual(res.status_code,200)
        print("Done\n")

        print("Sleeping for 5 secs\n")
        time.sleep(10)

        print("2 - Make sure a new reject order command event was delivered into the order-commands topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDER_COMMANDS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        reject_order_command = kc.pollNextEventByKey(ORDER_ID)
        # Verify an order command event object is read
        self.assertIsNotNone(reject_order_command)
        # Removing the timestamp from the comparison since we can't know what time exactly it was created at
        reject_order_command['timestampMillis'] = ""
        print("This is the order command event read from the topic:")
        print(json.dumps(reject_order_command, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Load the expected reject order command event from json file")
        # Open file to read
        f = open('../data/rejectOrderCommandEvent.json','r')
        # Load expected order command event
        expected_reject_order_command = json.load(f)
        # Verify we have read a container
        self.assertIsNotNone(expected_reject_order_command)
        # Assign the orderID
        expected_reject_order_command['payload']['orderID'] = ORDER_ID
        expected_reject_order_command['payload']['reeferID'] = CONTAINER_ID
        print("The expected reject order command event is:")
        print(json.dumps(expected_reject_order_command, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("4 - Verify order command event")
        # Verify order command event read from the topic is as expected
        self.assertEqual(sorted(expected_reject_order_command.items()),sorted(reject_order_command.items()))
        print("Done\n")

        print("Sleeping for 5 secs\n")
        time.sleep(10)

        print("5 - Load the expected OrderRejected event on the orders topic from its json files")
        # Open file to read
        f = open('../data/orderRejected.json','r')
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

        print("6 - Read OrderRejected event from the orders topic")
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

        print("7 - Verify OrderRejected event")
        # Verify OrderRejected event read from the orders topic is as expected
        self.assertEqual(sorted(expected_order.items()),sorted(order_event.items()))
        print("Done\n")


    def test6_orderRejectedREST(self):
        print('------------------------------------')
        print('--- [TEST] : Order Rejected REST ---')
        print('------------------------------------\n')

        print("1 - Load the expected resulting order from order command MS")
        # Open file to read
        f_order_command = open('../data/orderRejectedRESTCommand.json','r')
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
        f_order_query = open('../data/orderRejectedRESTQuery.json','r')
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


    def test8_voyageCompensated(self):
        print('-----------------------------------')
        print('--- [TEST] : Voyage compensated ---')
        print('-----------------------------------\n')

        print("1 - Read voyages from the voyages microservice's API endpoint")
        response = requests.get("http://" + VOYAGE_MS + "/voyage")
        # Verify we get a response
        self.assertIsNotNone(response)
        voyages = json.loads(response.text)
        # Verify we get 4 voyages back
        self.assertEqual(len(voyages),4)
        print("This are the voyages from the voyages microservice's API")
        print(json.dumps(voyages, indent=4, sort_keys=True))
        print("Done\n")

        print("2 - Compare voyages")
        # Verify expected voyage free capacity
        for x in range(4):
            voyage = voyages[x]
            if voyage['voyageID'] == "101":
                self.assertEqual(voyage['freeCapacity'],900)
        print("Done")


################
##### MAIN #####
################
if __name__ == '__main__':
    unittest.main()
