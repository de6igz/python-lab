#!/usr/bin/env bash
# A dedicated destination directory is required; never put private files there.
set -euo pipefail
source_dir=${1:?Usage: deploy.sh SOURCE_DIR}
: "${SSH_HOST:?}" "${SSH_USER:?}" "${REMOTE_DIR:?}" "${DEPLOY_KEY:?}" "${KNOWN_HOSTS:?}" "${SITE_URL:?}"
SSH_PORT=${SSH_PORT:-22}
[[ "$SSH_HOST" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*$ ]] || exit 2
[[ "$SSH_USER" =~ ^[A-Za-z0-9_][A-Za-z0-9_-]*$ ]] || exit 2
[[ "$SSH_PORT" =~ ^[0-9]+$ ]] || exit 2
# A restricted rrsync key uses '.' relative to its server-side directory.
[[ "$REMOTE_DIR" == . || ( "$REMOTE_DIR" =~ ^/[A-Za-z0-9_./-]+$ && "$REMOTE_DIR" != / && "$REMOTE_DIR" != *..* ) ]] || exit 2
[[ -f "$source_dir/index.html" ]] || { echo 'missing index.html'; exit 2; }
# mktemp uses the task-owned working directory; secrets are removed even on failure.
mkdir -p .work
key_dir=$(mktemp -d .work/deploy.XXXXXX)
trap 'rm -rf "$key_dir"' EXIT
chmod 700 "$key_dir"
printf '%s\n' "$DEPLOY_KEY" > "$key_dir/key"
printf '%s\n' "$KNOWN_HOSTS" > "$key_dir/known_hosts"
chmod 600 "$key_dir/key" "$key_dir/known_hosts"
unset DEPLOY_KEY KNOWN_HOSTS
export RSYNC_RSH="ssh -i $key_dir/key -p $SSH_PORT -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$key_dir/known_hosts"
# --delay-updates reduces mixed-version exposure but is NOT an atomic site switch.
# No --delete: the script must not erase existing user files on the server.
rsync -az --delay-updates "$source_dir/" "$SSH_USER@$SSH_HOST:$REMOTE_DIR/"
python3 scripts/healthcheck.py "$SITE_URL"
