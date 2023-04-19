webhookName := semgr8s
image       := xoph/$(webhookName)
version     := 0.1
tag         := $(image):$(version)

ns          := semgr8ns

all: delete clean certgen yamlgen redeploy

build:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	docker build --platform=linux/amd64 -t $(tag) . && docker push $(tag)

delete:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	-kubectl delete -f manifests/

redeploy: build deploy

deploy: yamlgen
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	-kubectl create -f manifests/
	@echo
	kubectl get validatingwebhookconfigurations.admissionregistration.k8s.io
	kubectl get pods -n $(ns)
	kubectl get secret -n $(ns)
	kubectl get svc -n $(ns)

.PHONY: test clean

clean:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	-rm -f conf/ext.cnf
	-rm -f certs/ca.* 
	-rm -f manifests/*.yaml

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

certgen:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	@sed -e "s/__NAMESPACE__/$(ns)/g" -e "s/__VERSION__/$(version)/g" -e "s/__WEBHOOK__/$(webhookName)/g" templates/ext.tpl >conf/ext.cnf
	openssl req -x509 -newkey rsa:4096 -nodes -out certs/ca.crt -keyout certs/ca.key -days 365 -config conf/ext.cnf -extensions req_ext
	ls -l certs/

yamlgen:
	@echo "####################"
	@echo "## $(@)"
	@echo "####################"
	@sed -e "s/__KEY__/$(shell cat certs/ca.key | base64 | tr -d '\n')/g" -e "s/__CRT__/$(shell cat certs/ca.crt | base64 | tr -d '\n')/g" -e "s/__WEBHOOK__/$(webhookName)/g" -e "s/__NAMESPACE__/$(ns)/g" -e "s|__TAG__|$(tag)|g" templates/secret.tpl >manifests/secret.yaml
	@sed -e "s/__NAMESPACE__/$(ns)/g" -e "s|__TAG__|$(tag)|g" -e "s/__WEBHOOK__/$(webhookName)/g" templates/k8s.tpl >manifests/k8s.yaml
	@sed -e "s/__NAMESPACE__/$(ns)/g" -e "s/__WEBHOOK__/$(webhookName)/g" -e "s/__CA_BUNDLE__/$(shell cat certs/ca.crt | base64 | tr -d '\n')/g" templates/webhook.tpl >manifests/webhook.yaml
	ls -l manifests/
