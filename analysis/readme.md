# Container Shipment Analysis
This section defines the overall steps in the methodology to analyse a specific global shipping example and derive the Event Driven Solution to address key ( MVP) components occurring in it. We combined some elements of the [Design Thinking](https://www.ibm.com/cloud/garage/content/think/practice_design_thinking/) methodology with the [event storming](https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/methodology/readme.md) and [domain driven design](https://www.ibm.com/cloud/garage/content/code/domain-driven-design/) to extract the following analysis of the business domain.

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

#### Container shipping Commands for order placement and land transport setup

<img src="ship-dom-cmd1.png" width="700">

This diagram shows the  command , agent issuing them and policies triggering events for the order placement and land transport set up ( at manufacturer location )  sections of the event timeline generated in step 1

#### Container Shipping  Event linkages for order placement setup 

<img src="ship-dom-cmd1.2.png" width="700">

The above diagram adds event linkages showing the causality chaining of events 

#### Container Shipping  Commands for pickup  at Manufacture 

<img src="ship-dom-cmd2.png" width="700">

The above diagram is generated for the cmmand and policies associated with pick up of a loaded container from the Manufacturer's location and delivery to the source port dockside 

#### Container shipping Commands  in port to port (Blue water)  section of the event time line

<img src="ship-dom-cmd3.png" width="700">

### Step 3: Decision Data, Predictive Insights and Insight Storming 

Insight storming  - extending the EventStorming workshop to identify and capture insightful predictive analytics - was introduced and described in [Workshop execution Step 8 - Insight](https://github.com/ibm-cloud-architecture/refarch-eda/tree/master/docs/methodology/readme.md) . 

Predictive analytic insights are effectively probabilistic statements about which future events are likely to occur and what are the like properties of those events. They are typicaly generated using models crreated by Data scientists or using Atifical Intalligence (AI) or Machine learning (ML).  Business owners and stakeholders in the Event Driven solution we are realizing are like to have good intuitions on:
* which probabilistic insights are likely to lead to better decision making and action when a particular event occurs
* what sources of information are likely to help create a model to predict this insight 

So in Event Storming for an EDA  system we recommend generalizing the step of identifying data (properties of past definite events) to help make good decision and replacing this with an **Insight Storming** step which will look for: 
* data which will help make good decisions about how to act when an event occurs
* predictive insights which could help guide our actions in response to proactively before some future evnet
* sources of data which are likely to enable the building of reliable predictive insight models 

This additional step of Insight Storming takes advantage of the fact that we already have a time line for the probelm being analysed with all events designed, commands, policies and event linkages already identified, and the business owners and stakeholders in the room whose insights for the business problem enable them to identify potentially valuable predictive insights. 

Working through Insight Storming in this way leads to a business value driven specification of possible predictive analytics opportunities in the solution. Event Driven Architecture provides a nature pattern to models addressing the identified needs. Event Stream Processing analytics infrastructure is then availalable to support scoring of these models and uses of the resulting insights in decision making and action in real time. 

#### Container Shipping  Event Stream Processing diagram - including event stream processing flows
The shipping example includes the case where continuous sensor measurement data is available form each refrigerated conatiner while it is stacked on board the container ship and is in between ports on a blue water phase of the scenario. We show how streaming analytics can process the arriving continuous sensor measures in real - time and to deliver additional capabilites in the EDA solution. 

A diagram for this flow  generated from Insight storming is shown below. 

<img src="ship-dom-insight1.PNG" width="700">

In this diagram it is made clear the the delivery of measured  temperature, probably GPS position, and power consumption of the refrigeration unit for that container is a recurring "continuous" event. Each container might report once a minute; this ensures that an auditable record of container temperature is available from the event bus.

We show a policy test to decide whether the temperature has gone outside the specified range committed to in that shipment contract for the goods in that container. If this violation has occured, this is an ( unusual ) alert event reporting that temperature has gone out of range.
This information is available as data to sme dashboard seen by the shipping company operator who must make the business decision whether the contents of the container aree spoiled. It is likely that involvement of human operator is necessary since this is a business decision with possibly significant $ co0nsequences. It is possible that a bad sensor reading could have been received or that in this contract violation of the temperature range for a very short interval of time is permissable. 

Some stateful analysis of the container temperature reposrt would make the readings more reliable; perhaps there need to be more than one out of rage reading to issue the alert to avoid corrupted data false positives. 

If the business decision is made that the container's contents are spoiled:
* a command is invoked to act on this decision
* the container refrigeration may be powered down ( possible other sensing left active)
* A policy based on e terms and Class of Service of this particular shipment will determine
    * whether a replacement shipment will be initiated and booked 
    * usually shipping and reciving parties need to be notified
    * the shipping company will schedule som salvage or disposal action for the content of the container at next port of call

Each of the actions above will be a event captured in the event bus - trigerring further loosely coupled commands and policies to take defined actions.  
    
 #### Container Shipping Event Stream Processing with predictive Insight flows included
The previous section defined how event stream processing could detect when a shipment was spoiled and trigger recovery actions. But shipping experts in an insight storming session will note that it is much better to predict when a spoilage temperature event is **likely to occur** and to take automated immediate (Real-time) action to avert the spoilage. 

The simplest form of prediction of a temperature likely to go outside of its permissible range is to have checks on whether the temperature is approaching these bounds. If the temperature must stay below T degrees, take corrective action if id reaches T - delta degrees. 

More complex models for predicting temperature, could take into account diurnal variation due to external temperatures, possible predicted external temperatures forecase for the current course of the ship, and whether ther container is stacked above deck and hence particularly exposed to external temperatures. 

We assume that possible corrective action includes resetting the thermostatic controls on the refrigeration unit for the cotainer, possibly resetting the controls which may have drifted from their calibrated settingsetc. 

An sight storming diagram which could be generated from discussion of these potentially useful insights and predictions is shown in the diagram below. 

<img src="ship-dom-insight2.PNG" width="700">

We have added an additional insight - namely that it may be possible to predict from the temperature observed in a container and the trend of poewer consumption ot tha refrigeration unit, that the unit is in danger of failing and should be inspected and possibly services as soon as possible. 

Insights about predicted risk of temperature based spoilage, and prediction of refrigeration unit  probable need for maintenance are phonw in a new color - light blue. These are probabilistic prediction for preperties and likely occurence of futeure events. Loose coupling and reuse of these insights by allowing publish subscribe to insight topics is helpful.  Insights are conceptually different from events sine they are probabilistic predictions for the future rather thsn events which by definition have already happened at some specific point in time.  

### Step 4: Aggregates

<img src="ship-aggr-transport-quote.png" width="700">

<img src="ship-aggr-shipment.png" width="700">

<img src="ship-aggr-transp.png" width="700">

### Step 5: Business context
