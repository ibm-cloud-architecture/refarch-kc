@ECHO OFF

:: Determine whether the target cluster is an OpenShift cluster
FOR /F "tokens=* USEBACKQ" %%F IN (`oc get clusterversion -o jsonpath^='{.items[].status.desired.version}'`) DO (
    SET OCPVERSION=%%F
)
IF NOT "%OCPVERSION%" == "" (
    echo Target is OpenShift version %OCPVERSION%
)