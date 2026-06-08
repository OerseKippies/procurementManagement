#!/usr/bin/env bash
# procM Versio deploy — git pull + public_html symlink (same pattern as invM/mdM)
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
REMOTE="${PROCM_VERSIO_SSH:-nol@vserver423.axc.eu}"
DOMAIN="procm.oerse-kippies.nl"
REPO_NAME="procurementManagement"
DOMAIN_DIR="~/domains/${DOMAIN}"
REPO_DIR="${DOMAIN_DIR}/${REPO_NAME}"

echo "Deploy procM to ${REMOTE}:${REPO_DIR}"

ssh "${REMOTE}" "mkdir -p ${DOMAIN_DIR}"
if ssh "${REMOTE}" "test -d ${REPO_DIR}/.git"; then
  ssh "${REMOTE}" "cd ${REPO_DIR} && git fetch origin && git checkout main && git reset --hard origin/main"
else
  ssh "${REMOTE}" "git clone git@github.com:OerseKippies/${REPO_NAME}.git ${REPO_DIR}"
fi

COMMIT="$(cd "${ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
ssh "${REMOTE}" "echo '${COMMIT}' > ${REPO_DIR}/DEPLOY_COMMIT.txt"

ssh "${REMOTE}" "rm -f ${DOMAIN_DIR}/public_html && ln -sfn ${REPO_DIR}/public/api ${DOMAIN_DIR}/public_html"

if ssh "${REMOTE}" "test -f ${REPO_DIR}/config/config.php"; then
  ssh "${REMOTE}" "php ${REPO_DIR}/scripts/migrate.php" || echo "WARN: migrate failed — check config.php credentials"
else
  echo "NOTE: config/config.php not on server — copy from config.example.php and set password, then re-run migrate"
fi

echo "Deploy complete: https://${DOMAIN}/health"
echo "Commit: ${COMMIT}"
