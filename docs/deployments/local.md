# Run the solution on your laptop

In this document we present how to set up, step by step, your local environment with some of the components deployed on IBM Cloud. To run the full solution locally you can use a kubernetes cluster, like Minikube or Docker Edge with kubernetes, or use docker-compose. We propose to use docker-compose for local deployment. The environment we put in place looks as the diagram below:

![]()


## Pre requisites 

* Get [docker and install](https://docs.docker.com/install/) it (if not done yet.) To verify docker runs fine use the command `docker version`
* Get [docker compose](https://docs.docker.com/compose/install/). To verify it runs enter `docker-compose version`.
* Assign at least 8GB of memory and may be 4 to 6 CPUs to your docker runtime. This is set in the Docker's Preferences menu and under the `Advanced` tab.

![](docker-preferences.png)

* Be sure to have the following hostnames: `kafka1 fleetms kcui simulator ordercmd orderquery` mapped to localhost. You can update your `/etc/hosts` with the following line.  

```
  127.0.0.1	localhost kafka1 fleetms simulator ordercmd orderquery kcsolution 
```
* If not already done, get a git client. See the following [installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git). 
* Be sure to have cloned this repository using git command: `git clone https://github.com/ibm-cloud-architecture/refarch-kc/`. Open a terminal and go to the `refarch-kc` folder.
* Use the command `./script/clone.sh` to get all the solution repositories. You should have at least the following:
```
refarch-kc-container-ms
refarch-kc-order-ms
refarch-kc-ui
refarch-kc
refarch-kc-ms
refarch-kc-streams
```
* We propose you to have two choices to build the solution: installing node, python and maven or use our own docker images for running those tools. It can be a mix too, for example if you already develop on nodejs or Java you may want to leverage your own env. See the [build section](#build-the-solution) below.

* To be able to build without our docker image for building, you need npm, node, maven and docker:  
     * Get [docker and install](https://docs.docker.com/install/) it (if not done yet).
     * Get [maven](https://maven.apache.org/install.html) and add it to your PATH.
     * Get [node and npm](https://nodejs.org/en/)
     * For python you can use the one from your computer, but we encourage you to use our python docker image. See the [build section](#build-the-solution) below.

## Start Kafka and Zookeeper

* In one Terminal window, under the `refarch-kc` folder, use our compose file to start the backend components:   

    `$ cd docker &&  docker-compose -f backbone-compose.yml up`.

It will take some time as it download zookeeper and kafka docker images from dockerhub. When started you should see the following trace:
```
Creating docker_zookeeper1_1 ... done
Creating docker_kafka1_1     ... done
Attaching to docker_zookeeper1_1, docker_kafka1_1
....
```

* The first time the kafka backbone is started, you need to configure the Kafka topics we are using in the solution. The local script: `scripts/createLocalTopics.sh` will create them.
 > Note: Starting those components will create two folders in the docker folder: `kafka1` and `zookeeper1`. Those folders could be deleted to restart from a fresh environment.  

## Build the solution

This project includes some scripts to help build the full solution once all the repositories are cloned. If you have some problem during this integrated build we recommend going into each project to assess the build process in detail. Also, for development purpose, going into each project, you can learn how to build and run locally.

We are using polyglote implementations so if you do not want to overload your own laptop with the different repositories, we propose to use docker images to get development environments for nodes, python and java. (Three separate images). This will help you to do not pollute your computer. Therefore if you want to use those images, run the three commands below: to build the three images (those images are also in docker hub). 

```sh
cd scripts
# build the image for java:
docker build -f docker-java-tools -t ibmcase/javatools .
# build the image for nodejs, angular, npm
docker build -f docker-node-tools -t ibmcase/nodetools .
# build the image for python
docker build  -f docker-python-tools -t ibmcase/python .
```

To validate the current images run `docker images`

![](images-1.png)


> you have two approaches to build the solution, one using a unique command, or going into each project and follow the local build instructions. From an education point of view we encourag to do the second approach:

1. You can build all projects in one command by executing: `scripts/buildAll LOCAL` from this project. This command may use the docker images  build previously if they are visible via the command `docker images`. If not it will build using maven, npm and angular cli. Some tests use kafka, we did not isolate well all the unit tests yet. So be sure to have kafka running as describe in the previous session: [ Start Kafka and Zookeeper](#start-kafka-and-zookeeper).
1. Build on project at a time in the following order:
    
      * [Build the fleet simulator microservice](). This is component done in java, to expose API to get fleets and ships and simulation APIs. When running it generates events for the ship mouvement and the container metrics. 

Use the `scripts/imageStatus` script to verify your docker images are built:

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

* If you want to delete the docker images after testing the solution, use the command:
`docker rmi $(docker -aq | grep ibmcase)`

## Start all the microservices

1. In a second terminal window, use our second docker compose file to start the web server and the other microservices: `$ docker-compose -f kc-solution-compose.yml up`

1. Verify the different components work fine. You can use the different test scripts we have defined in each of the microservices or use the following URLs:
  * For the [user interface URL http://localhost:3010](http://localhost:3010)
  * The Fleet Simulator [API URL](http://localhost:9080/api/explorer/) or one of its operation to get the fleet names: [http://localhost:9080/fleetms/fleets](http://localhost:9080/fleetms/fleets).
  * Add an order with the `scripts/` in the refarch-kc-orders-ms project
  * The voyages [http://localhost:3100/voyage](http://localhost:3100/voyage)
  * The order query microservice [http://localhost:11080/orders/byManuf/GoodManuf](http://localhost:11080/orders/byManuf/GoodManuf)

or run the smoke tests with the script: `localSmokeTests`.

Read the [demo script](../demo/readme.md) to see how all those components working together to demonstrate the business process.

