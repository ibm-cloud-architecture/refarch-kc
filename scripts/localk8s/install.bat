@ECHO OFF
SET SCRIPTLOC=%~dp0

call %SCRIPTLOC%\install-infra.bat
call %SCRIPTLOC%\install-app.bat
call %SCRIPTLOC%\run-integration-tests.bat
