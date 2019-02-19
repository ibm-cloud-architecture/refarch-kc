# Container Shipment EDA reference implementation
The IBM Event Driven architecture reference implementation illustrates the deployment of real time analytics on event streams in the context of container shipment in an [event driven architecture](https://github.com/ibm-cloud-architecture/refarch-eda) with event backbone, functions as service and microservices, and aims to illustrate the different event driven patterns like event sourcing, CQRS and Saga.

## What you will learn
* How to apply the event storming methodology and workshop to analyze the business process for fresh good shipment over sees.
* How to transform Domain Driven Design aggregates to microservices
* How to implement the different microservices using the event-driven pattern like CQRS pattern with event sourcing done in Apache Kafka or IBM Events Streams
* How to implement a Test Driven Development for the Order microservice uisng mockito to avoid Kafka dependency

## Target Audiences

You will be greatly interested by the subjects addressed in this solution if you are...

* An architect, you will get a deeper understanding on how all the components work together, and how to address resiliency, high availability.
* A developer, you will get a broader view of the solution end to end and get existing starting code, and practices you may want to reuse during your future implementation. We focus on event driven solution in hybrid cloud addressing patterns and non-functional requirements as CI/CD, Test Driven Development, ...
* A project manager, you may understand all the artifacts to develop in an EDA solution, and we may help in the future to do project estimation.

## Business process statement
In [this first chapter](introduction.md) we are presenting the business process for shipping fresh good over sees and detailing the event storming analysis workshop execution, and we are explaining how to transform analysis outcomes such as domain boundaries and aggregates to microservices. 

## Design considerations
In the [third chapter](design/readme.md) we are going in detail on the process analysis to define the requirements for the major microservices to implement.


## Architecture

This quick [architecture note](design/architecture.md) presents the components working together with the event backbone. 

## Deployment

To make the solution running we need to have to prepare a set of products installed and running:
* Event Streams
* Streaming Analytics
* Kubernetes Cluster (IBM Cloud Private or IBM Kubernetes Service on cloud) or Docker compose.

We can deploy the components of the solution into three environments:

* **Public cloud (IBM Cloud)**, [see this article](deployments/iks.md) for details on how to prepare the needed services.
* **Private cloud** (we are using IBM Cloud Private) and [see this article](deployments/icp.md) for details.
* **[Local](deployments/local.md)** to your laptop, using docker images and docker compose.
