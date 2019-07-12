
. ./icp-setenv.sh

echo ‘Logging onto IBM Cloud Private CLI $CLUSTER_NAME’
echo
cloudctl login -a https://$CLUSTER_NAME:8443 --skip-ssl-validation

echo ‘Logging onto Docker Registry’
echo
docker login $CLUSTER_NAME:8500

echo ‘Initializing Helm’
echo
helm init --client-only 
helm version --tls
