#!/bin/bash
# Session initialization script for AI_Agents workspace
# This script sets up the runbook toolkit environment

export RUNBOOK_TOOLKIT_REQUIRED=true
export RUNBOOK_TOOLKIT_PATH="/home/user/AI_Agents/runbook_toolkit"
export RUNBOOK_ARTIFACTS_DIR="/tmp/artifacts"
export RUNBOOK_ENFORCEMENT_MODE=strict

echo "🛡️ Runbook Toolkit Environment Initialized"
echo "Toolkit location: $RUNBOOK_TOOLKIT_PATH"
echo "Artifacts directory: $RUNBOOK_ARTIFACTS_DIR"
echo "Enforcement mode: $RUNBOOK_ENFORCEMENT_MODE"
