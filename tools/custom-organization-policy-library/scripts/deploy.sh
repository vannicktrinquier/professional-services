#!/bin/bash

# Function to check if gcloud is installed
function check_gcloud() {
  if ! command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK (gcloud) is not installed."
    return 1
  fi
  return 0
}

# Function providing installation instructions
function install_gcloud() {
  echo "Installing the Google Cloud SDK..."
  echo "Please refer to the official installation instructions for your operating system:"
  echo "https://cloud.google.com/sdk/docs/install" 
  echo
  echo "The installation includes the gcloud command-line tool."
}

# Function to process a single file
function process_file() {
  local file="$1"
  local file="$2"

  if [[ ! $file == *.yaml && ! $file == *.yml ]]; then
     return
  fi

  echo "Processing file: $file"

  if [[ $action == "constraint" ]]; then
      gcloud org-policies set-custom-constraint $file       
  elif [[ $action == "policy" ]]; then
      gcloud org-policies set-policy $file --update-mask=*
  fi

}

# Recursive function to traverse the file structure 
function traverse_folder() {
  local action="$1"
  local current_dir="$2"

  for item in "$current_dir"/*; do
    if [[ -f "$item" ]]; then
      process_file "$action" "$item" 
    elif [[ -d "$item" ]]; then
      traverse_folder "$action" "$item" # Recursion for subfolders
    fi
  done
}

check_gcloud
gcloud_installed=$?

# Guide installation if necessary
if [[ $gcloud_installed -ne 0 ]]; then
  install_gcloud
fi

if [[ $# -lt 1 ]]; then
  echo "Error: Please provide an action parameter."
  echo "Usage: $0 [constraint | policy] [folder]"
  exit 1
fi

action=$1

# Assign the second parameter if provided, otherwise use a default
folder=${2:-"../samples"}

case $action in
  "constraint")
    echo "Provisioning constraints from folder $folder"
    traverse_folder "constraint" "$folder"
    ;;
  "policy")
    echo "Provisioning policies from folder $folder"
    traverse_folder "policy" "$folder"
    ;;
  *)
    echo "Invalid action. Valid options are: constraint, policies"
    exit 1
    ;;
esac