#!/usr/bin/env bash
set -euo pipefail

semgrep_login_integration_test() {
	create_semgr8ns_namespace
	kubectl create secret generic -n semgr8ns --from-literal=token="${SEMGREP_APP_TOKEN}" semgrep-app-token
	create_test_namespaces
	update_with_file "semgrep_login"
	install "make"
	multi_test "semgrep_login"
	uninstall "make"
}
