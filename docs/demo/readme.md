# Demo Script 

This demo script is using the localhost deployment with a mapping of the host name kcsolution to localhost defined in the `/etc/hosts` file. For IBM Cloud change the hostname accordingly. 

Here is how to execute the business process step by step using the demonstration APIs and some scripts. 

## Pre-requisites

Set the following IP address - hostname mapping:

* Hostname `kcsolution` to map to localhost when running on local computer
* 

## Step 1: Manufacturer create an order:

* Go to the http://kcsolution:3110 URL to access the demonstration home page:

![kc-home](kc-home.png)

This page presents the simple version of the business process and the user interface tiles that can be used to simulate the progression within this business process. The grey shadowed tiles have not implemented logic. 

From the `Initiate Orders - Manufacturer` we can have the manufacturer creating a new fresh product order to ship over sea.

To represent different manufacturers the first select box is used to support different scenarios in the future. 'GoodManuf' should be used. 

![](kc-manuf-select.png)

Once the manufacturer is selected a list of existing orders may be displayed. You can add order with the UI, but you can also use a script in the order command microservice project: https://github.com/ibm-cloud-architecture/refarch-kc-order-ms/blob/master/order-command-ms/scripts/createOrder.sh

Below is an example of how to use the createOrder script to add a 'GoodManuf's' order to book a voyage from Oakland to Shanghai for a fresh product:
```
./createOrder.sh localhost:10080 ./orderOacklandToChinaCreate.json

```

![](kc-orders.png)

> There is a lot happening here. The Angular is getting orders using the [orders.service.ts](https://github.com/ibm-cloud-architecture/refarch-kc-ui/blob/master/ui/src/app/features/orders/orders.service.ts) service within the BFF component at the address: `http://localhost:3010/api/orders`.  
The BFF is calling the [Order Query Microservice](https://github.com/ibm-cloud-architecture/refarch-kc-order-ms/tree/master/order-query-ms) via a javascript client code: [getOrders(manuf) function.](https://github.com/ibm-cloud-architecture/refarch-kc-ui/blob/4b9d7d1241eaeeaee7fc01247a35b696f0b6d5b2/server/routes/OrderClient.ts#L12-L25). The Order Query microservice URL is defined in environment variable or defaulted in the config file. It is mapped to the deployed Order service. (e.g. http://ordercmd:9080/orders)

Selecting one order using the `Arrow` icon, allow the user to view the order details:

![](kc-order.png)

As illustrated in the CQRS diagram:

<img src="https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/design-patterns/images/cqrs-es-api.png" width="500px">

the creation of the order goes to the [order command microservice](https://github.com/ibm-cloud-architecture/refarch-kc-order-ms/tree/master/order-command-ms) which publishes a `OrderCreated` event to the `orders` topic and then consumes it to persist the data to its database. See [source code here](https://github.com/ibm-cloud-architecture/refarch-kc-order-ms/blob/6de424c443c05262ae013620f5f11b4a1b2e6f90/order-command-ms/src/main/java/ibm/labs/kc/order/command/service/OrderCRUDService.java#L51-L74)


If you plug a 'orders topic' consumer you can see the following trace with the status of the order being `pending` and the type of event being `OrderCreated`. 

```json
{"payload":{
    "orderID":"1fcccdf2-e29d-4b30-8e52-8116dc2a01ff",
    "productID":"Carrot",
    "customerID":"GoodManuf",
    "quantity":10000,
    "pickupAddress": "...",
    "expectedDeliveryDate":"2019-03-31T13:30Z",
    "status":"pending"},
"type":"OrderCreated",
"version":"1"}

```

## Step 2: K Container Shipment Manager looking at Orders

From the home page goes to the Shipment Inc tile:

![](shipment-inc.png) 

Then the home page lists the current order the shipment company received

![](kc-shipment-home.png)

The status of those events will be modified over time while the order is processed down stream by the voyage and container services. The following sequence diagram illustrates the flow:

![](kc-order-seq-diag.png)  

Looking at the traces in the voyage service
```
voyages_1     |  emitting {"timestamp":1548788544290,"type":"OrderAssigned","version":"1","payload":{"voyageID":100,"orderID":"1fcccdf2-e29d-4b30-8e52-8116dc2a01ff"}}
```

or at the `orders` topic:

```json
{"timestamp":1548792921679,
"type":"OrderAssigned","version":"1",
"payload":{"voyageID":100,"orderID":"1fcccdf2-e29d-4b30-8e52-8116dc2a01ff"}}

```

## Step3: Simulate the ship in blue water

From the home page, select the `Simulate the bluewater` tile. In the main page, select one of the available fleet. As of now, only the North Pacific has data:

![](kc-fleet-select.png)  

The fleet panel lists the boats, their location and status and a map:

![](kc-fleet-home.png)  

Selecting one boat with the edit button, goes to the boat detail view:

![](kc-ship-detail.png)  

You can start a simulation on the ship movement by selecting one of three pre-defined scenarios:

* Fire affecting some containers
* Reefer down
* Boat experiencing a heat wave

![](kc-ship-scenarios.png)  

The command is sent to the Simulator and the boat will start to move and generate container metrics:

![](boat-with-issues.png)  

The simulation implementation is yet not completed. 



