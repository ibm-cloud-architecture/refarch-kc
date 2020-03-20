#!/bin/bash

# Determine whether the target cluster is an OpenShift cluster
OCPVERSION=`oc get clusterversion -o jsonpath='{.items[].status.desired.version}'`
if [ ! -z "$OCPVERSION" ]; then
    echo "Target is OpenShift version $OCPVERSION"
fi