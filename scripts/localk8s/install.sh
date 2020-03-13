#!/bin/bash
SCRIPTLOC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$SCRIPTLOC/install-infra.sh
$SCRIPTLOC/install-app.sh
$SCRIPTLOC/run-integration-tests.sh
