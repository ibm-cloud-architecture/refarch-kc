# Deployment to local Kubernetes

The scripts in the `scripts/localk8s` directory can be used to deploy the refarch-kc microservices and backing services to a local Kubernetes cluster.

## Installation

The entire installation process can be run by executing the `install.sh` or `install.bat` script. This script will invoke:
- `install-infra.sh` to set up the Kafka and Postgres backing services,
- `install-app.sh` to configure the configmaps, Kafka topics and secrets, and deploy the microservices,
- `run-integration-tests.sh` to execute the integration tests against the deployment as a Kubernetes job.

If desired, these steps can each be run individually by running the appropriate script.

### Namespaces

During the installation, a set of namespaces will be created to hold the components:
- `strimzi` to hold the Strimzi operator,
- `kafka` to hold the Kafka cluster that Strimzi will create for us,
- `postgres` to hold the Postgres operator and DB instance,
- `shipping` to hold the application microservices and configuration.

### Infrastructure

The infrastructure set up by `install-infra.sh` consists of:
- The Strimzi Kafka Operator, installed using Helm, configured to watch the `kafka` namespace,
- A Kafka cluster named `my-cluster`, with a single replica, ephemeral storage, and no TLS,
- A ServiceAccount called `pgserviceaccount`,
- A Postgres DB installed using the Bitnami Postgresql Helm chart, configured with `pgserviceaccount`.

### Application and configuration

The configuration and services deployed by `install-app.sh` are all contained within the `shipping` namespace. The configuration consists of:
- A ServiceAccount called `kcserviceaccount`,
- Secrets for Postgresql to allow connection to the DB created in the previous step,
- ConfigMap `kafka-brokers` with the address of the Kafka cluster created in the previous step,
- ConfigMap `kafka-topics` with the names of the Kafka topics we'd like to use,
- A set of Strimzi KafkaTopic CRs to create the Kafka topics in our cluster,

Each of the microservices is then installed using its respective Helm chart. The repos will be cloned using the existing `clone.sh` script if they do not already exist at the same directory level as the `refarch-kc` repo.

### Integration tests

Running the `run-integration-tests.sh` script will:
- Update the `kafka-topics` configmap to prefix each Kafka topic with `itg-`,
- Create the itg-prefixed topics,
- Restart the microservices so that they pick up the new topic configuration,
- Create a Kubernetes job using the `itg-tests/es-it/ReeferItgTests.yaml` definition, with the `KAFKA_ENV` variable set to `LOCAL`,
- Follow the log so that the output and progress of the tests can be viewed on the console,
- Revert the topic names to their normal values, and restart the microservices.

## Uninstalling

The entire solution can be uninstalled by executing the `uninstall.sh` or `uninstall.bat` script. Similar to installation, this will invoke:
- `uninstall-app.sh` to uninstall the Helm release for each microservice, and remove the config and `shipping` namespace,
- `uninstall-infra.sh` to uninstall Kafka, Strimzi and Postgres and their respective namespaces.

