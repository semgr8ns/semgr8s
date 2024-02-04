#!/usr/bin/env bash
set -euo pipefail

basic_integration_test() {
	create_namespaces
	update_with_file "basic"
	install "make"
	multi_test "basic"
	uninstall "make"
}
