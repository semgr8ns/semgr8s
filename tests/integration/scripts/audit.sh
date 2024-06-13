#!/usr/bin/env bash
set -euo pipefail

audit_integration_test() {
	create_test_namespaces
	update_with_file "audit"
	install "make"
	multi_test "audit"
	uninstall "make"
}
