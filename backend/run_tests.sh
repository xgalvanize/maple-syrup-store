#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🧪 Running Backend Tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    # shellcheck disable=SC1091
    source ../.venv/bin/activate
else
    echo "⚠️  Warning: Virtual environment not found at ../.venv"
    echo "   Make sure dependencies are installed: pip install -r requirements.txt"
    echo ""
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run tests with coverage
pytest -v --cov=shop --cov-report=term-missing --cov-report=html

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Tests complete! Coverage report saved to htmlcov/index.html"
else
    echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
