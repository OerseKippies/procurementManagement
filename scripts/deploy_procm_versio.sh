#!/usr/bin/env bash
# procM Versio deploy — git clone + PHP health stub (Flask needs Python 3.10+ on host)
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
REMOTE="${PROCM_VERSIO_SSH:-nol@vserver423.axc.eu}"
DOMAIN="procm.oerse-kippies.nl"
REPO_NAME="procurementManagement"
DOMAIN_DIR="~/domains/${DOMAIN}"
REPO_DIR="${DOMAIN_DIR}/${REPO_NAME}"

echo "Deploy procM to ${REMOTE}:${REPO_DIR}"

ssh "${REMOTE}" "mkdir -p ${DOMAIN_DIR}"

# Sync repo via git on server (preferred) or SCP fallback
if ssh "${REMOTE}" "test -d ${REPO_DIR}/.git"; then
  ssh "${REMOTE}" "cd ${REPO_DIR} && git fetch origin && git checkout main && git reset --hard origin/main"
else
  ssh "${REMOTE}" "git clone git@github.com:OerseKippies/${REPO_NAME}.git ${REPO_DIR}" || {
    echo "Git clone failed — using SCP from local ${ROOT}"
    ssh "${REMOTE}" "mkdir -p ${REPO_DIR}"
    scp -r "${ROOT}/procm" "${ROOT}/templates" "${ROOT}/static" "${ROOT}/deployment" \
      "${ROOT}/requirements.txt" "${ROOT}/run.py" "${ROOT}/README.md" \
      "${REMOTE}:${REPO_DIR}/"
  }
fi

COMMIT="$(cd "${ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
ssh "${REMOTE}" "echo '${COMMIT}' > ${REPO_DIR}/DEPLOY_COMMIT.txt"

ssh "${REMOTE}" "rm -rf ${DOMAIN_DIR}/public_html && mkdir -p ${DOMAIN_DIR}/public_html"
scp "${ROOT}/deployment/public_html/index.php" "${REMOTE}:${DOMAIN_DIR}/public_html/"
ssh "${REMOTE}" "chmod 755 ${DOMAIN_DIR}/public_html && chmod 644 ${DOMAIN_DIR}/public_html/index.php"

echo "Deploy complete. Health: https://${DOMAIN}/ (if DNS/subdomain configured)"
echo "Commit: ${COMMIT}"
