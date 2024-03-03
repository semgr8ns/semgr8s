#!/usr/bin/env bash
set -euo pipefail

## UTILS ------------------------------------------------------- ##
fail() {
	echo -e "${FAILED}"
	exit 1
}

success() {
	echo -e "${SUCCESS}"
}

restore() {
	cp charts/semgr8s/values.yaml.bak charts/semgr8s/values.yaml
	rm charts/semgr8s/values.yaml.bak
}

null_to_empty() {
	read in

	if [[ "$in" == "null" ]]; then
		echo ""
	else
		echo "$in"
	fi
}

## INSTALLATIONS ---------------------------------------------- ##
install() { # $1: helm or make, $2: namespace (helm), $3: additional args (helm)
	echo -n 'Installing semgr8s ... '
	case $1 in
	"helm")
		helm install semgr8s charts/semgr8s --atomic --namespace "${2}" \
			${3} >/dev/null || fail
		sleep 1
		;;
	"make")
		make install >/dev/null || fail
		sleep 1
		;;
	*)
		fail
		;;
	esac
	success
}

uninstall() { # $1: helm or make, $2: namespace (helm)
	echo -n 'Uninstalling semgr8s ...'
	case $1 in
	"helm")
		helm uninstall semgr8s --namespace "${2}" >/dev/null || fail
		;;
	"make")
		make uninstall >/dev/null || fail
		;;
	"force")
		kubectl delete all,secrets,serviceaccounts,mutatingwebhookconfigurations,configmaps,namespaces \
			-lapp.kubernetes.io/instance=semgr8s -A --force --grace-period=0 >/dev/null 2>&1
		;;
	*)
		fail
		;;
	esac
	success
}

upgrade() { # $1: helm or make, $2: namespace (helm)
	echo -n 'Upgrading semgr8s ...'
	case $1 in
	"helm")
		helm upgrade semgr8s charts/semgr8s --wait \
			--namespace "${2}" >/dev/null || fail
		;;
	"make")
		make upgrade >/dev/null || fail
		;;
	*)
		fail
		;;
	esac
	success
}

## UPDATES ----------------------------------------------------- ##

update() { # $@: update expressions
	for update in "$@"; do
		yq e -i "${update}" charts/semgr8s/values.yaml
	done
}

update_with_file() { # $1: file name
	envsubst <tests/integration/test_cases/$1.yaml >$1
	yq eval-all --inplace 'select(fileIndex == 0) * select(fileIndex == 1).values' charts/semgr8s/values.yaml $1
	rm $1
}

## RULES ------------------------------------------------------- ##

add_rule() { # $1: rule name
	cp tests/integration/rules/$1.yaml charts/semgr8s/rules/
}

add_test_rules() {
	cp tests/integration/rules/* charts/semgr8s/rules/
}

## TEST NAMESPACES --------------------------------------------- ##

create_namespaces() {
	echo -n "Creating test namespaces..."
	kubectl apply -f tests/integration/data/00_namespaces.yaml >/dev/null
	success
}

## TESTS ------------------------------------------------------- ##
single_test() { # ID TXT TYP REF NS MSG RES
	echo -n "[$1] $2"
	i=0                                                              # intialize iterator
	export RAND=$(head -c 5 /dev/urandom | hexdump -ve '1/1 "%.2x"') # creating a random index to label the pods and avoid name collision for repeated runs

	if [[ "$6" == "" ]]; then
		MSG="pod/pod-$1-${RAND} created"
	else
		MSG=$(envsubst <<<"$6") # in case RAND is to be used, it needs to be added as ${RAND} to cases.yaml (and maybe deployment file)
	fi

	while :; do
		i=$((i + 1))
		if [[ "$3" == "deploy" ]]; then
			kubectl run pod-$1-${RAND} --image="$4" --namespace="$5" -luse="semgr8s-integration-test" >output.log 2>&1 || true
		else
			kubectl apply -f "${SCRIPT_PATH}/data/$4.yaml" --namespace="$5" >output.log 2>&1 || true
		fi
		# if the webhook couldn't be called, try again.
		[[ ("$(cat output.log)" =~ "failed calling webhook") && $i -lt ${RETRY} ]] || break
	done
	if [[ ! "$(cat output.log)" =~ "${MSG}" ]]; then
		echo -e ${FAILED}
		echo "::group::Output"
		cat output.log
		kubectl logs -n semgr8ns -lapp.kubernetes.io/instance=semgr8s
		echo "::endgroup::"
		EXIT="1"
	else
		echo -e "${SUCCESS}"
	fi
	rm output.log

	if [[ "$7" != "null" ]]; then
		DEPLOYMENT_RES[$7]=$((${DEPLOYMENT_RES[$7]} + 1))
	fi

	# 3 tries on first test, 2 tries on second, 1 try for all subsequential
	RETRY=$((RETRY - 1))
}

multi_test() { # $1: file name, $2: key to find the testcases (default: testCases)

	# converting to json, as yq processing is pretty slow
	test_cases=$(yq e -o=json ".${2:-testCases}" ${SCRIPT_PATH}/test_cases/$1.yaml)
	len=$(echo ${test_cases} | jq 'length')
	for i in $(seq 0 $(($len - 1))); do
		test_case=$(echo ${test_cases} | jq ".[$i]")
		ID=$(echo ${test_case} | jq -r ".id" | null_to_empty)
		TEST_CASE_TXT=$(echo ${test_case} | jq -r ".txt" | null_to_empty)
		TYPE=$(echo ${test_case} | jq -r ".type" | null_to_empty)
		REF=$(echo ${test_case} | jq -r ".ref" | null_to_empty)
		NAMESPACE=$(echo ${test_case} | jq -r ".namespace" | null_to_empty)
		EXP_MSG=$(echo ${test_case} | jq -r ".expected_msg" | null_to_empty)
		EXP_RES=$(echo ${test_case} | jq -r ".expected_result" | null_to_empty)
		single_test "${ID}" "${TEST_CASE_TXT}" "${TYPE:=deploy}" "${REF}" "${NAMESPACE:=default}" "${EXP_MSG}" "${EXP_RES:=null}"
	done
}
