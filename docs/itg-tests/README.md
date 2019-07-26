# Reefer container shipment solution integration tests

The `itg-tests` folder includes a set of tests to validate most of the event-driven microservice patterns like, event sourcing with fail over, CQRS and Saga patterns with recovery and fail over. (See our summary on those patterns [here](https://ibm-cloud-architecture.github.io/refarch-eda/evt-microservices/ED-patterns/))

These integration tests are done in Python to illustrate how to use Kafka python module of [this github](https://github.com/confluentinc/confluent-kafka-python) and because Python is nice to use for writing integration tests.

## pre-requisites

### Building the python environment as docker image

To avoid impacting your environment we use a dockerfile to get the basic of python 3.7.x and other needed modules like kafka, http requests, pytest... So build your python image with all the needed libraries, use the following commands:

```shell
cd docker
docker build -t ibmcase/python .
```

### Ensure all services are running

!!! Note
        This documentation assumes the solution is running within MINIKUBE, but tests will work the same with docker-compose, just replace MINIKUBE with LOCAL as argument of the scripts.

```
kubectl get pods -n greencompute
```

```
NAME                                         READY   STATUS    RESTARTS   AGE
fleetms-deployment-f85cb679d-582pp           1/1     Running   2          14d
kafkabitmani-0                               1/1     Running   1          3d23h
kafkabitmani-zookeeper-0                     1/1     Running   0          3d23h
kcsolution-kc-ui-76b7b4fccf-z85j5            1/1     Running   1          8d
ordercommandms-deployment-857865854f-7mzqs   1/1     Running   0          3d21h
orderqueryms-deployment-778d79d99c-lrgfs     1/1     Running   0          3d21h
postgre-db-postgresql-0                      1/1     Running   2          14d
```

## Run the python environment

With the image `ibmcase/python`, you will be able to run the different integration tests. For example, the following commands will start a bash shell with the python environment, mounting the local filesystem into the docker /home folder, and connect to the same network as the Kafka broker and the other solution components are running into:

```shell
$ pwd
itg-tests
$ ./startPythonEnv.sh MINIKUBE
root@fe61560d0cc4:/# 
```

From this shell, first specify where python should find the new modules, by setting the environment variable `PYTHONPATH`:

```
root@fe61560d0cc4:/# export PYTHONPATH=/home
root@fe61560d0cc4:/# cd /home
```
As the startPythonEnv is mounting the local `itg-tests` folder to the `/home` folder inside the docher container, we can access all the integration tests, and execute them now...

## How to proof the event sourcing

The goal of this test is to illustrate the happy path for event sourcing: all events for an order, are persisted in kafka, in the order of arrival, and a consumer with no offset commit, could run and help to answer to the question: **What happened to the orderId 75?**

We want to validate the order events are sequential over time, and it is possible to replay the loading of events from time origin.

![](es-test.png)

### Replay all events for a given key


1. First start the python docker container, so we can execute any python code. The script connects to the docker network where kafka runs. 

    ```
    cd itg_tests
    ./startPythonEnv.sh MINIKUBE
    ```

    In the bash session, use the following command to ensure python knows how to get our new defined modules like the kafka consumer and producer:
    ```
    export PYTHONPATH=/home
    cd /home/es-it
    ```

1. Start python interpreter with the producer events code with orderID set to 75.

    ```
    $ python ProducerOrderEvents.py 75
    The arguments are:  ['ProducerOrderEvents.py', '75']
    Generate events for 75
    Create order for 75
        1- CreateOrder:{"orderID": "75", "timestamp": 1555149614, "type": "OrderCreated", "payload": {"orderID": "75", "productID": "FreshFoodItg", "customerID": "Customer007", "quantity": 180, "pickupAddress": {"street": "astreet", "city": "Oakland", "country": "USA", "state": "CA", "zipcode": "95000"}, "destinationAddress": {"street": "bstreet", "city": "Beijing", "country": "China", "state": "NE", "zipcode": "09000"}, "pickupDate": "2019-05-25", "expectedDeliveryDate": "2019-06-25"}}
    {'bootstrap.servers': 'kafka1:9092', 'group.id': 'OrderProducerPython'}
    Message delivered to orders [0]
        2- Producer accept the offer so now the order is booked:{"orderID": "75", "timestamp": 1555317000, "type": "OrderBooked", "payload": {"orderID": "75", "productID": "FreshFoodItg", "customerID": "Customer007", "quantity": 180, "pickupAddress": {"street": "astreet", "city": "Oakland", "country": "USA", "state": "CA", "zipcode": "95000"}, "destinationAddress": {"street": "bstreet", "city": "Beijing", "country": "China", "state": "NE", "zipcode": "09000"}, "pickupDate": "2019-05-25", "expectedDeliveryDate": "2019-06-25"}}
    Message delivered to orders [0]
        3- Voyage is assigned to order:{"orderID": "75", "timestamp": 1555317300, "type": "OrderAssigned", "payload": {"orderID": "75", "voyageID": "voyage21"}}
    Message delivered to orders [0]
        4- Allocate Reefer to order:{"orderID": "75", "timestamp": 1555405800, "type": "ContainerAllocated", "payload": {"orderID": "75", "containerID": "c13"}}
    Message delivered to orders [0]
        5- Reefer loaded with goods ready for Voyage:{"orderID": "75", "timestamp": 1557930600, "type": "FullContainerVoyageReady", "payload": {"orderID": "75", "containerID": "c13"}}
    Message delivered to orders [0]
    ```

1. Now we can start the consumer to see the event coming with different time stamps. In a separate `terminal` windows run the command:

    ```
    ./runOrderConsumer.sh MINIKUBE 75
    ```
    
    You should get the following results

    ```
    @@@ pollNextOrder orders partition: [0] at offset 8 with key b'75':
        value: {"orderID": "75", "timestamp": 1555149614, "type": "OrderCreated", "payload": {"orderID": "75", "productID": "FreshFoodItg", "customerID": "Customer007", "quantity": 180, "pickupAddress": {"street": "astreet", "city": "Oakland", "country": "USA", "state": "CA", "zipcode": "95000"}, "destinationAddress": {"street": "bstreet", "city": "Beijing", "country": "China", "state": "NE", "zipcode": "09000"}, "pickupDate": "2019-05-25", "expectedDeliveryDate": "2019-06-25"}}
    @@@ pollNextOrder orders partition: [0] at offset 9 with key b'75':
        value: {"orderID": "75", "timestamp": 1555317000, "type": "OrderBooked", "payload": {"orderID": "75", "productID": "FreshFoodItg", "customerID": "Customer007", "quantity": 180, "pickupAddress": {"street": "astreet", "city": "Oakland", "country": "USA", "state": "CA", "zipcode": "95000"}, "destinationAddress": {"street": "bstreet", "city": "Beijing", "country": "China", "state": "NE", "zipcode": "09000"}, "pickupDate": "2019-05-25", "expectedDeliveryDate": "2019-06-25"}}
    @@@ pollNextOrder orders partition: [0] at offset 10 with key b'75':
        value: {"orderID": "75", "timestamp": 1555317300, "type": "OrderAssigned", "payload": {"orderID": "75", "voyageID": "voyage21"}}
    @@@ pollNextOrder orders partition: [0] at offset 11 with key b'75':
        value: {"orderID": "75", "timestamp": 1555405800, "type": "ContainerAllocated", "payload": {"orderID": "75", "containerID": "c13"}}
    @@@ pollNextOrder orders partition: [0] at offset 12 with key b'75':
        value: {"orderID": "75", "timestamp": 1557930600, "type": "FullContainerVoyageReady", "payload": {"orderID": "75", "containerID": "c13"}}
    ```

1. Stopping with Ctrl-C (it can take time for python to get the keyboard interrupt) and then restarting the same consumer will bring you the same content. We can always answer the question at different time, but still get the same answer. 

The tests are under the `itg-tests/es-it` folder. The testin `es-it/ProducerOrderEvents.py` create the order events, and when combined with an order consumer give you the tracing of the process. The diagram below illustrates this simple environment. 
 

* [EventSourcingTests.py](https://github.com/ibm-cloud-architecture/refarch-kc/blob/master/itg-tests/es-it/EventSourcingTests.py) uses the event backbone, and the order microservices. 

To run the tests set the KAFKA_BROKERS and KAFKA_APIKEY environment variables

### Happy path for the order life cycle

A classical happy path for a event-driven microservice is to receive a command to do something (could be an API operation (POST a new order)), validate the command, create a new event (OrderCreated) and append it to event log, then update its internal state, and may be run side effect like returning a response to the command initiator, or trigger a call to an external service to initiate a business process or a business task.  

Once the python image is build you can use the following command to run the first test that create an order, use Kafka consumer to get the different events and query the Order microservices. The code is documented and should be self-explanatory. The order state diagram is [presented here.](https://ibm-cloud-architecture.github.io/refarch-kc/design/readme/#shipment-order-lifecycle-and-state-change-events)


```shell
. ./setenv.sh
$ docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -v $(pwd):/home --network=docker_default -ti ibmcase/python bash
root@fe61560d0cc4:/# cd home/es-it
root@fe61560d0cc4:/# python EventSourcingTests.py
```

The implementation uses a set of constructs to poll the `orders` topic for events and  timing out if not events are there. Also it needs to filter out previous events and events not related to the created order. 

*The code is deliberatly not optimized. The second test will use a OrderConsumer module to isolate the specific kafka code to consumer orders.*

### Wrong path

One possible bad path, is when the command microservice fail, and needs to recover from failure. In this case it should reload the events from last snapshot up to the time it fails and update its internal states but do not run the side effect. 

To test this path, we create an order and kill the order command service after it generate the first event, while voyage service publishes voyage allocation event.

### First exception no voyage found

If there is no voyage found that matches the source and destination then the order is cancelled. The voyages definition is just a collection of json objects in the [voyage-ms project](https://github.com/ibm-cloud-architecture/refarch-kc-ms/tree/master/voyages-ms).

The test is `CancelledOrderTests.py`. It uses the OrderConsumer module.

### Use transaction to support read-process-write in one atomic operation


## How to proof the SAGA pattern

We want to validate the SAGA pattern to support the long-running, cross microservices, order transactions. The diagram is illustrating the use case we want to proof and tests:

![](./saga-ctx.png)

What we need to proof for the happy path:

* Send a new order to the order microservice via API with all the data to ship fresh goods from two countries separated by ocean
* verify the status of the order is pending
* The unique cross services key is the order ID
* verify orderCreated event was published
* verify voyage was allocated to order
* verify container was allocated to order
* verify ship has new containers added to its plan shipping plan 
* verify the status of the order is assigned

Business exeception error: no container for this type of load is available in this time frame. So the business response will be to keep the order in pending but trigger a business process for a customer representative to be in contact with the manufacturer for a remediation plan. 

* Verify the response to the container service is an OrderUnfulled event.
