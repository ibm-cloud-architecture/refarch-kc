Deployment of application microservices for the Event-Driven Architecture Reference Application

# Environment prerequisites

## Kafka Topic Creation

You can create the topics using the Event Streams console:

![](es-icp-topics.png)

or if you have manually deployed Event Streams or Kafka, you can use commands similar to the snippet below:

```shell
# get the name of the Kafka pod
$ export NAMESPACE=<target k8s namespace / ocp project>
$ export KPOF=$(kubectl get pods  -n ${NAMESPACE} | grep kafka | awk '{print $1;}')
$ cat ${KPOF}
rolling-streams-ibm-es-kafka-sts-0
rolling-streams-ibm-es-kafka-sts-1
rolling-streams-ibm-es-kafka-sts-2
# Then get the name of the zookeeper service:
$ export ZOOKSVC=$(kubectl get svc -n ${NAMESPACE} | grep zoo | awk '{print $1;}' | head -1)
rolling-streams-ibm-es-zookeeper-fixed-ip-svc-0
# Then remote exec a shell on one of this broker to configure the topic - for example the "orders" topic
$ kubectl exec -n ${NAMESPACE} -ti ${KPOF} -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper ${ZOOKSVC}:2181 --replication-factor 1 --partitions 1 --topic orders"
```

The topics that need to be created are:
- `bluewaterContainer`
- `bluewaterShip`
- `bluewaterProblem`
- `orders`
- `rejected-orders`
- `allocated-orders`
- `errors`
- `containers`
- `containerMetrics`

## Docker registries

You will need a Docker image registry to push and pull your images to and from.  There are multiple options depending on client use cases and we are only documenting a subset of potential solutions, including but not limited to IBM Cloud Container Registry, Docker Hub, Quay, etc.

### IBM Cloud Container Registry

* Install IBM Cloud Container Registry CLI plug-in if needed:
```
ibmcloud plugin install container-registry -r Bluemix
```

**Define a private image repository**

Use the [IBM Cloud Container Registry](https://cloud.ibm.com/containers-kubernetes/catalog/registry) to push your images and then deploy them to any Kubernetes cluster with access to the public internet.  When deploying enterprise applications, it is strongly recommended to use private registry to protect your images from being used and changed by unauthorized users. Private registries must be set up by the cluster administrator to ensure that the credentials to access the private registry are available to the cluster users.

* Create a namespace inside your Container Registry for use here:
```shell
ibmcloud cr namespace-add ibmcaseeda
```

We will use this namespace when tagging the docker images for our microservices. Here is an example of tagging:

```shell
docker tag ibmcase/kc-ui us.icr.io/ibmcaseeda/kc-ui:latest
```

To see the images in your private registry you can use the user interface at [https://cloud.ibm.com/containers-kubernetes/registry/main/private](https://cloud.ibm.com/containers-kubernetes/registry/main/private) or the command:

```
ibmcloud cr image-list
```

**Private Registry Token**

Each Helm Chart specifies the name of the Docker image to load the containers & pods. To enable access from Kubernetes Nodes to your private registry, an image pull secret is required and will be stored in a Kubernetes secret.  If you are using public Docker Hub image repositories, an image pull secret is not required.

*Using secret is also mandatory when registry and clusters are not in the same region.*

* Verify current secrets for a given namespace:

```shell
kubectl describe secrets -n <target namespace>
```

* Get a security token: _(these can be `permanent` or `renewable`)_

```shell
ibmcloud cr token-add --description "private registry secret for <target namespace>" --non-expiring -q
```

* To list the available tokens:

```shell
ibmcloud cr tokens
```
The result:
> TOKEN ID     READONLY   EXPIRY   DESCRIPTION
 2b5ff00e-a..  true       0       token for somebody
 3dbf72eb-6..  true       0       private registry secret for browncompute

* Get the token for a given token identifier:

```shell
ibmcloud cr token-get cce5a800-...
```

* Define the secret to store the Event stream API key token information:

```shell
kubectl --namespace <target namespace> create secret docker-registry
<target namespace>-registry-secret  --docker-server=<registry_url> --docker-username=token --docker-password=<token_value> --docker-email=<docker_email>
```

* Verify the secret

```shell
kubectl get secrets -n <target namespace>
```

You will see something like below.

> | NAME  | TYPE  | DATA | AGE |
| --- | --- | --- | --- |
| browncompute-registry-secret    |       kubernetes.io/dockerconfigjson     |   1  |       2m |
| default-token-ggwl2  |  kubernetes.io/service-account-token  | 3  |   41m  |
| eventstreams-apikey  |  Opaque   |      1   | 24m  |


## Basic Kubernetes

## IBM Cloud Kubernetes Service

To create the cluster follow [this tutorial](https://console.bluemix.net/docs/containers/cs_tutorials.html#cs_cluster_tutorial).

## OpenShift Container Platform 3.11

This needs to be done once per unique deployment of the entire application.

1. If desired, create a non-default Service Account for usage of deploying and running the K Container reference implementation.  This will become more important in future iterations, so it's best to start small:
  - Command: `oc create serviceaccount -n <target-namespace> kcontainer-runtime`
  - Example: `oc create serviceaccount -n eda-refarch kcontainer-runtime`
2. The target Service Account needs to be allowed to run containers as `anyuid` for the time being:
  - Command: `oc adm policy add-scc-to-user anyuid -z <service-account-name> -n <target-namespace>`
  - Example: `oc adm policy add-scc-to-user anyuid -z kcontainer-runtime -n eda-refarch`
  - NOTE: This requires `cluster-admin` level privileges.

## OpenShift Container Platform 4.X

# Deploy application microservices

## Using the master repository
You can download the necessary application microservice repsoitories using scripts provided in the master repository:

```shell
git clone https://github.com/ibm-cloud-architecture/refarch-kc.git
cd refarch-kc
./scripts/clone.sh
```

## Deploy Order Command microservice

* Go to the repo

```shell
cd refarch-kc-order-ms/order-command-ms
```

* Build the image

```shell
docker build -t order-command-ms:latest -f Dockerfile.NoKubernetesPlugin
```

* Tag the image

```shell
docker tag order-command-ms <private-registry>/<image-namespace>/order-command-ms:latest
```

* Push the image

```shell
docker login <private-registry>
docker push <private-registry>/<image-namespace>/order-command-ms:latest
```

* Generate application YAMLs via `helm template` with the following parameters:
  - `--set image.repository=<private-registry>/<image-namespace>/<image-repository>`
  - `--set image.tag=latest`
  - `--set image.pullSecret=<private-registry-pullsecret>` (optional or set to blank)
  - `--set image.pullPolicy=Always`
  - `--set eventstreams.env=ICP`
  - `--set eventstreams.brokersConfigMap=<kafka brokers ConfigMap name>`
  - `--set serviceAccountName=<service-account-name>`
  - `--namespace <target-namespace>`
  - `--output-dir <local-template-directory>`

```shell
# Example parameters
helm template --set image.repository=rhos-quay.internal-network.local/browncompute/order-command-ms --set image.tag=latest --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.env=ICP --set eventstreams.brokersConfigMap=kafka-brokers --set serviceAccountName=kcontainer-runtime --output-dir templ --namespace eda-refarch chart/ordercommandms/
```

* Deploy application using `kubectl/oc apply`:
```shell
(kubectl/oc) apply -f templates/ordercommandms/templates`
```

* Verify default service is running correctly:

Without any previously tests done, the call below should return an empty array: `[]`
```shell
curl http://<cluster endpoints>:31200/orders
```

## Deploy Order Query microservice

* Go to the repo

```shell
cd refarch-kc-order-ms/order-query-ms
```

* Build the image

```shell
docker build -t order-query-ms:latest -f Dockerfile.NoKubernetesPlugin
```

* Tag the image

```shell
docker tag order-query-ms <private-registry>/<image-namespace>/order-query-ms:latest
```

* Push the image

```shell
docker login <private-registry>
docker push <private-registry>/<image-namespace>/order-query-ms:latest
```

* Generate application YAMLs via `helm template` with the following parameters:
  - `--set image.repository=<private-registry>/<image-namespace>/<image-repository>`
  - `--set image.tag=latest`
  - `--set image.pullSecret=<private-registry-pullsecret>` (optional or set to blank)
  - `--set image.pullPolicy=Always`
  - `--set eventstreams.env=ICP`
  - `--set eventstreams.brokersConfigMap=<kafka brokers ConfigMap name>`
  - `--set serviceAccountName=<service-account-name>`
  - `--namespace <target-namespace>`
  - `--output-dir <local-template-directory>`

```shell
# Example parameters
helm template --set image.repository=rhos-quay.internal-network.local/browncompute/order-query-ms --set image.tag=latest --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.env=ICP --set eventstreams.brokersConfigMap=kafka-brokers --set serviceAccountName=kcontainer-runtime --output-dir templ --namespace eda-refarch chart/orderqueryms/
```

* Deploy application using `kubectl/oc apply`:
```shell
(kubectl/oc) apply -f templates/orderqueryms/templates`
```

* Verify default service is running correctly:

Without any previously tests done, the call below should return an empty array: `[]`
```shell
curl http://<cluster endpoints>:31100/orders
```

## Deploy Container microservice

**TODO** Container Microservice requires POSTGRES parameters

* Go to the repo

```shell
cd refarch-kc-container-ms/SpringContainerMS
```

* Build the image

```shell
docker build -t kc-spring-container-ms:latest -f Dockerfile.NoKubernetesPlugin
```

* Tag the image

```shell
docker tag kc-spring-container-ms <private-registry>/<image-namespace>/kc-spring-container-ms:latest
```

* Push the image

```shell
docker login <private-registry>
docker push <private-registry>/<image-namespace>/kc-spring-container-ms:latest
```

* Generate application YAMLs via `helm template` with the following parameters:
  - `--set image.repository=<private-registry>/<image-namespace>/<image-repository>`
  - `--set image.tag=latest`
  - `--set image.pullSecret=<private-registry-pullsecret>` (optional or set to blank)
  - `--set image.pullPolicy=Always`
  - `--set eventstreams.env=ICP`
  - `--set eventstreams.brokersConfigMap=<kafka brokers ConfigMap name>`
  - `--set serviceAccountName=<service-account-name>`
  - `--namespace <target-namespace>`
  - `--output-dir <local-template-directory>`

```shell
# Example parameters
helm template --set image.repository=rhos-quay.internal-network.local/browncompute/kc-spring-container-ms --set image.tag=latest --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.env=ICP --set eventstreams.brokersConfigMap=kafka-brokers --set serviceAccountName=kcontainer-runtime --output-dir templ --namespace eda-refarch chart/springcontainerms
```

* Deploy application using `kubectl/oc apply`:
```shell
(kubectl/oc) apply -f templates/springcontainerms/templates`
```

* Verify default service is running correctly:

```shell
curl http://cluster-endpoints:31900/containers
```

## Deploy Voyages microservice

The *Voyage microservice* is a simple nodejs app to mockup schedule of vessels between two harbors. It is here to illustrate Kafka integration with nodejs app.

* Go to the repo

```shell
cd cd refarch-kc-ms/voyages-ms
```

* Build the image

```shell
docker build -t kc-voyages-ms:latest -f Dockerfile
```

* Tag the image

```shell
docker tag kc-voyages-ms <private-registry>/<image-namespace>/kc-voyages-ms:latest
```

* Push the image

```shell
docker login <private-registry>
docker push <private-registry>/<image-namespace>/kc-voyages-ms:latest
```

* Generate application YAMLs via `helm template` with the following parameters:
  - `--set image.repository=<private-registry>/<image-namespace>/<image-repository>`
  - `--set image.tag=latest`
  - `--set image.pullSecret=<private-registry-pullsecret>` (optional or set to blank)
  - `--set image.pullPolicy=Always`
  - `--set eventstreams.env=ICP`
  - `--set eventstreams.brokersConfigMap=<kafka brokers ConfigMap name>`
  - `--set serviceAccountName=<service-account-name>`
  - `--namespace <target-namespace>`
  - `--output-dir <local-template-directory>`

```shell
# Example parameters
helm template --set image.repository=rhos-quay.internal-network.local/browncompute/kc-voyages-ms --set image.tag=latest --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.env=ICP --set eventstreams.brokersConfigMap=kafka-brokers --set serviceAccountName=kcontainer-runtime --output-dir templ --namespace eda-refarch chart/voyagesms
```

* Deploy application using `kubectl/oc apply`:
```shell
(kubectl/oc) apply -f templates/voyagesms/templates`
```

* Verify default service is running correctly:

```shell
curl http://cluster-endpoint:31000/voyage
```

## Deploy User Interface microservice

* Go to the repo

```
cd refarch-kc-ui/
```

* Build the image

```shell
docker build -t kc-ui:latest -f Dockerfile.NoKubernetesPlugin
```

* Tag the image

```shell
docker tag kc-ui <private-registry>/<image-namespace>/kc-ui:latest
```

* Push the image

```shell
docker login <private-registry>
docker push <private-registry>/<image-namespace>/kc-ui:latest
```

* Generate application YAMLs via `helm template` with the following parameters:
  - `--set image.repository=<private-registry>/<image-namespace>/<image-repository>`
  - `--set image.tag=latest`
  - `--set image.pullSecret=<private-registry-pullsecret>` (optional or set to blank)
  - `--set image.pullPolicy=Always`
  - `--set eventstreams.env=ICP`
  - `--set eventstreams.brokersConfigMap=<kafka brokers ConfigMap name>`
  - `--set serviceAccountName=<service-account-name>`
  - `--namespace <target-namespace>`
  - `--output-dir <local-template-directory>`

```shell
# Example parameters
helm template --set image.repository=rhos-quay.internal-network.local/browncompute/kc-ui --set image.tag=latest --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.env=ICP --set eventstreams.brokersConfigMap=kafka-brokers --set serviceAccountName=kcontainer-runtime --output-dir templates --namespace eda-refarch chart/kc-ui
```

* Deploy application using `kubectl/oc apply`:
```shell
(kubectl/oc) apply -f templates/kc-ui/templates`
```

* Verify the installed app

Point your web browser to [http://cluster-endpoints:31010](#) and login with username: eddie@email.com and password Eddie.

## Deploy the Fleet Simulator microservice

**TODO** Fleet Simulator

!!! note
    The fleet simulator is to move vessels from one harbors to another, and send container metrics while the containers are on a vessel. It has some predefined simulation to trigger some events.

* Go to the repo

```
$ cd refarch-kc-ms/fleet-ms
```

* Build the image

```
$ ./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/fleetms/ --name fleetms --set image.repository=ibmcase/kc-fleetms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=MINIKUBE --namespace greencompute
```

* Verify service runs

At the beginning the call below should return an empty array: `[]`
```
curl http://localhost:31300/fleetms/fleets
```

## Integration Tests

Integration tests are provided in the [itg-tests](itg-tests/) directory and are designed to be run in cluster with the rest of the application components.  However, they are regular Python scripts that can be adapted to be runnable anywhere, given the correct Kafka endpoints and configuration information.  For simplicity, this quick walkthrough will document how you can build and deploy Docker images that will run the integration tests inside the cluster, with the results visible via `kubectl logs` and the rest of the application's APIs.

* Build the base Docker image
```shell
# From the root of the 'refarch-kc' repository
docker build -f docker/docker-python-tools -t osowski/python-tools .
docker push osowski/python-tools
```

The above image is a base Python image with our integration tests, defined in the `itg-tests` directory.  It is a long-running Flask process that provides a simple web server, so once deployed, it will remain available to "exec" into for additional in-cluster CLI interaction.  However, for simplicity, we have defined a few integration scenarios, using a Kubernetes Deployment and multiple Kubernetes Jobs, that will automate some of the integration test scenarios.

* Update the `itg-tests/kustomization.yaml` file with the specifics for your `python-tools` Docker image, changing the `newName` and `newTag` fields, as appropriate, along with the `namespace` field.

* Then run the following the command to apply the customization and deploy to the platform:
```shell
# From the root of the 'refarch-kc' repository
kubectl apply -k itg-tests/
```
**NOTE:** `kubectl` must be at level `1.14` or higher for the `-k` flag to be available.

This Kubernetes YAML will create one Deployment and one Job.  The long-running Deployment will run the [OrdersPython/OrderConsumer.py](#) script to watch for order events in the Kafka backend, while the short-lived Job create all the necessary order events via the [es-it/ProducerOrderEvents.py](#) script and publish them to Kafka.

* View the output of the `es-it/ProducerOrderEvents.py` Job:
```shell
(kubectl/oc) get jobs | grep kcontainer
(kubectl/oc) logs -f <pod_name>
```

* View the output of the `OrdersPython/OrderConsumer.py` Deployment:
```shell
(kubectl/oc) get pods | grep consumer
(kubectl/oc) logs -f <pod_name>
```

You should see the same Order ID created by the Job in the output of the Deployment's container.

# Universal deployment considerations

When deploying kafka consumer it is important to assess the horizontal pod autoscaler settings and needs, as adding consumers will not address scalability if the number of partitions in the topic(s) to consume does not match the increase of consumers. So disable HPA by default. If you want to use HPA you also need to ensure that a metrics-server is running, then set the number of partition, and the `hpa.maxReplicas` to the number of partitions.
