# K Container Shipment Use Case

This solution implementation illustrates the deployment of real time analytics on event streams in the context of container shipment in an event driven architecture with event backbone, functions as service and microservices.

As part of producing the IBM event driven point of view and reference architecture, we wanted to bring together a complete scenario which would cover all aspects of developing an event driven solutions including extended connections to devices/IOT  and blockchain for trusted business trading networks. We felt that the shipping business could provide a good foundation for this and would enable us to show how to develop event driven solutions following the architecture patterns.

The high level process can be represented in the following diagram, we will describe the steps in the [use case section](#use-case-description):

![](analysis/shipment-bp.png)

In developing the scenario, it became apparent that the event driven nature of business, extends across the business network, so we have widened the view in the scenario to consider the chain of parties involved in the shipping process, including importer, exporter, land transport and customs. To keep the scenario easy to understand, we have only considered the following cases:

1. Importer Orders goods from exporter overseas
2. Exporter becomes the customer of the shipping agent and uses 'ToDoor' shiping service
3. Shipping agent manages process of land transport loading, unloading and shipping. Through the scenario we can see the impact of “events”, which may delay or change the shipping process across all three parties.  

## Table Of Content

* [Target Audiences](#target-audiences)
* [Use case description](#use-case-description)
* [Analysis](#analysis-outcomes)
* [Architecture](#architecture)
* [Deployment](#deployment)
* [Demonstration script](./docs/demo.md)

## Target Audiences

You will be greatly interested by the subjects addressed in this solution if you are...

* An architect, you will get a deeper understanding on how all the components work together, and how to address resiliency, high availability.
* A developer, you will get a broader view of the solution end to end and get existing starting code, and practices you may want to reuse during your future implementation. We focus on event driven solution in hybrid cloud addressing patterns and non-functional requirements as CI/CD, Test Driven Development, ...
* A project manager, you may understand all the artifacts to develop in an EDA solution, and we may help in the future to do project estimation.

## Use Case Description

## Analysis Outcomes

Using the [event storming](https://github.com/ibm-cloud-architecture/refarch-eda/blob/master/docs/methodology/readme.md) workshop the development team extracts the following analysis of the business domain.

## Architecture

Leveraging the Event Driven Architecture high level architecture foundation the solution is using the following components:

![High level component view](docs/kc-hl-comp-view.png)

* Top left represents the user interface to support the demonstration of the KC solution, with a set of widgets to present the ships movements, the container tracking / monitoring and the event dashboards. The botton of the UI will have controls to help performaing the step by step demonstration.
* The event backbone is used to define a set of topics used in the solution and as event sourcing for microservice to microservice data consistency support.
* Each service supports the top-level process with context boundary defining the microservice scope.
* Streamaing analytics is used to process aggreates and analytics on containers and ships movement data coming in real time.

## Deployment

The solution support a set of related repositories including user interface, a set of microservices to implement event sourcing, saga and SQRS patterns, and provides simulators and analytics content.
In each repository we are explaining the design and some code approach used.

### Related repositories

* [User Interface in Angular 7 and BFF server used for demonstration](https://github.com/ibm-cloud-architecture/refarch-kc-ui)
* [Supporting microservices and functions](https://github.com/ibm-cloud-architecture/refarch-kc-ms)
* [Real time analytics with IBM Streams](https://github.com/ibm-cloud-architecture/refarch-kc-streams)

### Configuration

To make the solution running we need to have a set of components ready. We can deploy the components of the solution into two models:

* [public cloud (IBM Cloud)](docs/prepare-ibm-cloud.md)
* pricate cloud (you are using [IBM Cloud Private for that](docs/prepare-icp.md))

## Devops

## Contribute

As this implementation solution is part of the Event Driven architeture reference architecture, the [contribution policies](https://github.com/ibm-cloud-architecture/refarch-eda#contribute) apply the same way here.

Please [contact me](mailto:boyerje@us.ibm.com) for any questions.
