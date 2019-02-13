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

### List of generic steps:
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
   * The diagram labels each specific event interaction between microservices trigerring a state change
   * ( Typically queries are synchronous API calls since the caller cannot usefully proceeed until a result is returned )
   * From this we can extract: (1)  a complete  list of event types on each topic, with information passed on each event type (2) the complete list of “logic segments” for each microservice processing action in response to an API call or initiating event 
   * When, at the next level of detail, the individual fields in each event are specified and typed, the CloudEvents standard  in https://github.com/cloudevents/spec should be assumed as a start point 
*  **Step 4 - specify recovery approach in case a microservice fails**
   * If a microservice fails it will need to recover its internal state date by resubscribing to one or more topics on the event bus  
   * In general, commamd and query microservices will have a standard pattern for doing this 
   * Any custom event filtering and service specific logic should be specified 

### Concepts and rationale underlying this design approach
* What is the difference between event information stored in the event backbone and state data stored in the microservices ?
   * the event information stored persistently in the event backbone is organized by topic and, within each topic, entirely by event time-of-occurrence.
   * the state information in a command microservice is a list (collection) of  all **currently active** entities of the owning aggregate ( e.g. all orders, all voyages etc ) and the **current** state of each such entity 
   * each command microservice will consist of a collection of entity records keyed by primary key 
   * this is complementary to the historically organized information in the event backbone. 
* When is it OK to be using synchronous interactions between services instead of asyncrhonous event interacts through the event backbone?
    * For non-state-changing queries, for which the response is always instantaneously available a synchronous query callmy be Ok and will provide a simpler more understandable interface.
    * Any processing which can be though of as being triggered by some state change in anothe aggregate should be modelled with an asynchronous, because as the solution eveolves other new microservices may also need to be aware of this event. We do not want to have to go back and change logic n the service where this event originated to have that microservice actively report the event to all potential consumers. 
*   How do we save microservices from having to maintain data collections with complex secondary indexing for which eventual consistency will be hard to implement? 
    * Each command  microservice should do all its state changing updates using the primary key lookup only for its entities.
    * Each asynchronous event interaction between microservices should carry primary entityIds ( orderID, VoyageID, shipID) for any entities associated with the interaction.
    * Each query which might require speciaoized secondary indexing to respond to queries can be implemented in a separate CQRS query service which subscribes to events  to do all internal updating and receives events from the event backbone in a ( Consistent) eventually correct order. 
    * This allows for recovery of anyfailed service by rebuilding it in eventually correct order.
    
    
  
