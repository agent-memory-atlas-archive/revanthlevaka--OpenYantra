#!/usr/bin/env bash
# Run once as the repo owner: gh auth login && ./apply-rules.sh
set -e
gh api -X POST repos/revanthlevaka/OpenYantra/rulesets --input .github/rulesets/protect-main.json
echo "Done. Also check: Settings > Collaborators - give others Read/Triage only, never Write."
