#!/bin/bash

echo "🍁 Maple Syrup Store - Running All Tests"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR" || exit 1

# Backend tests
echo "📦 Backend Tests"
echo "----------------"
cd "$PROJECT_DIR/backend" || exit 1

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    # shellcheck disable=SC1091
    source ../.venv/bin/activate
fi

pytest -v --cov=shop --cov-report=term-missing --cov-report=html
BACKEND_EXIT=$?
cd ..

echo ""
echo "🎨 Frontend Tests"
echo "-----------------"
cd "$PROJECT_DIR/frontend" || exit 1
npm test -- --coverage --watchAll=false
FRONTEND_EXIT=$?
cd ..

echo ""
echo "=========================================="
if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage reports:"
    echo "  Backend:  backend/htmlcov/index.html"
    echo "  Frontend: frontend/coverage/lcov-report/index.html"
    exit 0
else
    echo "❌ Some tests failed"
    [ $BACKEND_EXIT -ne 0 ] && echo "   Backend tests failed with exit code $BACKEND_EXIT"
    [ $FRONTEND_EXIT -ne 0 ] && echo "   Frontend tests failed with exit code $FRONTEND_EXIT"
    exit 1
fi
