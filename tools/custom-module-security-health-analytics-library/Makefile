SHELL 	:= /usr/bin/env bash

INPUT_VALUES    := $(or $(CUSTOM_SHA_INPUT_VALUES), values.yaml)
OUTPUT_GCLOUD   := $(or $(CUSTOM_SHA_OUTPUT_GCLOUD), samples/gcloud)
OUTPUT_TF       := $(or $(CUSTOM_SHA_OUTPUT_TF), samples/tf)

CONFIG := -f build/config/schema.yaml -f build/config/services/ -f $(INPUT_VALUES) -f build/ytt_lib/

# By default, generating all services 
# For testing, can be set SERVICE := "cloudsql"
# SERVICE := "cloudkms"

CUSTOM_SHA_BASE_DIR := build/custom-sha/
CUSTOM_SHA_DIR := $(CUSTOM_SHA_BASE_DIR)

ifneq ($(strip $(SERVICE)),"")
  CUSTOM_SHA_DIR := $(CUSTOM_SHA_BASE_DIR)$(SERVICE)
endif


YQ := $(shell command -v yq 2> /dev/null)
ifndef YQ
    $(error "yq is not installed or not in PATH. Please install yq: https://github.com/mikefarah/yq/#install")
endif

DEPLOYMENT_PARENT := $(shell $(YQ) '.deployment.parent' ${INPUT_VALUES})
PARENT_TYPE := $(shell echo $(DEPLOYMENT_PARENT) | cut -d'/' -f1)
PARENT_ID := $(shell echo $(DEPLOYMENT_PARENT) | cut -d'/' -f2)

PARENT_FLAG := $(shell if [ "$(PARENT_TYPE)" = "organizations" ]; then echo "--organization"; elif [ "$(PARENT_TYPE)" = "folders" ]; then echo "--folder"; elif [ "$(PARENT_TYPE)" = "projects" ]; then echo "--project"; fi)

.PHONY: sha
sha: 
	rm -rf $(OUTPUT_GCLOUD)
	ytt $(CONFIG) -f $(CUSTOM_SHA_DIR) --output-files $(OUTPUT_GCLOUD)

.PHONY: sha-tf
sha-tf: sha
	python3 scripts/cvt-tf-custom-sha-modules.py $(OUTPUT_GCLOUD) $(OUTPUT_TF)

.PHONY: build
build: clean sha

.PHONY: build-tf
build-tf: clean sha-tf

.PHONY: all
all: clean build build-tf

.PHONY: deploy-sha
deploy-sha:
	bash scripts/deploy.sh sha $(OUTPUT_GCLOUD) $(PARENT_FLAG) $(PARENT_ID)

.PHONY: deploy
deploy: build deploy-sha

.PHONY: clean
clean: 
	rm -rf $(OUTPUT_GCLOUD)
	rm -rf $(OUTPUT_TF)


