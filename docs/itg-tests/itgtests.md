# Reefer container shipment solution integration tests

The Reefer container shipment solution comes with a set of integration test cases to ensure the end to end functionality of the application. These test cases are part of our CI/CD process so that we ensure every new pull request that brings new code in does not break or modify the correct functionality of the application.

So far we have the following integration test cases:

- [Happy path](happy-path/happy_path.md) - End to end happy path test.
- [SAGA pattern](saga/saga.md) - SAGA pattern for new order creation test.
- [Order Rejection](order-rejected/order_rejected.md) - Order Rejection test.
- [Container Anomaly](containerAnomaly/containerAnomaly.md) - Container anomaly and maintenance test.
- [Dead Letter Queue](dlq/dlq.md) - Container Anomaly Dead Letter Queue Pattern test.

New integration test cases will be added in order to test other parts of the application as well as use cases and other Event Driven Patterns.

## How to run the integration test cases

### Pre-requisites

In order to run the integration tests against the Reefer container shipment solution you first need to have this solution deployed on an Openshift or Kubernetes cluster. The solution is made up of:

1. Backing services such as IBM Event Streams and PostgreSQL - Instructions [here](https://ibm-cloud-architecture.github.io/refarch-kc/deployments/backing-services/).
2. The Reefer container shipment solution components - Instructions [here](https://ibm-cloud-architecture.github.io/refarch-kc/deployments/application-components/).

Once you have the solution deployed into your cluster, apart from an instance of IBM Event Streams and PostgreSQL either on premises or in IBM Cloud, you should have the following components at the very least for the integration tests to run:

```bash
$ oc get pods
NAME                                                READY     STATUS    RESTARTS   AGE
pod/ordercommandms-deployment-7cfcf65ffc-ffbxt      1/1       Running   0          32d
pod/orderqueryms-deployment-5ff4fd44d-ghrg6         1/1       Running   0          32d
pod/springcontainerms-deployment-7f78fc9b64-kt2pf   1/1       Running   0          32d
pod/voyagesms-deployment-7775bb8974-h8vj4           1/1       Running   0          32d
```

The integration test cases have been implemented to be run as a kubernetes job called **reefer-itgtests-job**. This job consist of a tailored python container where the integration tests, which are written in Python, will get executed in. The yaml file that will create such kubernetes job, called **ReeferItgTests.yaml**, can be found under the `itg-tests/es-it` folder in this very same repository. The reason for creating a tailored python container which to execute the integration tests in is because we can then control the execution environment for the integration tests. This way we ensure the appropriate libraries, permissions, etc are as expected. This tailored python container docker image is publicly available in the Docker Hub (`ibmcase/kcontainer-python:itgtests`). Please, make sure you can access the Docker Hub public registries from your OpenShift or Kubernetes cluster.

The integration tests also require of some variables being defined beforehand, some of which need to be defined as **secrets or configMaps** within your kubernetes namespace or OpenShift project, such as `KAFKA_APIKEY`, `KAFKA_BROKERS` and the IBM Event Streams PEM certificate (in case you are working with IBM Event Streams on premise), where the Reefer container shipment solution has been deployed into. You should have got these secrets or configMaps already created when deploying your backing services in #1 of this pre-requisites section.

Other required variables for the integration tests need to be defined within the kubernetes job yaml file:

- Orders topic name: This could be specified within the integration tests kubernetes job yaml file under the variable **ITGTESTS_ORDERS_TOPIC** which defaults to `itg-orders`.

- Order Command topic name: This could be specified within the integration tests kubernetes job yaml file under the variable **ITGTESTS_ORDER_COMMANDS_TOPIC** which defaults to `itg-order-commands`.

- Containers topic name: This could be specified within the integration tests kubernetes job yaml file under the variable **ITGTESTS_CONTAINERS_TOPIC** which defaults to `itg-containers`.

- Container anomaly retry topic name: This could be specified within the integration tests kubernetes job yaml file under the variable **ITGTESTS_CONTAINER_ANOMALY_RETRY_TOPIC** which defaults to `itg-container-anomaly-retry`.

- Container anomaly dead topic name: This could be specified within the integration tests kubernetes job yaml file under the variable **ITGTESTS_CONTAINER_ANOMALY_DEAD_TOPIC** which defaults to `itg-container-anomaly-dead`.

- Kafka Environment: It should be either **OCP** or **IBMCLOUD** depending on where your IBM Event Streams instance is deployed onto. If it is deployed on premises in your OpenShift or Kubernetes cluster, then it `KAFKA_ENV` should be set to `OCP`. If you are using an IBM Event Streams instance in the IBM Cloud, then `KAFKA_ENV` should be set to `IBMCLOUD`.

  This is important as the **IBM Event Streams on-prem instances require a PEM certificate** for the Kafka libraries to successfully connect to it. So, if you are using IBM Event Streams on-prem in your OpenShift or Kubernetes cluster, you also have to:

  1. Uncomment the bottom part of the integration tests kubernetes job yaml file.
  2. Make sure you created the **eventstreams-pem-file** secret that will hold your IBM Event Streams PEM certificate, in step #1 of this pre-requisites section.

**IMPORTANT:** For the integration test suite to work fine, more precisely to get the test case for testing [the Dead Letter Queue pattern](../dlq/dlq.md)) to succeed, we **must** mockup the BPM integration which we have developed some internal endpoints for. To use the BPM mockup endpoints, you will need to make sure the **bpm-anomaly** configMap you created for the Spring Container microservice component of the Reefer container shipment solution holds the following values for the url and login attributes:

```bash
login: 'http://localhost:8080/bpm_mockup/login'
url: 'http://localhost:8080/bpm_mockup/bpm_process_404'
```

You can do so by manually editing the configMap:

```bash
$ oc edit configmap bpm-anomaly -n eda-integration
```

The above will require to restart the Spring Container microservice component, although we **strongly suggest** the integration tests are run on a separate testing environment where the **bpm-anomaly** (and any other configuration item) holds testing values as well as the **recreation** of the kafka topics involved in the integration tests suite.

### Run

In order to run the integration test cases for the Reefer container shipment solution, we need to create the the job that will run these. To create the job, we simply execute:

```bash
oc apply -f ReeferItgReefer.yaml -n <namespace>
```

You should see the following output:

``` bash
job.batch/reefer-itgtests-job created
```

and if you list the pods in your namespace you should see a new pod which is running the integration tests:

```bash
$ oc get pods | grep itgtests
NAME                                           READY     STATUS        RESTARTS   AGE
reefer-itgtests-job-x594k                      1/1       Running       0          2m
```

Once the integration tests have finished, the pod should transition to completed status:

```bash
$ oc get pods
NAME                                           READY     STATUS      RESTARTS   AGE
reefer-itgtests-job-x594k                      0/1       Completed   0          3m
```

and the job output should be like:

```bash
$ oc get jobs
NAME                      DESIRED   SUCCESSFUL   AGE
reefer-itgtests-job       1         1            3m
```

## Output

If we want to inspect the output of the integration tests, we would need to get the logs for the pod that ran them:

```bash
$ oc logs e2e-reefer-itgtests-job-x594k
```

The output of the integration test cases is made up of a brief description of the execution environment:

```bash
-----------------------------------------------------------------
-- Reefer Container Shipment EDA application Integration Tests --
-----------------------------------------------------------------

Executing integrations tests from branch master of https://github.com/ibm-cloud-architecture/refarch-kc.git
Kafka Brokers: broker-0-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-3-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-5-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-2-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-1-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-4-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093
Kafka API Key: XXXXXXX
Kafka Env: IBMCLOUD
Orders topic name: itg-orders
Order Command topic name: itg-order-commands
Containers topic name: itg-containers
------------------------------------------------------------------
```

Then, each of the three test cases outlined in the introduction of this readme file will get executed, each of them beginning with a header like:

```bash
******************************************
******************************************
**********   E2E Happy Path   ************
******************************************
******************************************
```

After the header, the different tests within the test case will get executed. Each of these comes with a header and look like:

```bash
--------------------------------
--- [TEST] : Voyage Assigned ---
--------------------------------

1 - Load the expected voyage assigned event on the order topic from its json files
The expected voyage assigned event is:
{
    "payload": {
        "orderID": "a467070e-797e-40f9-9644-7393e8553f1f",
        "voyageID": "101"
    },
    "timestamp": "",
    "type": "VoyageAssigned",
    "version": "1"
}
Done

2 - Read voyage assigned from oder topic
[KafkaConsumer] - This is the configuration for the consumer:
[KafkaConsumer] - {'bootstrap.servers': 'broker-0-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-3-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-5-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-2-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-1-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093,broker-4-hnkssdz.kafka.svc01.us-east.eventstreams.cloud.ibm.com:9093', 'group.id': 'pythonconsumers', 'auto.offset.reset': 'earliest', 'enable.auto.commit': True, 'security.protocol': 'SASL_SSL', 'sasl.mechanisms': 'PLAIN', 'sasl.username': 'token', 'sasl.password': 'XXXXXXXX'}
.[KafkaConsumer] - @@@ pollNextOrder itg-orders partition: [0] at offset 2 with key b'a467070e-797e-40f9-9644-7393e8553f1f':
	value: {"timestamp":1576667245430,"type":"VoyageAssigned","version":"1","payload":{"voyageID":"101","orderID":"a467070e-797e-40f9-9644-7393e8553f1f"}}
This is the event read from the order topic:
{
    "payload": {
        "orderID": "a467070e-797e-40f9-9644-7393e8553f1f",
        "voyageID": "101"
    },
    "timestamp": "",
    "type": "VoyageAssigned",
    "version": "1"
}
Done

3 - Verify voyage assigned event
Done

```

A summary of the test case execution is shown at the end of each test case:

```bash
----------------------------------------------------------------------
Ran 7 tests in 64.262s

OK
```

A final summary of all tests cases is shown at the very end and looks like the following:

```bash
END RESULTS:

TEST CASE - E2EHappyPath
-----------------------------------
test1_createContainer...OK
test2_voyagesExist...OK
test3_createOrder...OK
test4_containerAllocated...OK
test5_voyageAssigned...OK
test6_orderAssignedREST...OK
test7_exportValues...OK
-----------------------------------
PASSED: 7
FAILED: 0

TEST CASE - SagaNoContainer
-----------------------------------
test1_createOrder...OK
test2_containerNotFound...OK
test3_orderRejected...OK
test4_orderRejectedREST...OK
-----------------------------------
PASSED: 4
FAILED: 0

TEST CASE - SagaNoVoyage
-----------------------------------
test1_createContainer...OK
test2_createOrder...OK
test3_containerAllocated...OK
test4_voyageNotFound...OK
test5_orderRejected...OK
test6_orderRejectedREST...OK
test7_containerUnassignedREST...OK
test8_exportValues...OK
-----------------------------------
PASSED: 8
FAILED: 0

TEST CASE - OrderRejection
-----------------------------------
test1_createOrder...OK
test2_containerAllocated...OK
test3_voyageAssigned...OK
test4_orderAssignedREST...OK
test5_orderRejected...OK
test6_orderRejectedREST...OK
test7_containerUnassignedREST...OK
test8_voyageCompensated...OK
-----------------------------------
PASSED: 8
FAILED: 0

TEST CASE - SpoilOrder
-----------------------------------
test1_disableBPM...OK
test2_sendAnomalyEvents...OK
test3_containerMaintenanceNeeded...OK
test4_containerOrderSpoilt...OK
test5_containerToMaintenance...OK
test6_containerInMaintenance...OK
test7_containerOffMaintenance...OK
test8_containerEmpty...OK
test9_enableBPM...OK
-----------------------------------
PASSED: 9
FAILED: 0

TEST CASE - Dlq
-----------------------------------
test1_createContainer...OK
test2_sendAnomalyEvents...OK
test3_containerMaintenanceNeeded...OK
test4_containerAnomalyRetry...OK
test5_containerAnomalyDead...OK
-----------------------------------
PASSED: 5
FAILED: 0
```
