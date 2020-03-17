@ECHO OFF
SET SCRIPTLOC=%~dp0

call %SCRIPTLOC%\uninstall-app.bat

:: Uninstall Postgres Helm chart
helm uninstall postgresql -n postgres

:: TODO - is this required outside of OpenShift?
kubectl delete serviceaccount -n postgres pgserviceaccount

:: Delete Postgres namespace
kubectl delete ns postgres

:: Delete Kafka cluster
kubectl delete -f %SCRIPTLOC%\kafka-strimzi.yml -n kafka

:: Uninstall Strimzi Helm chart
helm uninstall strimzi -n strimzi

:: Remove Strimzi and Kafka namespaces
kubectl delete ns strimzi
kubectl delete ns kafka
