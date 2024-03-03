#!/usr/bin/env bash
set -euo pipefail

autofix_integration_test() {
	add_rule "test-semgr8s-no-foobar-label"
	create_namespaces
	update_with_file "autofix"
	install "make"
	multi_test "autofix"
	uninstall "make"
}
