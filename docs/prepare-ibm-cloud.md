# Prepare IBM Cloud Services to run the solution

IBM Cloud offers a set of services to run part of your event driven architecture. We are using the following services:
* [Kubernetes Service](https://console.bluemix.net/containers-kubernetes/catalog/cluster)

## Pre-requisites

* Have access to IBM Cloud.
* Install the following CLIs:
    * [IBM Cloud CLI](https://cloud.ibm.com/docs/cli/reference/ibmcloud/download_cli.html#install_use)
    * IBM Cloud Kubernetes Service [plug-in](https://cloud.ibm.com/docs/cli/reference/ibmcloud/extend_cli.html#plug-ins)
    ```
    $ ibmcloud plugin install container-service -r Bluemix
    ```
    * [Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
    * IBM Cloud Container Registry plug-in

All our docker images for this solution are in public docker registry: dockerhub under ibmcase.

## Kubernetes cluster service

To create the cluster uses [this tutorial](https://console.bluemix.net/docs/containers/cs_tutorials.html#cs_cluster_tutorial).

Here is an image of our cluster, with 3 nodes and the smallest configuration:

![](./iks-cluster.png) 

To access to the cluster:
```
ibmcloud login -a https://api.us-east.bluemix.net
```

Set the KUBECONFIG environment variable.

To set the cluster config to your cluster use: `ibmcloud ks cluster-config <cluster_name_or_ID>`

Create a namespace: `kubectl create namespace browncompute`

Now each components, microservices or cloud functions, we are deploying as part of this solution will have its helm chart or scripts.
 