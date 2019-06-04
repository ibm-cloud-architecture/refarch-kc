## Get the app

git clone https://github.com/ibm-cloud-architecture/refarch-kc.git

cd refarch-kc/

./scripts/clone.sh

## Setting up Kafka and Zookeeper

### On Docker

1. Deploying Kafka and Zookeeper on Docker

```
$ cd docker && docker-compose -f backbone-compose.yml up -d >& backend.logs

$ ./scripts/createLocalTopics.sh
```

### On Minikube

1. Create a namespace.

```
kubectl create namespace greencompute
```

2. Deploy kafka and zookeeper using helm

```
helm install --name kafka --set persistence.enabled=false confluentinc/cp-helm-charts --namespace greencompute
```

3. Deploy kafka client pod.

```
kubectl apply -f ./minikube/kafka_client.yaml -n greencompute
```

4. Log into the Pod

```
kubectl exec -it kafka-client bash -n greencompute
```

5. Go to `bin` folder.

```
$ cd bin
```

6. Create the topics.

```
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic bluewaterContainer --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic bluewaterShip --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic bluewaterProblem --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic orders --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic errors --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic containers --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic containerMetrics --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic rejected-orders --create --partitions 1 --replication-factor 1 --if-not-exists
kafka-topics --zookeeper kafka-cp-zookeeper-headless:2181 --topic allocated-orders --create --partitions 1 --replication-factor 1 --if-not-exists
```

7. Enter `exit` to come out of it.

## Fleet ms

1. Go to the repo

```
$ cd refarch-kc-ms/fleet-ms
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

3. Deploy on docker

```
$ docker run -it --name fleetms -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -d -p 9080:9080 -p 9444:9443 ibmcase/kc-fleetms
```

4. Deploy on minikube

```
helm install chart/fleetms/ --name fleetms --set image.repository=ibmcase/kc-fleetms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
```

## Voyage ms

1. Go to the repo

```
$ cd refarch-kc-ms/voyages-ms
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

3. Deploy on docker

```
$ docker run -it --name voyages -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 3100:3000 ibmcase/kc-voyagesms
```

4. Deploy on minikube

```
helm install chart/voyagesms/ --name voyages --set image.repository=ibmcase/kc-voyagesms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
```

## Order command ms

1. Go to the repo

```
$ cd refarch-kc-order-ms/order-command-ms
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

3. Deploy on docker

```
$ docker run -it --name ordercmd -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 10080:9080 ibmcase/kc-ordercommandms
```

4. Deploy on minikube

```
helm install chart/ordercommandms/ --name ordercmd --set image.repository=ibmcase/kc-ordercommandms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
```

## Order query ms

1. Go to the repo

```
$ cd refarch-kc-order-ms/order-query-ms
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

3. Deploy on docker

```
$ docker run -it --name orderquery -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 11080:9080 ibmcase/kc-orderqueryms
```

4. Deploy on minikube

```
helm install chart/orderqueryms/ --name orderquery --set image.repository=ibmcase/kc-orderqueryms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
```

## Container ms

1. Go to the repo

```
cd refarch-kc-container-ms/SpringContainerMS
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

ENV can be LOCAL, IBMCLOUD or ICP based on where you need to deploy.

3. Deploy on docker

```
docker run --name springcontainerms \
--network docker_default \
  -e KAFKA_ENV=$KAFKA_ENV \
  -e KAFKA_BROKERS=$KAFKA_BROKERS \
  -e KAFKA_APIKEY=$KAFKA_APIKEY \
  -e POSTGRESQL_URL=$POSTGRESQL_URL \
  -e POSTGRESQL_CA_PEM="$POSTGRESQL_CA_PEM" \
  -e POSTGRESQL_USER=$POSTGRESQL_USER \
  -e POSTGRESQL_PWD=$POSTGRESQL_PWD \
  -e TRUSTSTORE_PWD=${TRUSTSTORE_PWD} \
  -p 8080:8080 -ti  ibmcase/kc-springcontainerms
```

## Web

1. Go to the repo

```
cd refarch-kc-ui/
```

2. Build the image

```
$ ./scripts/buildDocker.sh
```

3. Deploy on docker

```
docker run -it --name kcsolution -e KAFKA_BROKERS="<your_kafka_brokers>" -e FLEET_MS_URL="<fleetms_url" ORDER_MS_URL="<orderms_url>" VOYAGE_MS_URL="<voyagems_url>" --link fleetms:fleetms --link voyages:voyages --link ordercmd:ordercmd --link orderquery:orderquery --link springcontainerms:springcontainerms -d -p 3110:3010 ibmcase/kc-ui
```
