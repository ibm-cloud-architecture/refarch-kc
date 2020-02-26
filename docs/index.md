# Reefer Container Shipment solution - EDA reference implementation

The IBM Event Driven architecture reference implementation illustrates the deployment of real time analytics on event streams in the context of container shipment in an [event driven architecture](https://ibm-cloud-architecture.github.io/refarch-eda/) with event backbone, functions as service and microservices. It aims to illustrate the different event driven patterns like event sourcing, CQRS and Saga and give a lot of best practices around implementing event driven microservices.

## What you will learn

* How to apply the event storming methodology and workshop to analyze the business process for fresh good shipment over sees.
* How to transform Domain Driven Design aggregates to microservices.
* How to implement the different microservices using the event-driven pattern like CQRS pattern with event sourcing done in Apache Kafka or IBM Events Streams.
* How to deploy your solution to IBM Cloud Kubernetes service (Public cloud), or to IBM Cloud Private (kubernetes based) or run locally with Docker compose.
* How to use event store (Kafka topics) as source for machine learning data source to build training and test sets.
* How to implement a Test Driven Development for the Order microservice uisng mockito to avoid Kafka dependency.
* How to implement the same container management microservices in python, nodejs, java microprofile 2 with Kafka streams API, and springboot, kafka template and PostgreSQL.

This is a lot, not all is done yet. But consider this content as a living book, with the left side representing major subjects and each subject with its own table of contents.

## Target Audiences

You will be greatly interested by the subjects addressed in this solution if you are...

* An architect, you will get a deeper understanding on how all the components work together, and how to address resiliency, high availability.
* A developer, you will get a broader view of the solution end to end and get existing starting code, and practices you may want to reuse during your future implementation. We focus on event driven solution in hybrid cloud addressing patterns and non-functional requirements as CI/CD, Test Driven Development, ...
* A project manager, you may understand all the artifacts to develop in an EDA solution, and we may help in the future to do project estimation.

## Business process statement

In [this first chapter](introduction.md) we are presenting the business process for shipping fresh good over sees and we are detailing the analysis we have done in San Francisco in November 2018 using the event storming analysis workshop. You could read more on how to organize and execute such workshop [here](https://ibm-cloud-architecture.github.io/refarch-eda/methodology/readme/). The workshop execution transcript is detailed in [a second chapter](analysis/readme.md).

## Design considerations

In the [third chapter](design/readme.md) we are detailing how to transform the analysis outcomes into some light design, conceptual view, just enough to start coding some microservices.

## Architecture

This quick [architecture chapter](design/architecture.md) presents the solution components working together with the event backbone.

## Build and Run

The end to end solution can be demonstrated from a unique user interface and it involves multiple microservices deployed independently. As some of those components are using IBM products or IBM Cloud services, you need to provision such services. We propose to develop with an hybrid environment, using IBM Cloud services, local environment running on your laptop and IBM private cloud cluster (optional). As of now only Mac and Linux development workstation are supported. For the Java development we used Eclipse 2019 edition. So basically we need the following:

* [Event Streams instance on IBM Cloud Public](https://ibm-cloud-architecture.github.io/refarch-eda/deployments/eventstreams) or Event streams on IBM Cloud private or a Kafka Docker image.
* Streaming Analytics on IBM Cloud public or on ICP for Data.
* Kubernetes Cluster (IBM Cloud Private or IBM Kubernetes Service on cloud) or Docker compose to run locally.
* Postgresql service in IBM Cloud. This database is used by one service, built with Spring boot, that can be plug and play. It is optional. We want to illustrate with this implementation a reversibility practice where we start development on the cloud and migrate to private cloud.

The instructions to build, deploy and test all the solution components, are defined in this source repository: [https://github.com/ibm-cloud-architecture/refarch-kc/tree/master/docs](https://github.com/ibm-cloud-architecture/refarch-kc/tree/master/docs). Also, each project, part of the solution, has its own installation explanations and scripts to build, package, test and deploy to the different Kubernetes deployment (private and public). We recommend studying those scripts.

## Deployments

We can deploy the components of the solution into any Kubernetes-based environment - including OpenShift, IBM Cloud Kubernetes Service, and vanilla Kubernetes:

* **[Backing Services](deployments/backing-services.md)** documents the required environment configuration, as well as Kafka and Postgresql options to satisfy application dependencies.
* **[Application Components](deployments/application-components.md)** documents the deployment steps required for the K Container Reference Implementation, as well as integration tests to validate deployment.

## Still project under development

The following items are not yet completed:

* Microprofile 2.2 container service with kafka streams
* An end to end automated test scenario
* A demonstration script to present the process execution from end users point of view
* A set of tests to validate event sourcing, and Saga patterns
* Cold chain predictive model
* Container predictive maintenance model and deployment.

## Further readings

* [Event driven architecture in IBM Garage method](https://www.ibm.com/cloud/garage/architectures/eventDrivenArchitecture)
* [Event driven compagnion github with other best practices](https://ibm-cloud-architecture.github.io/refarch-eda/)
* [Event-driven training journey](https://ibm-cloud-architecture.github.io/refarch-eda/eda-skill-journey/)
