PYTHON3 := $(shell which python3)
DEV_REQUIREMENTS := pytest black
DOCKER_IMAGE := "registry.digitalocean.com/johncunniff/petal-test"

help:
	@echo 'For convenience'
	@echo
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: debug              # Debug application (run app.py locally on port 5000)
debug: venv
	venv/bin/python3 app.py

.PHONY: build-docker       # Build docker image
build-docker:
	docker build -t $(DOCKER_IMAGE) .

.PHONY: debug-docker       # Debug docker image by running it locally
debug-docker: build-docker
	docker run -it --rm -p '5000:5000' $(DOCKER_IMAGE)

.PHONY: debug-docker       # Debug docker image by running it locally
push-docker: build-docker
	docker push $(DOCKER_IMAGE)

.PHONY: lint               # Lint app.py with black
lint: venv
	venv/bin/black app.py test_app.py

.PHONY: requirements.txt   # pip-compile requirements.txt dependencies
requirements.txt: requirements.in
	pip-compile requirements.in > requirements.txt

.PHONY: venv               # Generate a virtual environment for local debugging
venv:
	if [ ! -d venv ]; then \
		virtualenv -p $(PYTHON3) venv; \
		venv/bin/pip install -r requirements.txt; \
		venv/bin/pip install $(DEV_REQUIREMENTS); \
	fi

.PHONY: venv               # Provision the initial cluster with traefik and metric-server
provision-k8s:
	helm repo add traefik 'https://helm.traefik.io/traefik'
	helm upgrade \
		--install traefik traefik/traefik \
		--create-namespace \
		--values traefik-values.yaml \
		--version '9.19.1' \
		--namespace traefik
# Install k8s metrics server (necessary for hpas)
	kubectl apply -f "https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
	kubectl apply -f k8s-deployment.yaml

.PHONY: clean              # Clean local debug environment of artifacts
clean:
	rm -rf venv .pytest_cache
	rm -rf $(shell find . -name '__pycache__' -o -name '*.pyc')
