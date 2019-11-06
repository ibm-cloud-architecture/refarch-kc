# Build and run using docker-compose

To build and run the solution locally using docker, please follow the below instructions.

## Get the app

git clone https://github.com/ibm-cloud-architecture/refarch-kc.git

cd refarch-kc/

./scripts/clone.sh

## Setting up Kafka and Zookeeper

1. Deploying Kafka and Zookeeper on Docker

```
$ cd docker && docker-compose -f backbone-compose.yml up -d >& backend.logs

$ ./scripts/createLocalTopics.sh
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
$ docker run -it --name fleetms -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -d -p 9080:9080 -p 9444:9443 ibmcase/kcontainer-fleet-ms
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
$ docker run -it --name voyages -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 3100:3000 ibmcase/kcontainer-voyages-ms
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
$ docker run -it --name ordercmd -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 10080:9080 ibmcase/kcontainer-order-command-ms
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
$ docker run -it --name orderquery -e KAFKA_BROKERS="<your_kafka_brokers>" -e KAFKA_ENV="<LOCAL or IBMCLOUD or ICP>" -e KAFKA_APIKEY="<your_kafka_api_key>" -d -p 11080:9080 ibmcase/kcontainer-order-query-ms
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
  -p 8080:8080 -ti  ibmcase/kcontainer-spring-container-ms
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
docker run -it --name kcsolution -e KAFKA_BROKERS="<your_kafka_brokers>" -e FLEET_MS_URL="<fleetms_url" ORDER_MS_URL="<orderms_url>" VOYAGE_MS_URL="<voyagems_url>" --link fleetms:fleetms --link voyages:voyages --link ordercmd:ordercmd --link orderquery:orderquery --link springcontainerms:springcontainerms -d -p 3110:3010 ibmcase/kcontainer-ui
```
