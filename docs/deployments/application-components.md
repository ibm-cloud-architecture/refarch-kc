Deployment of application microservices for the Event-Driven Architecture Reference Application

# Environment prerequisites

## Kafka Topic Creation

**TODO** Kafka Topic Creation

You can create the topics using the Event Streams console:

![](es-icp-topics.png)

or the use a set of commands like below, which are done for you in the script: `scripts/createLocalTopicsOnK8S.sh `.

```shell
# get the name of the Kafka pod
$ export NAMESPACE=<target k8s namespace / ocp project>
$ kubectl get pods  -n ${NAMESPACE} | grep kafka | awk '{print $1;}'
> rolling-streams-ibm-es-kafka-sts-0
rolling-streams-ibm-es-kafka-sts-1
rolling-streams-ibm-es-kafka-sts-2
# Then get the name of the zookeeper service:
$ kubectl get svc -n ${NAMESPACE} | grep zoo | awk '{print $1;}' | head -1
rolling-streams-ibm-es-zookeeper-fixed-ip-svc-0
# Then remote exec a shell on one of this broker to configure the topic - for example the "orders" topic
$ kubectl exec -n ${NAMESPACE} -ti rolling-streams-ibm-es-kafka-sts-0 -- bash -c "/opt/kafka/bin/kafka-topics.sh --create  --zookeeper $zooksvc:2181 --replication-factor 1 --partitions 1 --topic orders"
```

## Docker registries

**IBM Cloud Container Registry**

* Install IBM Cloud Container Registry CLI plug-in, using the command:
```
ibmcloud plugin install container-registry -r Bluemix
```

The following diagram illustrates the command lines interface and how they interact with IBM Cloud components:

![](ic-cli-comp.png)

Each helm chart to deploy each component of the solution uses the private repository like: `us.icr.io/ibmcaseeda/`. As it is recommended to use your own private image repository, we are presenting a quick summary of what to do to define your own private registry in the next section.

**Define an image private repository**

Use the [docker container image private registry](https://cloud.ibm.com/containers-kubernetes/catalog/registry) to push your images and then deploy them to IBM Kubernetes Service. When deploying enterprise application it is strongly recommended to use private registry to protect your images from being used and changed by unauthorized users. Private registries must be set up by the cluster administrator to ensure that the credentials to access the private registry are available to the cluster users.

In the IBM Cloud Catalog, use the `Containers` category and `Container Registry` tile. Create the repository with the `create` button. You can share a repository between multi IKS clusters within the same region.

Once you access your registry, create a namespace for your solution. We used `ibmcaseeda` name.

*The namespace can also be created with the command:

```
ibmcloud cr namespace-add ibmcaseeda
```
Here is a screen shot of the created image repository:

![](iks-registry-ns.png)

We will use this namespace when tagging the docker images for our microservices. Here is an example of tagging:

```shell
docker tag ibmcase/kc-ui us.icr.io/ibmcaseeda/kc-ui:latest
```

To see the images in your private registry you can use the user interface at [https://cloud.ibm.com/containers-kubernetes/registry/main/private](https://cloud.ibm.com/containers-kubernetes/registry/main/private) or the command:

```
ibmcloud cr image-list
```

**Private Registry Token**

Each helm chart specifies the name of the docker image to load to create the containers / pods. The image name is from a private repository. To let kubernetes scheduler being able to access the registry, we need to define a secret to hold the security token. Here is an extract of a deployment yaml file referencing the `browncompute-registry-secret` secret.

```yaml
spec:
      imagePullSecrets:
        - name: browncompute-registry-secret
      containers:
      - name: "kc-ui"
        image: "us.icr.io/ibmcaseeda/kc-ui:latest"
        imagePullPolicy: Always
```

*Using secret is also mandatory when registry and clusters are not in the same region.*

* Verify current secrets for a give namespace

```shell
kubectl describe secrets -n browncompute
```

* Get a security token: you can use permanent or renewable one:

```shell
ibmcloud cr token-add --description "private registry secret for browncompute" --non-expiring -q
```

* To list the token use the command

```shell
ibmcloud cr tokens
```
The result:
> TOKEN ID     READONLY   EXPIRY   DESCRIPTION
 2b5ff00e-a..  true       0       token for somebody
 3dbf72eb-6..  true       0       private registry secret for browncompute

* To get the token for a given token identifier

```shell
ibmcloud cr token-get cce5a800-...
```

* Define the secret to store the Event stream API key token information:

```shell
kubectl --namespace browncompute create secret docker-registry
browncompute-registry-secret  --docker-server=<registry_url> --docker-username=token --docker-password=<token_value> --docker-email=<docker_email>
```

* Verify the secret

```shell
kubectl get secrets -n browncompute
```

You will see something like below.

> | NAME  | TYPE  | DATA | AGE |
| --- | --- | --- | --- |
| browncompute-registry-secret    |       kubernetes.io/dockerconfigjson     |   1  |       2m |
| default-token-ggwl2  |  kubernetes.io/service-account-token  | 3  |   41m  |
| eventstreams-apikey  |  Opaque   |      1   | 24m  |

Now for each microservice as part of the solution, we have defined helm chart and a script (deployHelm) to deploy to IKS.

This step is done one time only.
See also the product documentation [for more detail.](https://console.bluemix.net/docs/containers/cs_dedicated_tokens.html)

## Basic Kubernetes

## IBM Cloud Kubernetes Service

To create the cluster follow [this tutorial](https://console.bluemix.net/docs/containers/cs_tutorials.html#cs_cluster_tutorial).

* IBM Cloud Kubernetes Service [plug-in](https://cloud.ibm.com/docs/cli/reference/ibmcloud/extend_cli.html#plug-ins) using the following command:

```
ibmcloud plugin install container-service -r Bluemix
```

## OpenShift Container Platform 3.11

## OpenShift Container Platform 4.X

# Deploy application microservices

## Deploy Order Command microservice

!!! note
    Order command microservice implements the Command part of the CQRS pattern. It is done in Java and use Kafka API.

* Go to the repo

```
$ cd refarch-kc-order-ms/order-command-ms
```

* Build the image

```
$ ./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/ordercommandms/ --name ordercmd --set image.repository=ibmcase/kc-ordercommandms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=MINIKUBE --namespace greencompute
```

* Verify service runs

Without any previously tests done, the call below should return an empty array: `[]`
```
curl http://localhost:31200/orders
```

## Deploy Order Query microservice

!!! note
    Order command microservice implements the Query part of the CQRS pattern. It is done in Java and use Kafka API.

* Go to the repo

```
$ cd refarch-kc-order-ms/order-query-ms
```

* Build the image

```
$ ./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/orderqueryms/ --name orderquery --set image.repository=ibmcase/kc-orderqueryms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=MINIKUBE --namespace greencompute
```

* Verify service runs

At the beginning the call below should return an empty array: `[]`
```
curl http://localhost:31100/orders
```

## Deploy Container microservice

The container microservice manage the Reefer container inventory and listen to order created event to assign a container to an order.

!!! warning
    There are multiple different implementations of this service. This note is for the Springboot / Postgresql / Kafka implementation.


**Build and deploy the container manager microservice**

* Go to the repo

```
cd refarch-kc-container-ms/SpringContainerMS
```

* Build the image

```
$ ./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/springcontainerms/ --name containerms --set image.repository=ibmcase/kc-springcontainerms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=MINIKUBE --namespace greencompute
```

* Verify the deployed service:

```
curl http://localhost:30626/containers
```


## Deploy User Interface microservice

The last app is a web application to expose an user interface to run the demonstration end to end.

* Go to the repo

```
cd refarch-kc-ui/
```

* Build the image

```
./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/kc-ui/ --name kcsolution --set image.repository=ibmcase/kc-ui --set image.pullSecret= --set image.pullPolicy=Always --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=MINIKUBE --namespace greencompute
```

* Verify the installed app

Point your web browser to [http://localhost:31010](http://localhost:31010) and login with username: eddie@email.com and password Eddie.

## Deploy Voyages microservice

The *Voyage microservice* is a simple nodejs app to mockup schedule of vessels between two harbors. It is here to illustrate Kafka integration with nodejs app.

* Go to the repo

```
$ cd refarch-kc-ms/voyages-ms
```

** Build the image

```
$ ./scripts/buildDocker.sh MINIKUBE
```

* Deploy on minikube

```
helm install chart/voyagesms/ --name voyages --set image.repository=ibmcase/kc-voyagesms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafkabitnami:9092 --set eventstreams.env=local --namespace greencompute
```

* Verify it is correctly running

```
curl http://localhost:31000/voyage
```

## Deploy the Fleet Simulator microservice

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

TBD

# Universal deployment considerations

When deploying kafka consumer it is important to assess the horizontal pod autoscaler settings and needs, as adding consumers will not address scalability if the number of partitions in the topic(s) to consume does not match the increase of consumers. So disable HPA by default. If you want to use HPA you also need to ensure that a metrics-server is running, then set the number of partition, and the `hpa.maxReplicas` to the number of partitions.
