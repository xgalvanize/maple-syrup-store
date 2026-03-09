#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

if [ -z "${1:-}" ]; then
  echo "Usage: ./scripts/git-quick-push.sh \"your commit message\""
  exit 1
fi

COMMIT_MESSAGE="$1"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "❌ Not inside a git repository"
  exit 1
fi

if [ -z "$(git status --porcelain)" ]; then
  echo "ℹ️ No changes to commit"
  exit 0
fi

echo "📦 Staging changes..."
git add .

echo "📝 Committing..."
git commit -m "$COMMIT_MESSAGE"

echo "🚀 Pushing to remote..."
git push

echo "✅ Done"
