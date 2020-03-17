@ECHO OFF
SET SCRIPTLOC=%~dp0
echo Running from: %SCRIPTLOC%
SET REPOBASE=%SCRIPTLOC%\..\..\..
echo Other repos should be at: %REPOBASE%
echo One is:
dir %REPOBASE%\refarch-kc-order-ms

IF NOT EXIST %REPOBASE%\refarch-kc-order-ms GOTO clone
GOTO install

:clone
call %SCRIPTLOC%\..\clone.bat

:install
:: Create namespace for refarch-kc microservices
kubectl create ns shipping

:: TODO - is this required outside of OpenShift?
kubectl create serviceaccount -n shipping kcserviceaccount

:: Configure secrets to allow microservices to connect to Postgres
kubectl create secret generic postgresql-url --from-literal=binding="jdbc:postgresql://postgresql.postgres.svc:5432/postgres" -n shipping
kubectl create secret generic postgresql-user --from-literal=binding="postgres" -n shipping
kubectl create secret generic postgresql-pwd --from-literal=binding="supersecret" -n shipping

:: Create a configmap to allow microservices to find Kafka
:: This uses port 9092 (without TLS)
kubectl create configmap kafka-brokers --from-literal=brokers="my-cluster-kafka-bootstrap.kafka.svc:9092" -n shipping

:: Create configmap to configure microservices with topic names
kubectl apply -f %SCRIPTLOC%\kafka-topics-configmap.yaml -n shipping

:: Create Kafka topics using Strimzi CRs
kubectl apply -f %SCRIPTLOC%\topics.yaml -n kafka

:: TODO - make sure other repos are cloned

:: Install order-command-ms using pre-built image
:: note: --set eventstreams.enabled=false and --set eventstreams.truststoreRequired=false 
:: for connecting to Kafka rather than Event Streams
helm install order-command-ms %REPOBASE%\refarch-kc-order-ms/order-command-ms/chart/ordercommandms -n shipping --set image.repository=ibmcase/kcontainer-order-command-ms --set eventstreams.enabled=false --set eventstreams.truststoreRequired=false --set serviceAccountName=kcserviceaccount

:: Install order-query-ms using pre-built image
helm install order-query-ms %REPOBASE%\refarch-kc-order-ms/order-query-ms/chart/orderqueryms -n shipping --set image.repository=ibmcase/kcontainer-order-query-ms --set eventstreams.enabled=false --set eventstreams.truststoreRequired=false --set serviceAccountName=kcserviceaccount

:: Install spring-container-ms using pre-built image
:: note: uses postgres secrets defined above
helm install spring-container-ms %REPOBASE%\refarch-kc-container-ms/SpringContainerMS/chart/springcontainerms -n shipping --set image.repository=ibmcase/kcontainer-spring-container-ms --set eventstreams.enabled=false --set eventstreams.truststoreRequired=false --set serviceAccountName=kcserviceaccount

:: Install voyages-ms using pre-built image
helm install voyages-ms %REPOBASE%\refarch-kc-ms/voyages-ms/chart/voyagesms --set image.repository=ibmcase/kcontainer-voyages-ms -n shipping --set eventstreams.enabled=false --set serviceAccountName=kcserviceaccount

:: Install fleet-ms
helm install fleet-ms %REPOBASE%\refarch-kc-ms/fleet-ms/chart/fleetms --set image.repository=ibmcase/kcontainer-fleet-ms -n shipping --set eventstreams.enabled=false --set eventstreams.truststoreRequired=false --set serviceAccountName=kcserviceaccount

:: Install kc-ui
helm install kc-ui %REPOBASE%\refarch-kc-ui/chart/kc-ui --set image.repository=ibmcase/kcontainer-ui -n shipping --set eventstreams.enabled=false --set serviceAccountName=kcserviceaccount

:: Wait for all services to start
kubectl rollout status -n shipping deployment springcontainerms-deployment
kubectl rollout status -n shipping deployment fleetms-deployment
kubectl rollout status -n shipping deployment kc-ui-deployment
kubectl rollout status -n shipping deployment ordercommandms-deployment
kubectl rollout status -n shipping deployment orderqueryms-deployment
kubectl rollout status -n shipping deployment voyagesms-deployment

:: call %SCRIPTLOC%\postinstall.bat
