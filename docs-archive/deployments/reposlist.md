# Related repositories

This solution supports a set of related repositories which includes user interface, a set of microservices to implement the Event Sourcing and CQRS patterns, and to implement simulators and analytics content.
In each repository we are explaining the design and implementation approach, how to build and run them for development purpose.

The command `./scripts/clone.sh` in this project clones all the dependant repositories as part of the solution.

| Component                 | GitHub Repository | MVP Level* | Language(s) | Description |
| ------------------------- | ------------------ | ------ |------------------ | ------------------ |
| User Interface                | [refarch-kc-ui](https://ibm-cloud-architecture.github.io/refarch-kc-ui/) | 1 | Angular 7 | User Interface and Backend For Frontend server used for demonstration purpose |
| Order management microservice | [refarch-kc-order-ms](https://ibm-cloud-architecture.github.io/refarch-kc-order-ms) | 1 | Java with Liberty & MicroProfile | Order management using CQRS and event sourcing pattern |
| Shipping container management microservice | [refarch-kc-container-ms](https://ibm-cloud-architecture.github.io/refarch-kc-container-ms/) | 2 | Spring Boot Java, Python | Reefer container management microservice in different programming language, and to define python tools to do machine learning on top of event store from Kafka. |
| Fleet microservice | [refarch-kc-ms/fleet-ms](https://ibm-cloud-architecture.github.io/refarch-kc-ms/fleetms) | 2 | Java | Simulation of a fleet of container carrier vessels |
| Voyage microservice       | [refarch-kc-ms/voyages-ms](https://ibm-cloud-architecture.github.io/refarch-kc-ms/voyagems) | 2 | NodeJS | Supports the order management and ship voyage assignment, using Nodejs / express and kafka javascript APIs. |
| Reefer predictive maintenance | [refarch-reefer-ml](https://ibm-cloud-architecture.github.io/refarch-reefer-ml/) | 3 | Python | Uses Reefer container metrics like power, temperature, CO2, or other sensors to build a machine learning model, deploy it as a service and run it on Event Streams. |
| MQ to Kafka integration with a 'legacy' app | [refarch-container-inventory](https://ibm-cloud-architecture.github.io/refarch-container-inventory/) | 3 | Java | Bi-directional connections between MQ and Kafka, using a legacy JEE app to manage the inventory for metal and Reefer containers, but only Reefer information is sent to Kafka. |
| Microprofile 3.0 producer and consumer template | [microprofile-event-driven-microservice-template](https://github.com/jbcodeforce/microprofile-event-driven-microservice-template) | n/a | Java microprofile 3.0 | Get started from a DDD project template on Openliberty and microprofile 3.0- Kafka API |
| Quarkus Microprofile 3.0 consumer template | [quarkus-event-driven-consumer-microservice-template](https://github.com/jbcodeforce/quarkus-event-driven-consumer-microservice-template) | n/a | Quarkus Java microprofile 3.0 | Get started from a DDD project template on Quarkus and microprofile 3.0- Kafka consumer API |
| Quarkus Microprofile 3.0 producer template | [quarkus-event-driven-producer-microservice-template](https://github.com/jbcodeforce/quarkus-event-driven-producer-microservice-template) | n/a | Quarkus Java microprofile 3.0 | Get started from a DDD project template on Quarkus and microprofile 3.0- Kafka producer API |
| Kafka order producer in python| [jbcodeforce/order-producer-python](https://github.com/jbcodeforce/order-producer-python) | n/a | Python and Flask | Quickly test an IBM Cloud Event Streams deployment. |

**\*** **MVP Level** denotes minimal level of system capability to demostrate overall solution functionality.  *MVP Level 1* requires the least amount of components, *MVP Level 2* requires more components, and so on.
