webhookName := semgr8s
image       :=  $(shell yq e '.deployment.image.repository' charts/semgr8s/values.yaml)
version     := $(shell yq e '.appVersion' charts/semgr8s/Chart.yaml)
tag         := $(image):v$(version)

ns          := semgr8ns

all: uninstall install

.PHONY:build
build:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker buildx build --platform=linux/amd64 -t $(tag) -f build/Dockerfile .

.PHONY:build-tester
build-tester:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker buildx build --platform=linux/amd64 --target tester -t $(tag)-tester -f build/Dockerfile .

.PHONY:push
push:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker push $(tag)

.PHONY:install
install:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	helm install semgr8s charts/semgr8s --atomic --create-namespace --namespace $(ns)

.PHONY:uninstall
uninstall:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	helm uninstall semgr8s -n $(ns)

.PHONY:annihilate
annihilate:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	helm uninstall semgr8s -n $(ns)
	kubectl delete ns $(ns)

.PHONY: test
test:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	-kubectl create -f tests/demo
	@echo
	-kubectl get pods -n test-semgr8s
	@echo
	-kubectl delete -f tests/demo

.PHONY: unittest
unittest:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker run --rm -t -v ${PWD}/tests/:/app/tests/ $(tag)-tester pytest --cov=semgr8s --cov-report term-missing tests/
