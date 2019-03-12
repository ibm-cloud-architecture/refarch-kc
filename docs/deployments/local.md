# Run with Docker Compose

To run the full solution locally you can use a kubernetes cluster like Minikube or Docker Edge with kubernetes, or use docker-compose. We propose to use docker-compose for local deployment.

## Pre requisites 

1. Get [docker and install](https://docs.docker.com/install/) it (if not done yet)
1. Get [docker compose](https://docs.docker.com/compose/install/)
1. Assign at least 8GB of memory and may be 4 to 6 CPUs to your docker runtime. This is set in the Preferences menu and under the `Advanced` tab.
1. Be sure to have the following hostnames: `kafka1 fleetms kcui simulator ordercmd orderquery` mapped to localhost. You can update your `/etc/hosts` file for that.
```
127.0.0.1	localhost kafka1 fleetms simulator ordercmd orderquery kcsolution 
```
1. If not already done, get a git client. See the folloing [installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 
1. Be sure to have cloned this repository using git command: `git clone https://github.com/ibm-cloud-architecture/refarch-kc/`


## Start Kafka and Zookeeper

1. In one Terminal window, use our compose file to start the backend components:   

    `$ cd docker &&  docker-compose -f backbone-compose.yml up`.

1. The first time the backend is started, you need to configure the Kafka topics we are using in the solution. The local script: `scripts/createLocalTopics.sh` will create them.
 > Note: Starting those components will create two folders in the docker folder: `kafka1` and `zookeeper1`. Those folders could be deleted to restart from a fresh environment.  

## Build the solution

This project includes some scripts to help build the full solution once all the repositories are cloned. If you have some problem during this integrated build we recommend going into each project to assess the build process in detail. Also, for development purpose, going into each project, you can learn how to build and run locally.

We are using polyglote implementations so if you do not want to overload your own laptop we propose to use docker images to get development environments for nodes, python and java. (Three separate images). This will help to do not pollute your computer. So if you want to do so here are three commands to build the three images (those images are also in docker hub). 

```sh
cd scripts
# build the image for java:
docker build -f docker-java-tools -t ibmcase/javatools .
# build the image for nodejs, angular, npm
docker build -f docker-java-tools -t ibmcase/javatools .
# build the image for python
cd ../itg-tests
docker build  -t ibmcase/python .
```

* To be able to build without our docker image for building, you need npm, node, maven and docker:  
     * Get [docker and install](https://docs.docker.com/install/) it (if not done yet).
     * Get [maven](https://maven.apache.org/install.html) and add it to your PATH.
     * Get [node and npm](https://nodejs.org/en/)
* Build all projects in one command by executing: `scripts/buildAll` from this project. This command may use the docker images  build previously if they are visible via the command `docker images`. If not it will build using maven, npm and angular cli.
* Use the `scripts/imageStatus` script to verify your docker images are built:

```
 ibmcase/kc-ui                                        latest              c89827424689        15 hours ago        596MB  
 registry.ng.bluemix.net/ibmcaseeda/kc-ui             latest              c89827424689        15 hours ago        596MB  
 ibmcase/kc-orderqueryms                              latest              09406c8795e8        23 hours ago        548MB   
 registry.ng.bluemix.net/ibmcaseeda/kc-orderqueryms   latest              09406c8795e8        23 hours ago        548MB   
 ibmcase/kc-ordercmdms                                latest              5190db45e4bf        23 hours ago        548MB   
 registry.ng.bluemix.net/ibmcaseeda/kc-ordercmdms     latest              5190db45e4bf        23 hours ago        548MB   
 ibmcase/kc-voyagesms                                 latest              54b8d6a61f4e        23 hours ago        1.16GB   
 registry.ng.bluemix.net/ibmcaseeda/kc-voyagesms      latest              54b8d6a61f4e        23 hours ago        1.16GB   
 ibmcase/kc-fleetms                                   latest              a5e1d40a8b1f        23 hours ago        616MB   
 registry.ng.bluemix.net/ibmcaseeda/kc-fleetms        latest              a5e1d40a8b1f        23 hours ago        616MB   
```

* If you want to delete the docker images after tesing the solution, use the command:
`docker rmi $(docker -aq | grep ibmcase)`

## Start all the microservices

1. In a second terminal windows, use our second docker compose file to start the web server and the other microservices: `$ docker-compose -f kc-solution-compose.yml up`

1. Verify the different components work fine. You can use the different test scripts we have defined in each of the microservices or use the following URLs:
  * For the [user interface URL http://localhost:3010](http://localhost:3010)
  * The Fleet Simulator [API URL](http://localhost:9080/api/explorer/) or one of its operation to get the fleet names: [http://localhost:9080/fleetms/fleets](http://localhost:9080/fleetms/fleets).
  * Add an order with the `scripts/` in the refarch-kc-orders-ms project
  * The voyages [http://localhost:3100/voyage](http://localhost:3100/voyage)
  * The order query microservice [http://localhost:11080/orders/byManuf/GoodManuf](http://localhost:11080/orders/byManuf/GoodManuf)

or run the smoke tests with the script: `localSmokeTests`.

Read the [demo script](../demo/readme.md) to see how all those components working together to demonstrate the business process.

