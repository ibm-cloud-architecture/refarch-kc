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
At the high level the shipment process flow is suggested and illustrated in the diagram below.

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
## Event Storming Analysis of the container shipping flow 
We use the  [Event Storming](https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/methodology/readme.md) Analysis to move from the high level description of a complex flow above to a specific event timeline with identified bounded contexts each of which could be a target MVP  compnent linked through EDA architecture. 

Event storming is a rapid light weight design process enabling the team of business owners and stake holders, architects and IT specialists to fomalize a complex solution in a clearly communicable event timeline. This step is effective in developing Event microservices linked through an EDA architecture in one or more MVP contexts. 

Steps in an 8 hour Event Storming analysis workshop of  the Container Shipping example are illustrated and described below. 

### Event Storming Step 1: capture the Domain Event Timeline
The initial step in Event Storming Analysis is to capture all events, things which have happened at a point in time, and organize them into a timeline. 
* each event goes on an orange "sticky note" 
* parallel or independent processes may be separated with blue horizontal swim lanes
* critical events indication a new stage in the flow shown with vertical blue bars 

For the global shipment example described at a very high level above we came up with an event timeline shown in the set of diagrams below. 
( The event storming process captures these event timeline sections in charts on walls around the meeting room ) 

#### Container Shipping Event Timeline section 1

<img src="ship-dom-evt1.png" width="700">

This section of the event time line deals with initial contracts to ship container and startup actions - specifically:
* Retailer and Manufacturer settling on an initial order for delivery of goods in a container
* Manufacturer placing order for shipment with Shipping Company 
* Land transport arranged to pick up container and deliver to source port
* Container ship approach source port adjacent to Manufacturer's location 

The events are organized into separate swim lanes for Manufacturer, Retailer and Ship perspectives operating in parallel. 

Some of the value of swimlanes is shown in the separation of ship events as it approaches the source port from container specific events with agreements to ship etc. There is no  time coupling or precise causality between events in these two swim lanes.

The red note is a comment.
* In this case we make the parctical simplification to limit the scenario to shipping complete containers only. This avoids having to deal with additional warehousing, container load aggregation and packing events - together with correspondng unpacking and disaggregation.

#### Container Shipping Event timeline Section 2

<img src="ship-dom-evt2.png" width="700">

This section continues event time line development with a swim lane now focussed on loading and pickup of a specific container at the Manufacturer's location and its delivery to the source port dockside. 

There is a critical event (indicated by vertical blue bar) separating the "source dockside" phase of the solution. Before this critical event we are deling with container specific activities in collecting and transporting the container from Maufacturer's location to dockside. 
In the following dockside phase there are interactions with Customs Officer to get the container cleared for export. 

The Manufacturer will need an empty container (refrigerated if necessary for the shipment of interest) to load the goods into. We show an event for empty container being delivered. The solution is simplified if we assume that the Manufacture has a pool of empty containers always available. Alternatively this can be analyzed fully in some more complete generalized version of the solution. 

When the container arrives at source port dockside it may or may not be intime for the cutoff time required by the Customs Officer to get containers cleared for export before the scheduled departure of a particular container ship. If the cutoff deadline is missed the shipment will need to be rebooked on a later container ship and the client Manufacturer notified of expected delay in delivery. 

#### Container shipping Event Timeline Section 3 

<img src="ship-dom-evt3.png" width="700">

This section continues the event timelines with swim lanes relating to a specific container shipment and also to the movement of a ship potentially carrying thousands of caontainers.

It introduces two new critical events:
* the Customs decision phase of event ends with a specific decision to clear a container for export or not, or posiibly a request for additionalinspecion or documents requiring more decision time 
  * If the container is approved for export it can proceed to loading 
  * if additional time is required for the clearance process, the original booking and expected delivery date may need to be modified 
  * if export clearance is denied, then shipmen is cancelled and requesting parties notified 
* ship enters dock ready to start unloading and loading is a new critical event 
  * previous ship events in Event Timeline section 1 dealt with ship "booking" a load/unload timeslot at a dock in the source port 
  * also getting  national authority or Customs clearance to enter that jurisdiction 
  * now on arrival at the source port anchorage area, the ship requests permission to moor at an available dock facility
  * The critical event when a ship is cleared and moored at a dock hence ready to start unloading and loading containers is the start of the next event phase - container loading (and unloading)
  
#### Container Shipping Event Timeline Section 4

<img src="ship-dom-evt4.png" width="700">

This segment of the event timeline deals with a single swim lane for the ship while it is moored in a dock facility at the source port, is having arriving containers destined for this port unloaded and new containers being loaded at his port. The Port Dock Facility Operator is coordinating many events in he yard to perform load unload operation. These steps - as noted in a red discussion "sticky" in the event storming timeline is repeated for many containers. The time line presened here captures representative high level events. It is straightforward to extend the analysis to open up additional layers of detail touching on operational optimizations and coordination at the cost of addiional complexity not essential to our reference example here.   

Some of the events in this phase are now specialized to address needs of particular ype of container - refrigerated containers - able to maintain specific temperature bounds and to report on their global location and temperature status on a continuous basis. This is a natural outcome of the event Storming analysis involving free parallel capture of event types by a team of individuals with different points of view and interests. Working forward towards one or more MVP implementations of key components of this solution linked through EDA architecture we will need to characterize event types more unifromly end to end - but imposing that level of consistency checking on the initial eventstorming process will slow down progess without providing significan benefit. 

#### Container Shipping Event Timeline Section 5

<img src="ship-dom-evt5.png" width="700">

This segment of the event timeline captures events which occure in the blue water phase of the shipping, after the container ship has left the source port and is travelling owards but has not yet reached the destination port. 

It is divided into two swim lanes the ship perspective and individual container perspectives. The ship perspective includes events relating to the entire ship:
* leaving port 
* reporting its current position 
* deciding to alter planned course to avoid a weather event

The upper swim lane capture events which are specific to a particular container 
* container sensors reporting on geolocation 
* refrigerated container sensors reporting on temperature in the container and power consumption of the refrigeration unit 


#### Container shipping Event Timeline sections 6 and 7 

<img src="ship-dom-evt6.png" width="700">

The remining event time line segments 6 and 7 deal with arrival at the destination port unload of the container and delivery to the Supplier location. At the level of simplification in the reference architecture example, the steps for unloading a container at the destination port, clearing Customs and delivering it to are Retailer location are the symmetric image of the steps to pick up the container from the Manufacture location, clear it through export permissions and load onto the ship. 

For these reason we just provide event timeline digrams for these steps withou going into further explanatory detail. 

<img src="ship-dom-evt7.png" width="700">


### Event Storming Step 2:  identify Commands and event linkages  
After capturing all events for the scenario and organizing them in a time line, the next step in event storming analysis is to identify the triggers for events and causal linkages between events.  

For each identified event in the timeline we ask "What triggered this event to occur?". Expected event trigger types are:
* a human operator makes a decision and issues a command
* some external system or sensor provides a stimulus
* an event results from some policy  - typically automated processing of a precursor event 
* it is is triggered by completion of some determined period of elapsed time.

For each event trigerred by a command 
* the triggering command is identified in a blue (sticky) note 
   * this may become a microservice api in a later implementation 
*  the human persona issuing the command is identified and shown in a yellow note above this 

For events trigerred by processing of some precursor events the trigerring policy explaining when and why his event occurs is summarized in a lilac colored note. Specific causal event linkages are added to the event storming diagram as blue directed (arrow) linkages  

In the following subsections we show the results of command and event linkage analysis for some selected areas of the container shipping example 

#### Container shipping Commands for order placement  

<img src="ship-dom-cmd1.png" width="700">

The above figure can be alterred using event flow:

#### Container Shipping  Event linkages for order placement 

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
