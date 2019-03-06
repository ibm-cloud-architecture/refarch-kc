# Run locally

To run the full solution locally you can use a kubernetes cluster like Minikube or Docker Edge with kubernetes, or use docker-compose. We propose to use docker-compose for local deployment, and here are the instructions to launch the backbone (kafka and zookeeper) and the solution components:

1. Get [docker and install](https://docs.docker.com/install/) it (if not done yet)
1. Get [docker compose](https://docs.docker.com/compose/install/)
1. Assign at least 8GB of memory and may be 4 to 6 CPUs to your docker runtime. This is set in the Preferences menu and under the `Advanced` tab.
1. Be sure to have the following hostnames: `kafka1 fleetms kcui simulator ordercmd orderquery` mapped to localhost. You can update your `/etc/hosts` file for that.
```
127.0.0.1	localhost kafka1 fleetms simulator ordercmd orderquery kcsolution 
```

1. In one Terminal window, use our compose file to start the backend components: `$ cd docker &&  docker-compose -f backbone-compose.yml up`.    
The first time the backend is started, you need to configure the Kafka topics we are using in the solution. The local script: `scripts/createLocalTopics.sh` will create them.
 > Note: Starting those components will create two folders in the docker folder: `kafka1` and `zookeeper1`. Those folders could be deleted to restart from a fresh environment.  
1. If not done yet, build the solution using the commands: 
 
 ```
 $ cd scripts
 $ ./prepareEnv
 $ ./buildAll
 ```

1. In a second terminal use our second compose file to start the web server and the other microservices: `$ docker-compose -f kc-solution-compose.yml up`

1. Verify the different components work fine. You can use the different test scripts we have defined in each of the microservices or use the following URLs:
  * For the [user interface URL http://localhost:3010](http://localhost:3010)
  * The Fleet Simulator [API URL](http://localhost:9080/api/explorer/) or one of its operation to get the fleet names: http://localhost:9080/fleetms/fleets.
  * Add an order with the `scripts/` in the refarch-kc-orders-ms project
  * The voyages http://localhost:3100/voyage
  * The order query microservice http://localhost:11080/orders/byManuf/GoodManuf

or run a smoke test with the script: `localSmokeTests`.

Read the [demo script](../demo/readme.md) to see how all those components working together to demonstrate the business process.

### Build

This project includes some scripts to help build the full solution once all the repositories are cloned. If you have some problem during this integrated build we recommend going into each project to assess the build process in detail. Also for development purpose, going into each project, you can learn how to build and run locally.

* To be able to build without or docker image for building, you need npm, node, maven and docker:
  * Get [docker and install](https://docs.docker.com/install/) it (if not done yet).
  * Get [maven](https://maven.apache.org/install.html) and add it to your PATH
  * Get [node and npm](https://nodejs.org/en/)

* Build all projects in one command by executing: `scripts/buildAll`
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