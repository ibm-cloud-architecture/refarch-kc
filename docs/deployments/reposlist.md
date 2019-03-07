# Related repositories
This solution supports a set of related repositories which includes user interface, a set of microservices to implement the Event Sourcing and CQRS patterns, and to implement simulators and analytics content.
In each repository we are explaining the design and implementation approach, how to build and run them for development purpose.

The command `./scripts/clone.sh` in this project clones all the dependant repositories as part of the solution. 

* [User Interface in Angular 7 and Backend For Frontend server used for demonstration purpose](https://github.com/ibm-cloud-architecture/refarch-kc-ui).
* [Ship and fleet microservice](https://github.com/ibm-cloud-architecture/refarch-kc-ms/tree/master/fleet-ms) of this solution are grouped in one repository. We may change that later if we need it.
* [Real time analytics with IBM Streaming Analytics](https://github.com/ibm-cloud-architecture/refarch-kc-streams) to identify problem on containers from real time events.
* [Order management microservice using CQRS and event sourcing pattern](https://github.com/ibm-cloud-architecture/refarch-kc-order-ms).
* [Voyage microservice](https://github.com/ibm-cloud-architecture/refarch-kc-ms/tree/master/voyages-ms) to support the order management and ship voyage assignment.
* [Container microservice](https://github.com/ibm-cloud-architecture/refarch-kc-container-ms/) to support the container management and tools to do machine learning on top of event store from Kafka.