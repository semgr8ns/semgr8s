#!/usr/bin/env bash
set -euo pipefail

declare -A DEPLOYMENT_RES=(["VALID"]="0" ["INVALID"]="0")
SCRIPT_PATH=$(tmp=$(realpath "$0") && dirname "${tmp}")
RED="\033[0;31m"
GREEN="\033[0;32m"
NC="\033[0m"
SUCCESS="${GREEN}SUCCESS${NC}"
FAILED="${RED}FAILED${NC}"
EXIT="0"
RETRY=3

# install/uninstall/upgrade, utility stuff
source ${SCRIPT_PATH}/scripts/common.sh

# integration test specific functions
source ${SCRIPT_PATH}/scripts/basic.sh
source ${SCRIPT_PATH}/scripts/remote_rules.sh
source ${SCRIPT_PATH}/scripts/autofix.sh

# backup values.yaml
cp charts/semgr8s/values.yaml charts/semgr8s/values.yaml.bak

case $1 in
"basic")
	# testing basic functionality
	basic_integration_test
	;;
"remote_rules")
	# testing multiple pre-built rules
	rules_integration_test
	;;
"autofix")
	# testing autofixing with mutating webhook
	autofix_integration_test
	;;
"restore")
	restore
	;;
*)
	echo "Unknown test type: $1"
	EXIT="1"
	;;
esac

if [[ "${EXIT}" != "0" ]]; then
	echo -e "${FAILED} Failed integration test."
else
	echo -e "${SUCCESS} Passed integration test."
fi

if [[ "${CI-}" == "true" ]]; then
	exit $((${EXIT}))
fi

echo 'Cleaning up ...'
restore
make uninstall >/dev/null 2>&1 || true
kubectl delete all,cronjobs,daemonsets,jobs,replicationcontrollers,statefulsets,namespaces -luse="semgr8s-integration-test" -A >/dev/null
