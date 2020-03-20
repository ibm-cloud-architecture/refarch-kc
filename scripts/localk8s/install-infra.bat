@ECHO OFF
SET SCRIPTLOC=%~dp0

CALL %SCRIPTLOC%\ocpversion.bat

:: Create namespaces for Strimzi and Kafka
kubectl create ns strimzi
kubectl create ns kafka

:: Install Strimzi Helm chart
helm repo add strimzi https://strimzi.io/charts
helm install strimzi strimzi/strimzi-kafka-operator -n strimzi --set watchNamespaces={kafka} --wait --timeout 300s

:: Install Strimzi custom resource to create cluster
kubectl apply -f %SCRIPTLOC%\kafka-strimzi.yml -n kafka

:: Create namespace for Postgres
kubectl create ns postgres

:: Create a service account for the postgres container to use
kubectl create serviceaccount -n postgres pgserviceaccount
:: Postgres requires root permissions which must be explicitly granted on OpenShift
IF NOT "%OCPVERSION%" == "" (
    oc adm policy add-scc-to-user anyuid -z pgserviceaccount -n postgres
)

:: Install Postgres Helm chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql -n postgres --wait --timeout=300s --set postgresqlPassword=supersecret --set persistence.enabled=false --set serviceAccount.enabled=true --set serviceAccount.name=pgserviceaccount

:: Wait for cluster to be ready before continuing
kubectl wait --for=condition=Ready kafkas/my-cluster -n kafka --timeout 180s
