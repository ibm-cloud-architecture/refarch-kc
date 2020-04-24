# Security

This section addresses some challenges and best practices to support security for event-driven microservice integrating Kafka consumer or producer, or both, into the code, and CI/CD platform.

Kafka [consumers](https://ibm-cloud-architecture.github.io/refarch-eda/kafka/consumers/) and [producers](https://ibm-cloud-architecture.github.io/refarch-eda/kafka/producers/) need at least the broker URLs, the security API key in the case of Event Stream deployed on IBM Cloud public or private, and the SSL certificate as the communication is encrypted. 

Applying the "store config in the environment" rule of [the 12 factors](https://12factor.net/) manisfesto, we are using the following environment variables:

```
export KAFKA_BROKERS="localhost:9092"
export KAFKA_APIKEY="nokey"
export KAFKA_ENV="LOCAL"
export POSTGRESQL_URL="jdbc:postgresql://localhost:5432/postgres"
export POSTGRESQL_USER="postgres"
export POSTGRESQL_PWD="supersecret"
export POSTGRESQL_CA_PEM=""
```

The settings above are for running locally on the developer's laptop. To support the different environment (LOCAL, ICP, IBMCLOUD), we have a `scripts/setenv.sh` bash script to help export those variables. We are providing a template for this file in the file: [setenv.sh.tmpl](https://github.com/ibm-cloud-architecture/refarch-kc/blob/master/scripts/setenv.sh.tmpl) 

The settings are a little bit different for public cloud and private cloud. 

## IBM Cloud

For public cloud we need to get the credentials for Event Streams service (see the explanations and figures in [this note](../deployments/iks/#event-streams-service-on-ibm-cloud)) and for the postgresql service in [this note](../deployments/iks/#the-postgresql-service). 

For the Postgresql certificate the following command helps to get it. You may need to install the cloud database CLI with the command `ibmcloud plugin install cloud-databases`

```
ibmcloud cdb deployment-cacert <name-of-postgres-service> > postgresql.crt
```

This file will be used for adding certificate in the Java Truststore. 

## Certificate - Java Truststore - Docker

We have encoutered some challenges to inject SSL certificate in truststore when using Docker build stage. We have implemented scripts to do the following:

* add certificate to trustore using openssl and  keytool. [This script](https://github.com/ibm-cloud-architecture/refarch-kc-container-ms/blob/master/SpringContainerMS/scripts/add_certificates.sh) has to be run during the build stage, as unit tests are run inside the docker it needs to get certificate for maven, but it also need to execute when the container start in the deployed cluster. See the multi-stages [dockerfile here](https://github.com/ibm-cloud-architecture/refarch-kc-container-ms/blob/master/SpringContainerMS/Dockerfile).
* a startup script to start the java application, but calling the add certificate script and set the Java options.

The [Springboot implementation](https://ibm-cloud-architecture.github.io/refarch-kc-container-ms/springboot/) of the container management microservice uses this approach. Environment variables are used for passing values to maven, for the build and unit tests, and to Java for runtime. 
