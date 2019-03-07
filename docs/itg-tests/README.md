# K Container integration tests

This folder includes a set of tests to validate some of the event-driven microservice patterns like, event sourcing with fail over, CQRS and Saga pattern with recovery and fail over.

These code samples are using Python to illustrate how to use Kafka python module from [this github.](https://github.com/confluentinc/confluent-kafka-python)

## Building the python environment as docker image

To avoid impacting your environment we use a dockerfile to get the basic of python 3.6 and other needed modules like kafka, http requests... So build your image using the following command under current folder `itg-tests`:

```shell
$ docker build -t ibmcase/python .
```
With this image we will be able to run the different tests. For example the following commands will start a bash shell with the python environment, mounting the local filesystem into the docker /home folder, and connect to the same network as the Kafka broker and other KC solution components are running in:

```shell
$ pwd
itg-tests
. ./setenv.sh
$ docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -v $(pwd):/home --network=docker_default -ti ibmcase/python bash
root@fe61560d0cc4:/# 
```
From this shell we can execute our tests.

## How to proof the event sourcing

To validate event sourcing we want to use the order event topic (named `orders`) and add some events to cover the full order lifecycle. We want to validate the order events are sequential over time, and it is possible to replay the loading of events from time origin or from a last committed offset.

The tests are under the es-it folder. The tests are done in python, so we can also illustrate how to use kafka python client API. 

### Happy path for the order life cycle

Once the python image is build you can use the following command to run the first test that create an order, use Kafka consumer to get the different events and query the Order microservices. The code is documented and should be self-explanatory. The state diagram is [here](https://ibm-cloud-architecture.github.io/refarch-kc/design/readme/#shipment-order-lifecycle-and-state-change-events)


```shell
. ./setenv.sh
$ docker run -e KAFKA_BROKERS=$KAFKA_BROKERS -v $(pwd):/home --network=docker_default -ti ibmcase/python bash
root@fe61560d0cc4:/# cd home/es-it
root@fe61560d0cc4:/# python EventSourcingTests.py
```

The implementation uses a set of constructs to poll the topic and may be timing out. Also it needs to filter out previous events and events not related to the created order. 

*The code is deliveratly not optimized. The second test will use a OrderConsumer module to isolate the specific kafka code to consumer orders.*

### First exception no voyage found

If there is no voyage found that matches the source and destination then the order is cancelled. The voyages definition is just a collection of json objects in the [voyage-ms project](https://github.com/ibm-cloud-architecture/refarch-kc-ms/tree/master/voyages-ms).

The test is `CancelledOrderTests.py`. It uses the OrderConsumer module.

### Replay all events for a given key


### Use transaction to support read-process-write in one atomic operation


## How to proof the SAGA pattern

We want to validate the SAGA pattern to support the long-running, cross microservices, order transactions. The diagram is illustrating the use case we want to proof and tests:

![](docs/saga-ctx.png)

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
