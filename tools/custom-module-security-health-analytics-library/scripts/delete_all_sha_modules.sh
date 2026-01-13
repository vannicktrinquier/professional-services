#!/bin/bash

# This script deletes all descendant custom Security Health Analytics (SHA)
# modules under a specified GCP Organization.

# --- Configuration ---
# ⚠️ IMPORTANT: Replace '123' with your actual GCP Organization ID.
ORGANIZATION_ID="262782368104"

# Exit immediately if a command exits with a non-zero status.
set -e
set -o pipefail

# --- Main Script Logic ---

echo "🔹 Fetching all descendant custom SHA modules for organization '$ORGANIZATION_ID'..."

# Retrieve the full resource name of every custom module.
# The `jq -r '.[].name'` command filters the JSON output to get only the 'name'
# field for each module.
MODULES_TO_DELETE=$(gcloud scc manage custom-modules sha list-descendant \
  --organization="organizations/$ORGANIZATION_ID" \
  --format="json" | jq -r '.[].name')

# Check if any modules were found.
if [ -z "$MODULES_TO_DELETE" ]; then
  echo "✅ No custom SHA modules found to delete. Exiting."
  exit 0
fi

echo "🔍 The following custom modules will be deleted:"
echo "--------------------------------------------------"
echo "$MODULES_TO_DELETE"
echo "--------------------------------------------------"
echo ""

# Ask for user confirmation before proceeding.
read -p "Are you absolutely sure you want to delete all these modules? This action cannot be undone. (y/n) " -n 1 -r
echo # Move to a new line

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deletion cancelled by user."
    exit 1
fi

echo ""
echo "🔥 Starting deletion process..."

# Loop through each module's full resource name and execute the delete command.
# The `delete` command accepts the full resource name directly.
# The `--quiet` flag suppresses the interactive "Do you want to continue?" prompt for each deletion.
for module_name in $MODULES_TO_DELETE; do
  echo "   - Deleting module: $module_name"
  gcloud scc manage custom-modules sha delete "$module_name" --quiet
  echo "   ✔ Successfully deleted."
done

echo ""
echo "🎉 All identified custom SHA modules have been deleted."