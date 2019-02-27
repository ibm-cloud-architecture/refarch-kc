# K Container integration tests

This folder includs a set of tests to validate some of the event driven patterns like event sourcing with fail over, CQRS and Saga pattern with recovery and fail over.

## How to proof the event sourcing

To validate event sourcing we want to use the order event topic and add some events for the full order lifecycle. We want to validate the orders are sequential over time, and it is possible to replay the loading of events from time origin and from a last committed offset.

The tests are under the es-it folder. The tests are done un python, so we can also illustrate how to use kafka python client API. To avoid impacting your environment we use a dockerfile to get the basic of python 3.6 and other needed module like kafka, http requests... So build your image using the command:

```
$ docker build -t ibmcase/python .
```
With this image we will be able to run the different tests.


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
