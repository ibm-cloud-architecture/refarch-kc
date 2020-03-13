::ECHO OFF
SET SCRIPT_DIR=%~dp0

cd %SCRIPT_DIR%\..\..
git clone https://github.com/ibm-cloud-architecture/refarch-kc-ui
git clone https://github.com/ibm-cloud-architecture/refarch-kc-ms
git clone https://github.com/ibm-cloud-architecture/refarch-kc-streams
git clone https://github.com/ibm-cloud-architecture/refarch-reefer-ml
git clone https://github.com/ibm-cloud-architecture/refarch-kc-order-ms
git clone https://github.com/ibm-cloud-architecture/refarch-kc-container-ms
