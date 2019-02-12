# Analysis to Microservices 
## Goals and outline of section 
This section describes the design step which uses output from the event storming session and subsequent analysis and derives a set of micro services design specification.
The goals for ts design step and the resulting specifications are: 
* Highly modular cloud native microservices 
* Event coupled microservices -  facilitating independent modification and evolution of each microservice separatelys
* Allow for event sourcing – eventual correctness and recovery using event base) 
* Illustrate CQRS and its scaling advantages 

Since we are delivering a demonstration application there will be some simulator / scaffolding / testing services mixed in with the required business processing.
This is a common occurrence in agile development and it may be helpful to show how decision to scope and simplify a particular build and test step interact with decisions relating strictly to microservices design.  

Requirements for scalability, coupling of microservices only through the event back bone and eventual correctness   differentiate this step from previous Event Storming and Domain Driven Design activities which were 100% business requirement driven.



Here is an example of screen I may use:

<img src="kc-order.png" height="630px">
