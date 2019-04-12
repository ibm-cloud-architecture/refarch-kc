# IKS Deployment

In this document, you will learn 
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

All our docker images for this solution are in public docker registry: dockerhub under the [`ibmcase` namespace](https://cloud.docker.com/u/ibmcase). But all the helm charts to deploy each component of the solution use private repository like: `us.icr.io/ibmcaseeda/`. As it is recommended to use your own private image repository, we are presenting a quick summary of what to do in the next section.

## Define an image private repository

Use the [docker container image private registry](https://cloud.ibm.com/containers-kubernetes/catalog/registry) to push your images and then deploy them to IBM Kubernetes Service. When deploying enterprise application it is strongly recommended to use private registry to protect your images from being used and changed by unauthorized users. Private registries must be set up by the cluster admin to ensure that the credentials to access the private registry are available to the cluster users. In the Catalog Use the `Containers` category and `Container Registry` tile. Create the repository with the `create` button. You can share a repository between multi IKS clusters within the same region.

Once you access your registry, create a namespace for your solution. We used `ibmcaseeda` name. 

*The namespace can also be created with the command: `ibmcloud cr namespace-add ibmcaseeda`* 

![](iks-registry-ns.png)

We will use this namespace when tagging the docker images for our microservices. Here is an example of tagging:

```shell
docker tag ibmcase/kc-ui us.icr.io/ibmcaseeda/kc-ui:latest
```
To see the images in your private registry you can use the user interface at [https://cloud.ibm.com/containers-kubernetes/registry/main/private](https://cloud.ibm.com/containers-kubernetes/registry/main/private) or the command: `ibmcloud cr image-list`
But first let add a kubernetes cluster.

## Kubernetes Cluster Service

If you need to know more about kubernetes, read the [basic concepts here](https://kubernetes.io/docs/tutorials/kubernetes-basics/), see also our summary [here](https://jbcodeforce.github.io/#/studies).

To create the cluster follow [this tutorial](https://console.bluemix.net/docs/containers/cs_tutorials.html#cs_cluster_tutorial).

Here is an image of our cluster, with 3 nodes and the smallest configuration:

![](./iks-cluster.png) 

To access to the cluster use the following command:
```sh
# login to IBM Cloud. Do not need to be done each time.
$ ibmcloud login -a https://api.us-east.bluemix.net

# Target the IBM Cloud Container Service region in which you want to work.
$ ibmcloud ks region-set us-east

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

### Event stream API key

The Event streams broker API key is needed to connect any deployed consumers or producers within kubernetes cluster to access the service in IBM Cloud. To avoid sharing security keys, we propose to define a kubernetes secret and deploy it to the IKS cluster.

Define a Event Stream API key secret: To use Event Streams, we need to get the API key and configure a secret under the `browncompute` namespace.  

```shell
$ kubectl create secret generic eventstreams-apikey --from-literal=binding='<replace with api key>' -n browncompute
# Verify the secrets
$ kubectl describe secrets -n browncompute
```   

This secret is used by all the solution microservices which are using Kafka / Event Streams. The detail of how we use it with environment variables, is described in one of the project [here](https://github.com/ibm-cloud-architecture/refarch-kc-ms/blob/master/fleet-ms/README.md#run-on-ibm-cloud-with-kubernetes-service)  

### Private Registry Token

Each helm chart specify the name of an image to load to create the containers / pods. The image name is from a private repository. To let kubernetes scheduler being able to access the registry, we need to define a secret to hold the security token. Here is an extract of a deployment yaml referencing the `browncompute-registry-secret` secret.

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

```shell
# Verify current secrets for a give namespace
$ kubectl describe secrets -n browncompute

# Get a security token: you can use permanent or renewable one:
$ ibmcloud cr token-add --description "private registry secret for browncompute" --non-expiring -q

# To list the token use the command
$  ibmcloud cr tokens
TOKEN ID     READONLY   EXPIRY   DESCRIPTION   
2b5ff00e-a..  true       0       token for somebody
3dbf72eb-6..  true       0       private registry secret for browncompute

# To get the token for a given token identifier
$ ibmcloud cr token-get cce5a800-...

# Define the secret to store the token information
$ kubectl --namespace browncompute create secret docker-registry browncompute-registry-secret  --docker-server=<registry_url> --docker-username=token --docker-password=<token_value> --docker-email=<docker_email>
 
```   
Verify the secret   
```
$ kubectl get secrets -n browncompute  
```   
You will see something like below.   
  
| NAME  | TYPE  | DATA | AGE |  
| --- | --- | --- | --- |
| browncompute-registry-secret    |       kubernetes.io/dockerconfigjson     |   1  |       2m |
| default-token-ggwl2  |  kubernetes.io/service-account-token  | 3  |   41m  |  
| eventstreams-apikey  |  Opaque   |      1   | 24m  |   

Now for each microservice as part of the solution, we have defined helm chart and a script (deployHelm) to deploy to IKS. 

This step is done one time only.
See also the product documentation [for more detail.](https://console.bluemix.net/docs/containers/cs_dedicated_tokens.html)

### Push images

This step is done each time you want to deploy the solution to IKS. When using continuous deployment, this step will be automated.

If you are not connected to IBM Cloud, do the following:   
```sh
$ ibmcloud login -a https://api.us-east.bluemix.net
 
# Target the IBM Cloud Container Service region in which you want to work.   
$ ibmcloud ks region-set us-east   

# Set the KUBECONFIG environment variable.   

$ ibmcloud ks cluster-config fabio-wdc-07

$ export KUBECONFIG=/Users/$USER/.bluemix/plugins/container-service/clusters/fabio-wdc-07/kube-config-wdc07-fabio-wdc-07.yml   

# Verify you have access to your cluster by listing the node:   
$ kubectl get nodes   

# login to the container registry
$ ibmcloud cr login
```   

Then execute the script: `./scripts/pushToPrivate`  to deploy all component, or go to each repository and use the script `deployHelm`.

* Verify the images are in you private repo:
 ```
 $ ibmcloud cr image-list
 ```

* Deploy the helm charts for each components using the `scripts/deployHelms`.   
* Verify the deployments and pods:  
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

* You can perform a smoke test with the `scripts/smokeTestsIKS` or you can try to access some of the read APIs using the web browser. So first to get the public IP address of your cluster, go to the `Worker Nodes` view of the Clusters console.  Then to get the service exposed NodePort use `kubectl get services -n browncompute` and then get the port number mapped from one of the exposed ports (9080, 3010, 3000...):
  * fleetms: here is an example of URL : http://Public IP:31300/fleetms/fleets
  * UI: http://Public IP:31010/
* Access the kubernetes console from your IKS deployment to see the deployment   


