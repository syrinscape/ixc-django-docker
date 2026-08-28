#!/bin/bash

set -e

REPOSITORY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ixc-pip-install-test.XXXXXX")"
BIN_DIR="$TEST_DIR/bin"
PROJECT_DIR="$TEST_DIR/project"
COMMAND_LOG="$TEST_DIR/commands.log"

trap 'rm -rf "$TEST_DIR"' EXIT

mkdir -p "$BIN_DIR" "$PROJECT_DIR"
touch "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/requirements-local.txt"

cat > "$BIN_DIR/python3.5" <<'EOF'
#!/bin/bash

printf '%s\n' "$*" >> "$COMMAND_LOG"
EOF

cat > "$BIN_DIR/pip" <<'EOF'
#!/bin/bash

echo "pip must be selected through the configured Python runtime" >&2
exit 1
EOF

chmod +x "$BIN_DIR/python3.5" "$BIN_DIR/pip"

COMMAND_LOG="$COMMAND_LOG" \
PATH="$BIN_DIR:$PATH" \
PYTHON_VERSION=python3.5 \
	bash "$REPOSITORY_DIR/ixc_django_docker/bin/pip-install.sh" "$PROJECT_DIR"

diff -u <(printf '%s\n' \
	'-m pip install -r requirements.txt' \
	'-m pip install -r requirements-local.txt') "$COMMAND_LOG"

echo "pip-install.sh runtime selection test passed"
