#!/usr/bin/env bash
set -euo pipefail

rules_integration_test() {
	create_test_namespaces
	update_with_file "basic"
	install "make"
	multi_test "remote_rules"
	uninstall "make"
}
