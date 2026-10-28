#!/bin/sh
# One-time setup for any clone:
#   1. activate the repo's git hooks (.githooks/)
#   2. expose .agents/AGENTS.md (root AGENTS.md, .claude/CLAUDE.md) and the skills (.claude/skills)
set -e
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git config core.hooksPath .githooks
chmod +x .githooks/* scripts/*.py scripts/*.sh
echo "hooks: core.hooksPath -> .githooks"

# Instruction-file aliases (symlinks, so there is a single source of truth).
link() { # link <target> <link-path>
  mkdir -p "$(dirname "$2")"
  if [ -e "$2" ] && [ ! -L "$2" ]; then
    echo "skip:  $2 exists and is not a symlink"
  else
    ln -sfn "$1" "$2" && echo "link:  $2 -> $1"
  fi
}
link .agents/AGENTS.md AGENTS.md                # Codex, Cursor, Jules, Amp, generic
link ../.agents/AGENTS.md .claude/CLAUDE.md     # Claude Code project memory
link ../.agents/skills .claude/skills           # Claude Code skill discovery
