#!/bin/bash

export PLACEHOLDER_INTRO=$(cat src/pages/quickstart-tutorial/_fragment-introduction.mdx)
export PLACEHOLDER_OPENLABS=$(cat src/pages/quickstart-tutorial/_fragment-openlabs.mdx)
export PLACEHOLDER_PLAYGROUNDS=$(cat src/pages/quickstart-tutorial/_fragment-playgrounds.mdx)
export PLACEHOLDER_RUNTHEDEMO=$(cat src/pages/quickstart-tutorial/_fragment-run-the-demo.mdx)
export PLACEHOLDER_CLEANUP=$(cat src/pages/quickstart-tutorial/_fragment-cleanup.mdx)

TEMPLATE_FILE="src/pages/quickstart-tutorial/_deploy-on-ibm-openlabs-template.mdx"
OUTPUT_FILE="src/pages/quickstart-tutorial/deploy-on-ibm-openlabs.mdx"
TARGET_VARS='$PLACEHOLDER_INTRO:$PLACEHOLDER_OPENLABS:$PLACEHOLDER_RUNTHEDEMO:$PLACEHOLDER_CLEANUP'
envsubst "${TARGET_VARS}" < "$TEMPLATE_FILE" > "$OUTPUT_FILE"

TEMPLATE_FILE="src/pages/quickstart-tutorial/_deploy-on-openshift-playgrounds-template.mdx"
OUTPUT_FILE="src/pages/quickstart-tutorial/deploy-on-openshift-playgrounds.mdx"
TARGET_VARS='$PLACEHOLDER_INTRO:$PLACEHOLDER_PLAYGROUNDS:$PLACEHOLDER_RUNTHEDEMO:$PLACEHOLDER_CLEANUP'
envsubst "${TARGET_VARS}" < "$TEMPLATE_FILE" > "$OUTPUT_FILE"
