#!/bin/bash
#
# Watch for frontend file changes and auto-deploy to remote cluster
# Useful for development with live updates
#
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
cd "$PROJECT_DIR"

WATCH_DIR="$PROJECT_DIR/frontend/src"
DEPLOY_SCRIPT="$PROJECT_DIR/scripts/deploy-frontend-remote.sh"
DEBOUNCE_SECONDS=2

if ! command -v inotifywait &> /dev/null; then
    echo "❌ inotifywait not found. Install inotify-tools:"
    echo "   sudo pacman -S inotify-tools"
    exit 1
fi

echo "🍁 Watching Frontend for Changes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Directory: $WATCH_DIR"
echo "   Press Ctrl+C to stop"
echo ""

LAST_DEPLOY=0

inotifywait -m -r -e modify,create,delete "$WATCH_DIR" --format '%w%f' | while read FILE
do
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_DEPLOY))
    
    if [ $ELAPSED -ge $DEBOUNCE_SECONDS ]; then
        echo ""
        echo "📝 Change detected: $FILE"
        echo "🚀 Deploying..."
        
        if "$DEPLOY_SCRIPT"; then
            LAST_DEPLOY=$(date +%s)
            echo "✅ Deployed at $(date '+%H:%M:%S')"
        else
            echo "❌ Deploy failed"
        fi
        
        echo "👀 Watching for changes..."
    fi
done
