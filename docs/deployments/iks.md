# IKS Deployment

## Prepare IBM Cloud Services to run the solution

IBM Cloud offers a set of services to run part of your event driven architecture. We are using the following services for our reference implementation:
* [Kubernetes Service](https://cloud.ibm.com/containers-kubernetes/catalog/cluster)
* [Streaming Analytics Service](https://cloud.ibm.com/catalog/services/streaming-analytics)
* [Event Streams](https://cloud.ibm.com/catalog/services/event-streams)

At the high level the deployed solution will look like the following:

![ic-deployment](ic-deployment.png)  

## Pre-requisites

* Create an account on [IBM Cloud](https://cloud.ibm.com).
* Install the following CLIs:
    * [Docker CLI](https://docs.docker.com/install/)
    * [IBM Cloud CLI](https://cloud.ibm.com/docs/cli/reference/ibmcloud/download_cli.html#install_use)
    * IBM Cloud Kubernetes Service [plug-in](https://cloud.ibm.com/docs/cli/reference/ibmcloud/extend_cli.html#plug-ins) using the following command:
      ```sh
      $ ibmcloud plugin install container-service -r Bluemix
      ```
    * [Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
    * IBM Cloud Container Registry plug-in
      ```sh
      $ ibmcloud plugin install container-registry -r Bluemix
      ```

The following diagram illustrates the command lines interface and how they interact with IBM Cloud components:

![](ic-cli-comp.png)

All our docker images for this solution are in public docker registry: dockerhub under the [`ibmcase` namespace](https://cloud.docker.com/u/ibmcase). This means using our images may work for your deployment if you configure the secrets and other configuration files to point to your services (see detail [in this section](#using-api-keys)) 

It is recommended that you use your own private image repository, so the following section should be performed.

## Define an image private repository

Use the [docker container image private registry](https://console.bluemix.net/containers-kubernetes/catalog/registry) to push your images and then deploy them to IBM Kubernetes Service. When deploying enterprise application it is strongly recommended to use private registry to protect your images from being used and changed by unauthorized users. Private registries must be set up by the cluster admin to ensure that the credentials to access the private registry are available to the cluster users. In the Catalog Use the `Containers` category and `Container Registry` tile. Create the repository with the `create` button. You can share a repository for multi IKS clusters.

Once you access your registry, create a namespace for your solution. We used `ibmcaseeda`. 

![](iks-registry-ns.png)

We will use this namespace when tagging the docker images for our microservice. But first let add a kubernetes cluster.

## Kubernetes Cluster Service

If you need to know more about kubernetes, read the [basic concepts here](https://kubernetes.io/docs/tutorials/kubernetes-basics/).

To create the cluster follow [this tutorial](https://console.bluemix.net/docs/containers/cs_tutorials.html#cs_cluster_tutorial).

Here is an image of our cluster, with 3 nodes and the smallest configuration:

![](./iks-cluster.png) 

To access to the cluster use the following command:
```sh
# login to IBM Cloud. Do not need to be done each time.
$ ibmcloud login -a https://api.us-east.bluemix.net

# Target the IBM Cloud Container Service region in which you want to work.
$ ibmcloud cs region-set us-east

# You may need to update the CLI, as it changes quite often
$ ibmcloud plugin update container-service

# Set the KUBECONFIG environment variable.
$ export KUBECONFIG=/Users/$USER/.bluemix/plugins/container-service/clusters/fabio-wdc-07/kube-config-wdc07-fabio-wdc-07.yml

# Verify you have access to your cluster by listing the node:
$ kubectl get nodes
```

To set the cluster config to your cluster use: `ibmcloud ks cluster-config <cluster_name_or_ID>`

As it is recommended to ilosate your deployment from kubernetes default setting, create a namespace that can be the same as the container registry namespace name or something else. Below we create the browncompute namespace: `kubectl create namespace browncompute`.

## Event Streams Service on IBM Cloud

To provision your service, go to the IBM Cloud Catalog and search for `Event Streams`. It is in the Integration category. Create the service and specify a name, a region, and a space. 

* In the service credentials create new credentials to get the Kafka broker list, the admim URL and the api_key needed to authenticate the consumers or producers.

 ![](./IES-IC-credentials.png)

 We will use a kubernetes secret to define the api key (see detail [in this section](#using-api-keys))
* In the Manage panel add the topics needed for the solution. We need at least the following:

 ![](./IES-IC-topics.png) 


## Streaming Analytics Service

The documentation located [here](https://github.com/ibm-cloud-architecture/refarch-kc-streams#application-development-and-deployment) describes how to configure the IBM Cloud based Streaming Analytics Service and how to build/deploy the example application. 


## Run the solution on IBM Cloud Kubernetes Services

The Event streams broker API key is needed to connect any deployed consumers or producers within kubernetes cluster to access the service in IBM Cloud. To avoid sharing the key with public github we propose to define a kubernetes secret and deploy it to the IKS cluster.

1. Define a Event Stream API key secret: To use Event Streams, we need to get the API key and configure a secret to the `browncompute` namespace.  
  ```
  $ kubectl create secret generic eventstreams-apikey --from-literal=binding='<replace with api key>' -n browncompute
  # Verify the secrets
  $ kubectl get secrets -n browncompute
  ```   
  This secret is used by all the solution microservices which are using Kafka. The detail of how we use it with environment variables, is described in one of the project [here](https://github.com/ibm-cloud-architecture/refarch-kc-ms/blob/master/fleet-ms/README.md#run-on-ibm-cloud-with-kubernetes-service)  

2. Define a secret to access the IBM CLoud docker image private repository so when your IKS instance accesses docker images it will authenticate. This is also mandatory when registry and clusters are not in the same region.   
  ```
  kubectl get secret bluemix-default-secret-regional -o yaml | sed 's/default/browncompute/g' | kubectl -n browncompute create -f -   
  ```   
  Verify the secret   
  ```
  $ kubectl get secrets -n browncompute  
  ```   
  You will see something like below.   
   
  | NAME  | TYPE  | DATA | AGE |  
  | --- | --- | --- | --- |
  | bluemix-browncompute-secret-regional   |  kubernetes.io/dockerconfigjson  |   1   |    22m  |
  | default-token-ggwl2  |  kubernetes.io/service-account-token  | 3  |   41m  |  
  | eventstreams-apikey  |  Opaque   |      1   | 24m  |   

  Now for each microservice of the solution, we have defined a helm chart and a script (deployHelm) to deploy it to IKS.   
3. Push images to your IBM Cloud private image repository. If not connected to IBM Cloud do the following:   
  ```  
  $ ibmcloud login -a https://api.us-east.bluemix.net
  ```  
  # Target the IBM Cloud Container Service region in which you want to work.   
  ```
  $ ibmcloud ks region-set us-east   
  ```  
  # Set the KUBECONFIG environment variable.   
  ```
  $ ibmcloud ks cluster-config fabio-wdc-07
  $ export KUBECONFIG=/Users/$USER/.bluemix/plugins/container-service/clusters/fabio-wdc-07/kube-config-wdc07-fabio-wdc-07.yml   
  ```  
  # Verify you have access to your cluster by listing the node:   
  ```
  $ kubectl get nodes   

  # login to the container registry
  $ ibmcloud cr login
  ```   
  Then execute the script: `./scripts/pushToPrivate`  
4. Verify the images are in you private repo:
 ```
 $ ibmcloud cr image-list
 ```
4. Deploy the helm charts for each components using the `scripts/deployHelms`.   
5. Verify the deployments and pods:  
    ```
    $ kubectl get deployments -n browncompute
    ```

  | NAME | DESIRED | CURRENT  | UP-TO-DATE  | AVAILABLE  | AGE |
  | --- | --- | --- | --- | --- | --- |
  | fleetms-deployment  |  1  |       1     |    1     |       1     |      23h |
  | kc-ui              |  1  |  1  |  1   |  1  |     18h |
  | ordercommandms-deployment | 1  | 1  | 1  |  1  |   1d |
  | orderqueryms-deployment | 1  |   1 |  1  |  1  |   23h  |
  | voyagesms-deployment |   1   |  1  |  1  |  1  |   19h |    

  ```  
    $  kubectl get pods -n browncompute
  ``` 

  | NAME |                                       READY  |   STATUS  |  RESTARTS |  AGE |
  | --- | --- | --- | --- | --- |
  | fleetms-deployment-564698b998-7pb2n   |      1/1   |    Running  | 0    |      23h |
  | kc-ui-749d7df9db-jl6tv          |           1/1      | Running  | 0       |   14h |
  | ordercommandms-deployment-d6dc4fdc7-5wjtp |  1/1   |  Running  | 0      |    1d | 
  | orderqueryms-deployment-5db96455f-6fqp5   |  1/1   |   Running |  0     |     23h |  
  | voyagesms-deployment-6d7f8cdc8d-hnvq6     |  1/1   |    Running |  0     |     19h |   

6. You can perform a smoke test with the `scripts/smokeTests`.   
7. Access the kubernetes console from your IKS deployment to see the deployment   

> It is possible to get an authentication / authorization issue when IKS service try to access the image from the private registry. This may be due to a security token expired. The following commands can be execute:
  ```
  
  ```
