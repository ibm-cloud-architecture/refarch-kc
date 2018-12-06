# Container Shipment Analysis
This section defines the overall steps in the methodology to analyse a specific global shipping example and derive the Event Driven Solution to address key ( MVP) components occurring in it.
## Output from Domain Driven Design workshop
From the design thinking workshop we extracted the following artifacts:
* a persona list
* the MVP hills
### Personas for each stakeholder
We develop personas for each of the business stakeholders to better understand their work environment, motivations and challenges.  Personas helps to capture the decisions and questions that these stakeholders must address with respect to the targeted key business initiative.

Persona name | Objectives | Challenges
--- | --- | ---
Retailer |Receive shipped goods on time, on date contracted with manufacturer <br>Receive assurance that temperature sensitive goods have remained with bounds| Late delivery may miss market opportunity <br> long delivery time makes market opportunitiy prediction more difficult
Manufacturer |Good enough estimates of shipment times from Shipment Company to close sale and delivery with Retailer<br>Pickup of containers by land transporter <br> Timely delivery of container to Retailer as contracted with Shipment company <br> Able to get information on current location and state of container in transit| Contract with Shipment company will include timing estimates and penalty clauses <br> must update Retailer as sonn as schedule changes known <br> Must receive and communicate to retailer assurance on history of temperature sensitive goods  
Shipping Company |Provide good enough estimates of shipment time to close shipment contract with Manufacturer<br>Execute shipment contracts on time profitably ( with minimal cost)|Fixed ship and itinerary schedule <br> variability in ship leg travel times and costs <br> variability in port congestion and load / unload times at dock <br> variability in Land transport timings 
Land Transporter |Pick up and drop off containers at times and locations agreed with Shipment company |May be short notice requests <br> may actually use bids in a market to resolve at lowest cost best response etc.
Port Dock Operator |Load and unload containers from docked ship as specified by Shipping Company with minimal time and effort <br> free up dock asset quickly to become available for next ship | Highly complex sequence of operation in Dockyard to be coordinated to minimize effort and time 
Customs Officer|Clear containers for export and assess duty on import containers|Depends on quality of manifest and certification of origin documentation for each container from Manufacturer 
### MVP Hills 
The challenges listed in the persona table above identify a possible set of MVP hills for this end to end solution. The event storming methodology described below  will lead to picking out speicif subareas of the solution with most value as initial MVPs.
## High level View of the Shipment Process flow
At the high level the shipment process flow is suggested and illustrated in the diagram below:

![](shipment-bp.png)

For the purposes of showing how to architect a reference EDA solution we select on a simple subcase of all actual and possible variations of the global container flow. Very high level steps in this flow are as follows: 
1. Retailer and Manufacturer interact to create agreement to deliver specific goods in a container from Manufacturers location to Retailers location with an expected arrival date 
1. Manufacturer places shipping order with Shipping Company to pickup Container and deliver as expected above
1. Shipping Company arranges for land transport to pick up loaded container and required documentation from Manufacturer and deliver the container to dockside  at source port ( adjacet to Maufacturer) for loading onto container ship 
1. Shipping company works with Customs Officer at source port to clear outbound container for export 
1. When Container Ship is in dock at source port Shipping company arranges with  Port Dock Operator to load and unload containers at this port 
1. Loaded container ship leaves dock in source port adjacent to Manufacturer and sails to destination port 
1. Container ship arrives at destination port (adjacent to Retailer) and queues to enter Port Docking area 
1. Shipment company arranges with Port Docking Operator to unload specific containers needed at this port and reload additional ones for next shipping leg
1. Shipment company works with Import Export office at destination port to clear and collect any import duties 
1. Shipment company works with Land Transporter at destination port to pick up container and deliver to Retailer 
1. Container is delivered by Land Transporter to Retailer's location - transaction is complete 
## Event Storming Method for quick clear definition and communication of complex process
### Step 1: Domain Events
From the business context description above, we started the [Event Storming](https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/methodology/readme.md) Analysis to build the following events timeline. The process start with a request for quote so a `delivery estimate time and cost requested` event occurs.

<img src="ship-dom-evt1.png" width="700">

Three swim lanes were quickly added to the model, after the event storming activity so we can organize event sequencing and parallelism.

<img src="ship-dom-evt2.png" width="700">

<img src="ship-dom-evt3.png" width="700">

<img src="ship-dom-evt4.png" width="700">

<img src="ship-dom-evt5.png" width="700">

<img src="ship-dom-evt6.png" width="700">

<img src="ship-dom-evt7.png" width="700">


### Step 2: Commands

<img src="ship-dom-cmd1.png" width="700">

The above figure can be alterred using event flow:

<img src="ship-dom-cmd1.2.png" width="700">

<img src="ship-dom-cmd2.png" width="700">

<img src="ship-dom-cmd3.png" width="700">

<img src="ship-dom-cmd4.png" width="700">

### Step 3: Aggregates

<img src="ship-aggr-transport-quote.png" width="700">

<img src="ship-aggr-shipment.png" width="700">

<img src="ship-aggr-transp.png" width="700">

### Step 4: Business context

### Step 5: Data
