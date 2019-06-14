# Reefer Container Shipment solution - EDA reference implementation

As part of producing the IBM event driven point of view and reference architecture, we wanted to bring together a complete scenario which would cover all aspects of developing an event driven solutions including extended connections to devices/IOT and blockchain for trusted business trading networks. We felt that the shipping business could provide a good foundation for this and would enable us to show how to develop event driven solutions following the architecture patterns.

## TL;TR

If you want to just get the code, build and run we propose running locally with Minikube or Docker-compose.

To build and run the solution locally, please follow the below instructions.

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

2. Add the helm repo.

```
helm repo add bitnami https://charts.bitnami.com
```

2. Deploy kafka and zookeeper using helm

```
helm install --set persistence.enabled=false --name my-release bitnami/kafka --namespace greencompute
```

3. Deploy kafka client pod.

```
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=my-release,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
```

4. Create the topics.

```
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic bluewaterContainer
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic bluewaterShip
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic bluewaterProblem
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic orders
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic errors
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic containers
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic containerMetrics
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic rejected-orders
kubectl exec -it $POD_NAME -- kafka-topics.sh --create --zookeeper my-release-zookeeper:2181 --replication-factor 1 --partitions 1 --topic allocated-orders
```

5. Deploy postgresql using helm.

```
helm install --name postgre-db \
  --set postgresqlPassword=supersecret \
  --set persistence.enabled=false \
    stable/postgresql --namespace greencompute
```

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

### Getting the certs for PostgreSQL

PostgreSQL (Using the cloud instance)

Spring Container MS

$ ibmcloud cdb deployment-cacert <your-DB-PostgreSQL>
# if you do not have the cloud database plugin does the following and rerun previous command:
$ ibmcloud plugin install cloud-databases

# transform
$ openssl x509 -in postgressql.crt -out postgressql.crt.der -outform der
# save in keystore
$ keytool -keystore clienttruststore -alias postgresql -import -file postgressql.crt.der -storepass changeit

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

4. Create required secrets.

```
kubectl create secret generic postgresql-url --from-literal=binding='jdbc:postgresql://postgre-db-postgresql:5432/postgres' -n greencompute

kubectl create secret generic postgresql-user --from-literal=binding='postgres' -n greencompute

kubectl create secret generic postgresql-pwd --from-literal=binding='supersecret' -n greencompute
```

4. Deploy on minikube

```
helm install chart/springcontainerms/ --name containerms --set image.repository=ibmcase/kc-springcontainerms --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
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

4. Deploy on minikube

```
helm install chart/kc-ui/ --name kcsolution --set image.repository=ibmcase/kc-ui --set image.pullSecret= --set image.pullPolicy=IfNotPresent --set eventstreams.brokers=kafka-cp-kafka:9092 --set eventstreams.env=local --namespace greencompute
```
