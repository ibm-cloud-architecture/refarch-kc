#!/bin/bash

if [[ $(pwd) = */iks ]]; then
 cd ../..
fi

source ./scripts/setenv.sh IBMCLOUD 

function logger() {
  echo "$(date +'%F %H:%M:%S') $@"
}




echo "export KUBECONFIG=$HOME/.bluemix/plugins/container-service/clusters/$IKS_CLUSTER_NAME/kube-config-$IKS_ZONES-$IKS_CLUSTER_NAME.yml   "
export KUBECONFIG=$HOME/.bluemix/plugins/container-service/clusters/$IKS_CLUSTER_NAME/kube-config-$IKS_ZONES-$IKS_CLUSTER_NAME.yml 
echo $KUBECONFIG

logger ibmcloud login
ibmcloud login -u $IBMCLOUD_USER -p $IBMCLOUD_PWD -c $IBMCLOUD_ACCOUNT -r $IKS_REGION

logger ibmcloud cr login
ibmcloud cr login

logger ibmcloud ks region-set $IKS_REGION
ibmcloud ks region-set $IKS_REGION 

logger ibmcloud ks cluster-config $IKS_CLUSTER_NAME
ibmcloud ks cluster-config --cluster $IKS_CLUSTER_NAME

logger Verify iks nodes....
kubectl get nodes

logger get exposed services $KC_NAMESPACE
kubectl get svc -n $KC_NAMESPACE