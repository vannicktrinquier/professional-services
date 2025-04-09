# Make will use bash instead of sh
SHELL 	:= /usr/bin/env bash
CONFIG_PREVENTIVE := -f build/preventive/config/schema.yaml -f build/preventive/config/services/ -f values_preventive.yaml -f build/ytt_lib/
CONFIG_DETECTIVE := -f build/detective/config/schema.yaml -f build/detective/config/services/ -f values_detective.yaml -f build/ytt_lib/
OUTPUT_GCLOUD 	:= samples/gcloud
OUTPUT_TF := samples/tf

YQ := $(shell command -v yq 2> /dev/null)
ifndef YQ
    $(error "yq is not installed or not in PATH. Please install yq: https://github.com/mikefarah/yq/#install")
endif

DETECTIVE_ORGANIZATION_ID := $(shell $(YQ) '.organization' values_detective.yaml)

.PHONY: constraints
constraints: 
	rm -rf $(OUTPUT_GCLOUD)/constraints
	ytt $(CONFIG_PREVENTIVE) -f build/preventive/custom-constraints/  --output-files $(OUTPUT_GCLOUD)/constraints

.PHONY: constraints-tf
constraints-tf: constraints
	python3 scripts/cvt-tf-constraints.py $(OUTPUT_GCLOUD)/constraints $(OUTPUT_TF)/custom-constraints

.PHONY: policies
policies: 
	rm -rf $(OUTPUT_GCLOUD)/policies
	ytt $(CONFIG_PREVENTIVE) -f build/preventive/org-policies/  --output-files $(OUTPUT_GCLOUD)/policies
	python3 scripts/format-policies.py $(OUTPUT_GCLOUD)/policies/policies.yaml $(OUTPUT_GCLOUD)/policies
	rm $(OUTPUT_GCLOUD)/policies/policies.yaml

.PHONY: policies-tf
policies-tf: policies
	python3 scripts/cvt-tf-policies.py $(OUTPUT_GCLOUD)/policies $(OUTPUT_TF)/custom-policies

.PHONY: sha
sha: 
	rm -rf $(OUTPUT_GCLOUD)/sha
	ytt $(CONFIG_DETECTIVE) -f build/detective/custom-sha/  --output-files $(OUTPUT_GCLOUD)/sha

.PHONY: build
build: clean constraints policies sha

.PHONY: build-tf
build-tf: clean constraints-tf policies-tf

.PHONY: all
all: clean build build-tf

.PHONY: simulate
simulate: clean constraints policies
	bash scripts/simulate.sh $(OUTPUT_GCLOUD)/constraints $(OUTPUT_GCLOUD)/policies $(OUTPUT_GCLOUD)/simulation

.PHONY: deploy-constraints
deploy-constraints:
	sh scripts/deploy.sh constraint $(OUTPUT_GCLOUD)/constraints

.PHONY: deploy-policies
deploy-policies:
	sh scripts/deploy.sh policy $(OUTPUT_GCLOUD)/policies

.PHONY: deploy-sha
deploy-sha:
	sh scripts/deploy.sh sha $(OUTPUT_GCLOUD)/sha --organization $(DETECTIVE_ORGANIZATION_ID)

.PHONY: deploy
deploy: deploy-constraints deploy-policies

.PHONY: config
config: 
	ytt $(CONFIG_PREVENTIVE) -f build/config/config.yaml

.PHONY: clean
clean: 
	rm -rf $(OUTPUT_GCLOUD)
	rm -rf $(OUTPUT_TF)


