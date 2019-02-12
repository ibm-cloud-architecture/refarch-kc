# From Analysis to Microservice Specifications 
## Goals and outline of section 
This section describes the design step which uses output from the event storming session and subsequent analysis and derives a set of micro services design specification.
The goals for ts design step and the resulting specifications are: 
* Highly modular cloud native microservices 
* Event coupled microservices -  facilitating independent modification and evolution of each microservice separatelys
* Allow for event sourcing – eventual correctness and recovery using event base) 
* Illustrate CQRS and its scaling advantages 

Since we are delivering a demonstration application there will be some simulator / scaffolding / testing services mixed in with the required business processing.
This is a common occurrence in agile development and it may be helpful to show how decision to scope and simplify a particular build and test step interact with decisions relating strictly to microservices design.  

Requirements for scalability, coupling of microservices *only* through the event back bone and eventual correctness   differentiate this step from previous Event Storming and Domain Driven Design activities which were 100% business requirement driven.

## Starting materials generated during Event Storming and Analysis
In this microservices specification step we make use of the following materials generated during Event Storming and analysis of the K Container Shipping example problem: 
* Event Sequence flow
* Events – business description
* Critical events 
* Aggregates and services  
   * Users – roles user stories 
   * Commands
   * Event linkages
   * Policies 
   * Event prediction and probability flows 
* Data  ( Conceptual ) 
The derivation of these material was described in: [Analysis](../analysis/readme.md) .

## Event linked microservices design - structure 
A complete microservices specification ( the target of this design step ) will include specifications of the following: 
* Event Topics 
   * Used to configure the Kafka Event Backbone 
* Event types within each event topic 
* Microservices: 
   * These are finer grained than aggregates 
   * May separate query and command; possibly multiple queries  
   * May Separate whether simulation or business processing component 
   * Demonstration Control –main UI 
   * Scaffolding and testing services  - whether local and cloud versions 
* Microservice specification ( for each identified 
   * Data within Each microservice
   * APIs  ( Synchronous ) 
   * Topics and events Subscribed to
   * Events published / emitted   
* List of end to end interactions 
   * List of logic segments per microservice 
* Recovery processing, scaling 
   * We expect this to be highly patterned and template driven not requiring example-specific design 
With the above information coging of each microservice and other components of the sprint should be straightforward.    


## Steps in the design process 
Here we describe in generic terms, each step in the process of deriving event-linked microservice specification. In following section we will describe in more detail how each of these steps plays out in the specific context of the the K container shipping example.

#### List of generic steps:
*  **Step 1 - limit the context and scope for this particular build / sprint** 
   * we assume that we are developing a particular build for a sprint within some agile development ; additional functions and complexity may be added in later sprints
   * working from the initial list of aggregates, select which aggregates will be included in this build
   * for each aggregate possible choices are: (1) to completely skip and workaround the aggregate in this build (2) to include a full lifecycle implementation of the aggregate (3) to provide a simplified lifecycle implementation - typicall a table of entities is initialized at s.  tart up, and state changes to existing entities are tracked 
   * determine whether there are simulation services or predictive analytics service to be included in the build 
   * identify the external query apis and command apis which this build will support 
   * create entity lifecycle diagrams for entites having a full lifecycle implementation in this build / sprint .
*  **Step 2 -    identify specific microservices in each aggregate**
   *  each aggregate will be implemented as some composition of (1) a command microservice managing state chsnges to the entities in this aggregate (2) possibly one or more separate ( CQRS) query services providing internal or external API query capabilities (3) additional simulation, predictive analytics or User Interface microservices 
   * The command microservice will be built around and manage a collection of active entites for the aggregate, keyed by some primary key
   * The separation of each aggregate into specific component microservices as outlined above, will be a complete list of microservices for the build / sprint. 
   * Identify the data collections, and collection organization (keying structure)  in each command and query microservice for this build.
*  **Step 3 -  generate microservice interaction diagrams for the build** 
   * The diagram will show API calls initiating state change 
   * It shows for each interaction whether this is a synchronous API calls or an asynchronous event interaction via the event backbone
   * The diagram labes each specific event interaction between microservices trigerring a state change
   * ( Typically queries are synchronous API calls since the caller cannot usefully proceeed until a result is returned )
   * From this we can extract: (1)  a complete  list of event types on each topic, with information passed on each event type (2) the complete list of “logic segments” for each microservice processing action in response to an API call or initiating event 
   * When specifying  the “fields” in each event – the CloudEvents standard  in https://github.com/cloudevents/spec should be assumed as a start point 


   
## Example of a reference to an image 
Here is an example of screen I may use:

<img src="kc-order.png" height="630px">
