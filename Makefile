webhookName := semgr8s
image       :=  $(shell yq e '.deployment.image.repository' helm/values.yaml)
version     := $(shell yq e '.appVersion' helm/Chart.yaml)
tag         := $(image):$(version)

ns          := semgr8ns

all: delete install

build:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker build --platform=linux/amd64 -t $(tag) -f docker/Dockerfile .

delete:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	helm uninstall semgr8s -n $(ns)

install:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	helm install semgr8s helm --create-namespace --namespace $(ns)

.PHONY: test clean helm annihilate

test:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	-kubectl create -f tests/
	@echo
	-kubectl get pods -n test-case-excl
	-kubectl get pods -n test-case-incl
	@echo
	-kubectl delete -f tests/
