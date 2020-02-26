# Spoil order test for the Reefer Container Shipment reference application

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
    CONTAINERS_TOPIC = os.environ['ITGTESTS_CONTAINERS_TOPIC']
except KeyError:
    print("The ITGTESTS_CONTAINERS_TOPIC environment variable not set... assume local deployment")
    CONTAINERS_TOPIC="containers"

try:
    ORDER_ID = os.environ['E2EHappyPath_ORDER_ID']
except KeyError:
    print("The E2EHappyPath_ORDER_ID environment variable not set.")

try:
    CONTAINER_ID = os.environ['E2EHappyPath_CONTAINER_ID']
except KeyError:
    print("The E2EHappyPath_CONTAINER_ID environment variable not set.")

number_of_tests = 0
number_of_test_failed = 0
results_file=None

#####################
##### UNIT TEST #####
#####################
class SpoilOrder(unittest.TestCase):

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

    def test1_disableBPM(self):
        print('--------------------------')
        print('-- [TEST] : Disable BPM --')
        print('--------------------------\n')

        print("1 - Get BPM status")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/bpm/status")
        # Verify we get a response
        self.assertIsNotNone(response)

        print("This is the BPM status: " + response.text)
        print("Done\n")

        print("2 - Check BPM status")
        expected_status="BPM service enabled = true"
        # Check BPM status is true
        self.assertEqual(response.text,expected_status)
        print("Done\n")

        print("3 - Disable BPM")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/bpm/disable")
        # Verify we get a response
        self.assertIsNotNone(response)
        print("This is the BPM status: " + response.text)
        print("Done\n")

        print("4 - Check BPM status")
        expected_status="BPM service enabled = false"
        # Check BPM status is true
        self.assertEqual(response.text,expected_status)
        print("Done\n")

    def test2_sendAnomalyEvents(self):
        print('----------------------------------')
        print('-- [TEST] : Send Anomaly Events --')
        print('----------------------------------\n')

        print("1 - Load Container Anomaly event from file")
        # Open file to read
        f = open('../data/containerAnomalyEvent.json','r')
        # Load container anomaly event
        container_anomaly_event = json.load(f)
        # Verify we have read a file
        self.assertIsNotNone(container_anomaly_event)
        # Assign the containerID
        container_anomaly_event['containerID'] = CONTAINER_ID
        print("The container anomaly event to produce is :")
        print(json.dumps(container_anomaly_event, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Post container anomaly into the containers topic")
        # Create a KafkaProducer object to interact with Kafka/Event Streams
        kp = KafkaProducer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY)
        # Verify we have a KafkaProducer object
        self.assertIsNotNone(kp)
        kp.prepareProducer("ProduceContainerPython")
        # Verify the producer has been created
        self.assertIsNotNone(kp.producer)
        # Publish the container anomaly event
        for i in range(3):
            print('Posting container anomaly event number ' + str(i))
            kp.publishEvent(CONTAINERS_TOPIC,container_anomaly_event,"containerID")
            time.sleep(3)
        print("Done\n")

    def test3_containerMaintenanceNeeded(self):
        print('----------------------------------------------------')
        print('-- [TEST] : Container in MaintenanceNeeded status --')
        print('----------------------------------------------------\n')

        print("1 - Read container object from the container microservice's API endpoint")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/containers/" + CONTAINER_ID)
        # Verify we get an http 200 response
        self.assertEqual(200,response.status_code)
        # Load containers from the response
        container = json.loads(response.text)
        # Verify we don't get an empty item
        self.assertIsNotNone(container)
        print("This is the container: ")
        print(json.dumps(container, indent=4, sort_keys=True))

        print("2 - Read the expected container")
        # Open file to read
        f = open('../data/containerMaintenanceNeeded.json','r')
        # Load the expected container object
        expected_container = json.load(f)
        # Verify we have a container
        self.assertIsNotNone(expected_container)
        # For simplicity, we will not work out timestamps
        expected_container['createdAt'] = container['createdAt']
        expected_container['updatedAt'] = container['updatedAt']
        # Assign the containerID
        expected_container['id'] = CONTAINER_ID
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("3 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(container.items()))
        print("Done\n")

    def test4_containerOrderSpoilt(self):
        print('---------------------------')
        print('-- [TEST] : Order Spoilt --')
        print('---------------------------\n')

        print("1 - Load the expected order spoilt event its json file")
        # Open file to read
        f = open('../data/orderSpoiltEvent.json','r')
        # Load the expected order spoilt event
        expected_order_spoilt_event = json.load(f)
        # Verify we have read the files
        self.assertIsNotNone(expected_order_spoilt_event)
        # Prepare expected container assigned to order event with the containerID and orderID
        expected_order_spoilt_event['orderID'] = ORDER_ID
        expected_order_spoilt_event['payload']['orderID'] = ORDER_ID
        expected_order_spoilt_event['payload']['containerID'] = CONTAINER_ID
        print("The expected container assigned to order event is:")
        print(json.dumps(expected_order_spoilt_event, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Read the order spoilt event from the orders topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,ORDERS_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        # Read next event in the topic by key
        order_spoilt_event = kc.pollNextEventByKey(ORDER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        order_spoilt_event['timestamp'] = ""
        print("This is the order spoilt event read from the orders topic:")
        print(json.dumps(order_spoilt_event, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify the order spoilt event")
        # Verify order spoilt event read from the topic is as expected
        self.assertEqual(sorted(expected_order_spoilt_event.items()),sorted(order_spoilt_event.items()))
        print("Done\n")

        print("4 - Load the expected resulting order for Order Command")
        # Open file to read
        f_order_command = open('../data/orderSpoiltRESTOrderCommand.json','r')
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

        print("5 - Read order from the order command microservice's API endpoint")
        response = requests.get("http://" + ORDER_CMD_MS + "/orders/" + ORDER_ID)
        # Verify we get an http 200 response
        self.assertEqual(200,response.status_code)
        # Load the order from the API's response
        order_command = json.loads(response.text)
        print("This is the order from the order command microservice's API")
        print(json.dumps(order_command, indent=4, sort_keys=True))
        print("Done\n")

        print("6 - Verify order")
        # Verify order from the order command API's endpoint is as expected
        self.assertEqual(sorted(expected_order_command.items()),sorted(order_command.items()))
        print("Done\n")

        print("7 - Load the expected resulting order for Order Query")
        # Open file to read
        f_order_query = open('../data/orderSpoiltRESTOrderQuery.json','r')
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

        print("8 - Read order from the order query microservice's API endpoint")
        response = requests.get("http://" + ORDER_QUERY_MS + "/orders/" + ORDER_ID)
        # Verify we get an http 200 response
        self.assertEqual(200,response.status_code)
        # Load the order from the order query API's response
        order_query = json.loads(response.text)
        print("This is the order from the order command microservice's API")
        print(json.dumps(order_query, indent=4, sort_keys=True))
        print("Done\n")

        print("9 - Verify order")
        # Verify order from the order query microservice API's is as expected
        self.assertEqual(sorted(expected_order_query.items()),sorted(order_query.items()))
        print("Done\n")

    def test5_containerToMaintenance(self):
        print('---------------------------------------')
        print('-- [TEST] : Container to maintenance --')
        print('---------------------------------------\n')

        print("1 - Load the container objet for the post data from file")
        # Open file to read
        f = open('../data/containerToMaintenance.json','r')
        # Load the container object to be sent
        container = json.load(f)
        # Verify we have read a file
        self.assertIsNotNone(container)
        # Set the container ID
        container['containerID'] = CONTAINER_ID
        print('This is the container to set into maintenance:')
        print(json.dumps(container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Set container to maintenance by POST to container microservice's API endpoint")
        res = requests.post("http://" + CONTAINER_SPRING_MS + "/containers/toMaintenance",json=container)
        # Make sure we get http 200 response
        self.assertEqual(200,res.status_code)

    def test6_containerInMaintenance(self):
        print('---------------------------------------------')
        print('-- [TEST] : Container InMaintenance status --')
        print('---------------------------------------------\n')

        print("1 - Read container object from the container microservice's API endpoint")
        # Sleep for 5 seconds to allow the container to get into InMaintenance status
        time.sleep(5)
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/containers/" + CONTAINER_ID)
        # Verify we get an http 200 response
        self.assertEqual(200,response.status_code)
        # Load containers from the response
        container = json.loads(response.text)
        # Verify we get at least one container back
        self.assertIsNotNone(container)
        print("This is the container: ")
        print(json.dumps(container, indent=4, sort_keys=True))

        print("2 - Read the expected container")
        # Open file to read
        f = open('../data/containerInMaintenance.json','r')
        # Load the expected container object
        expected_container = json.load(f)
        # Verify we have a container
        self.assertIsNotNone(expected_container)
        # For simplicity, we will not work out timestamps
        expected_container['createdAt'] = container['createdAt']
        expected_container['updatedAt'] = container['updatedAt']
        # Assign the containerID
        expected_container['id'] = CONTAINER_ID
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("3 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(container.items()))
        print("Done\n")

    def test7_containerOffMaintenance(self):
        print('----------------------------------------')
        print('-- [TEST] : Container off maintenance --')
        print('----------------------------------------\n')

        print("1 - Load the container objet for the post data from file")
        # Open file to read
        f = open('../data/containerOffMaintenance.json','r')
        # Load the container object to be sent
        container = json.load(f)
        # Verify we have read a file
        self.assertIsNotNone(container)
        # Set the container ID
        container['containerID'] = CONTAINER_ID
        print('This is the container to get off maintenance:')
        print(json.dumps(container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Set container off maintenance by POST to container microservice's API endpoint")
        res = requests.post("http://" + CONTAINER_SPRING_MS + "/containers/offMaintenance",json=container)
        # Make sure we get http 200 response
        self.assertEqual(200,res.status_code)

    def test8_containerEmpty(self):
        print('-------------------------------------')
        print('-- [TEST] : Container Empty status --')
        print('-------------------------------------\n')

        print("1 - Read container object from the container microservice's API endpoint")
        # Sleep for 5 seconds to allow the container to get into InMaintenance status
        time.sleep(5)
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/containers/" + CONTAINER_ID)
        # Verify we get an http 200 response
        self.assertEqual(200,response.status_code)
        # Load containers from the response
        container = json.loads(response.text)
        # Verify we get at least one container back
        self.assertIsNotNone(container)
        print("This is the container: ")
        print(json.dumps(container, indent=4, sort_keys=True))

        print("2 - Read the expected container")
        # Open file to read
        f = open('../data/containerEmpty.json','r')
        # Load the expected container object
        expected_container = json.load(f)
        # Verify we have a container
        self.assertIsNotNone(expected_container)
        # For simplicity, we will not work out timestamps
        expected_container['createdAt'] = container['createdAt']
        expected_container['updatedAt'] = container['updatedAt']
        # Assign the containerID
        expected_container['id'] = CONTAINER_ID
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("3 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(container.items()))
        print("Done\n")

    def test9_enableBPM(self):
        print('-------------------------')
        print('-- [TEST] : Enable BPM --')
        print('-------------------------\n')

        print("1 - Get BPM status")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/bpm/status")
        # Verify we get a response
        self.assertIsNotNone(response)
        print("This is the BPM status: " + response.text)
        print("Done\n")

        print("2 - Check BPM status")
        expected_status="BPM service enabled = false"
        # Check BPM status is true
        self.assertEqual(response.text,expected_status)
        print("Done\n")

        print("3 - Enable BPM")
        response = requests.get("http://" + CONTAINER_SPRING_MS + "/bpm/enable")
        # Verify we get a response
        self.assertIsNotNone(response)
        print("This is the BPM status: " + response.text)
        print("Done\n")

        print("4 - Check BPM status")
        expected_status="BPM service enabled = true"
        # Check BPM status is true
        self.assertEqual(response.text,expected_status)
        print("Done\n")


################
##### MAIN #####
################
if __name__ == '__main__':
    unittest.main()
