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
    CONTAINER_ANOMALY_RETRY_TOPIC = os.environ['ITGTESTS_CONTAINER_ANOMALY_RETRY_TOPIC']
except KeyError:
    print("The ITGTESTS_CONTAINER_ANOMALY_RETRY_TOPIC environment variable not set... assume local deployment")
    CONTAINER_ANOMALY_RETRY_TOPIC="container-anomaly-retry"

try:
    CONTAINER_ANOMALY_DEAD_TOPIC = os.environ['ITGTESTS_CONTAINER_ANOMALY_DEAD_TOPIC']
except KeyError:
    print("The ITGTESTS_CONTAINER_ANOMALY_DEAD_TOPIC environment variable not set... assume local deployment")
    CONTAINER_ANOMALY_DEAD_TOPIC="container-anomaly-dead"

CONTAINER_ID=str(random.randrange(10000))

number_of_tests = 0
number_of_test_failed = 0
results_file=None

#####################
##### UNIT TEST #####
#####################
class Dlq(unittest.TestCase):

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
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f2.close()
        print("Done\n")

        print("7 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(api_container.items()))
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
        # Set appropriate capacity for this test case
        expected_container['capacity'] = 100
        print("This is the expected container object:")
        print(json.dumps(expected_container, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("3 - Compare Containers")
        # Verify the container object returned by the API endpoint is the expected container object
        self.assertEqual(sorted(expected_container.items()),sorted(container.items()))
        print("Done\n")


    def test4_containerAnomalyRetry(self):
        print('------------------------------------------')
        print('-- [TEST] : ContainerAnomalyRetry Event --')
        print('------------------------------------------\n')

        print("1 - Load the expected ContainerAnomalyRetry event from its json file")
        # Open file to read
        f = open('../data/containerAnomalyRetryEvent.json','r')
        # Load the expected container anomaly retry event
        expected_container_anomaly_retry_event = json.load(f)
        # Verify we have read the files
        self.assertIsNotNone(expected_container_anomaly_retry_event)
        # Prepare expected container anomaly retry event with the containerID
        expected_container_anomaly_retry_event['containerID'] = CONTAINER_ID
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Read the container anomaly retry events from the container-anomaly-retry topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,CONTAINER_ANOMALY_RETRY_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)
        for i in range(3):
            retry = i + 1
            print("Event number "+"{}".format(retry))
            print("Sleeping for "+"{}".format(retry*10)+" seconds.")
            time.sleep(retry*10)
            # Set the retry for the expected container anomaly retry event
            expected_container_anomaly_retry_event['retries'] = retry
            print("Read a container anomaly retry event from the container anomaly retry topic")
            # Read next event in the topic by key
            container_anomaly_retry_event = kc.pollNextEventByKey(CONTAINER_ID)
            # Remove timestamp as it is not important for integration tests and would be hard to calculate
            container_anomaly_retry_event['timestamp'] = ""
            print("This is the container anomaly retry event read from the container anomaly retry topic:")
            print(json.dumps(container_anomaly_retry_event, indent=4, sort_keys=True))
            print("This is the expected container anomaly retry event:")
            print(json.dumps(expected_container_anomaly_retry_event, indent=4, sort_keys=True))
            print("Compare container anomaly events")
            # Verify the container anomaly event received in the topic is the expected container anomaly event
            self.assertEqual(sorted(container_anomaly_retry_event.items()),sorted(expected_container_anomaly_retry_event.items()))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")
    
    def test5_containerAnomalyDead(self):
        print('-----------------------------------------')
        print('-- [TEST] : ContainerAnomalyDead Event --')
        print('-----------------------------------------\n')

        print("1 - Load the expected ContainerAnomalyDead event from its json file")
        # Open file to read
        f = open('../data/containerAnomalyDeadEvent.json','r')
        # Load the expected container anomaly dead event
        expected_container_anomaly_dead_event = json.load(f)
        # Verify we have read the files
        self.assertIsNotNone(expected_container_anomaly_dead_event)
        # Prepare expected container anomaly dead event with the containerID
        expected_container_anomaly_dead_event['containerID'] = CONTAINER_ID
        print("The expected container anomaly dead event is:")
        print(json.dumps(expected_container_anomaly_dead_event, indent=4, sort_keys=True))
        # Close the file
        f.close()
        print("Done\n")

        print("2 - Read the container anomaly dead event from the container-anomaly-dead topic")
        # Create a KafkaConsumer object to interact with Kafka/Event Streams
        kc = KafkaConsumer(KAFKA_ENV,KAFKA_BROKERS,KAFKA_APIKEY,CONTAINER_ANOMALY_DEAD_TOPIC)
        # Verify we have a KafkaConsumer object
        self.assertIsNotNone(kc)
        kc.prepareConsumer()
        # Verify the consumer has been created
        self.assertIsNotNone(kc.consumer)    
        # Read next event in the topic by key
        container_anomaly_dead_event = kc.pollNextEventByKey(CONTAINER_ID)
        # Remove timestamp as it is not important for integration tests and would be hard to calculate
        container_anomaly_dead_event['timestamp'] = ""
        print("This is the container anomaly dead event read from the container anomaly dead topic:")
        print(json.dumps(container_anomaly_dead_event, indent=4, sort_keys=True))
        # Close the Kafka/Event Streams consumer
        kc.close()
        print("Done\n")

        print("3 - Verify the container anomaly dead event")
        # Verify container anomaly dead event read from the topic is as expected
        self.assertEqual(sorted(container_anomaly_dead_event.items()),sorted(expected_container_anomaly_dead_event.items()))
        print("Done\n")


################
##### MAIN #####
################
if __name__ == '__main__':
    unittest.main()
