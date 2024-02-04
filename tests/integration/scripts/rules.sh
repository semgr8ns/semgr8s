#!/usr/bin/env bash
set -euo pipefail

rules_integration_test() {
	create_namespaces
	update_with_file "basic"
	install "make"
	multi_test "rules"
	uninstall "make"
}
