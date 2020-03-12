# Order Rejection

This use case consist of giving the ability to the Reefer Container Shipment administrator/operator or a customer of its services to reject an order. This could be because the customer wants to wait until they have more fresh goods to get them sent, the final client of those goods do not require these anymore, the Reefer Container Shipment have problems with containers, ships, workforce, etc. Whatever the reason might be, we want to offer all parties of our Event Driven solution the option to reject an order.

A new order successful request flow, implementing the [SAGA pattern](https://ibm-cloud-architecture.github.io/refarch-eda/design-patterns/saga/) for long running transactions, looks like the following sequence diagram:

![saga](images/Slide1.png)

At this point, if any of the interested parties rejects an order, a compensation/rejection process kicks off that looks like the following diagram:

![rejection](images/Slide2.png)

where the Order Command microservice in charge of receiving such rejection request will:

1. Transition the order to **Rejected** state.
2. Emit an **OrderRejected** event so that any other interested party in the overall application take the appropriate action. In our case, the Spring Containers and Voyages microservices will kick off a kind of compensation process whereby the container allocated to the order will get de-allocated and the voyage assigned to the order will get unassigned respectively. As a result, the container will become empty and available for a coming new order as well as the ship making the voyage will get the container's capacity freed up.
