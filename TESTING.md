# Testing Guide

This project includes comprehensive automated testing for both backend (Django/Python) and frontend (React).

## Backend Tests

### Technologies
- **pytest**: Test framework
- **pytest-django**: Django integration for pytest
- **pytest-cov**: Code coverage reporting
- **factory-boy**: Test data factories
- **faker**: Fake data generation

### Test Structure

```
backend/shop/tests/
├── __init__.py
├── factories.py          # Test data factories
├── test_models.py        # Django model tests
├── test_schema.py        # GraphQL schema/integration tests
└── test_shipping.py      # Shipping logic tests
```

### Running Backend Tests

From the `backend/` directory:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest shop/tests/test_models.py

# Run specific test class
pytest shop/tests/test_models.py::TestProduct

# Run specific test
pytest shop/tests/test_models.py::TestProduct::test_create_product

# Run tests with coverage report
pytest --cov=shop --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel (faster)
pytest -n auto
```

### Backend Test Coverage

The backend tests cover:

✅ **Models** (test_models.py)
- Product CRUD operations
- Cart and CartItem relationships
- Order creation and management
- OrderItem with deleted products
- Model string representations

✅ **GraphQL Schema** (test_schema.py)
- Product queries (all products, single product)
- User registration and authentication
- Cart mutations (add, update, remove)
- Checkout process with inventory management
- Admin mutations (create/update products, update order status)
- Shipping estimation queries
- Permission checks (staff vs regular users)

✅ **Shipping Logic** (test_shipping.py)
- Local radius shipping (P0R postal codes)
- Ontario shipping
- Canada-wide shipping (all provinces)
- International shipping
- Edge cases (empty/malformed postal codes, case insensitivity)

---

## Frontend Tests

### Technologies
- **Jest**: Test framework (included with Create React App)
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: Custom matchers

### Test Structure

```
frontend/src/__tests__/
├── ProductCard.test.js   # ProductCard component tests
├── Navbar.test.js        # Navigation component tests
├── Notification.test.js  # Notification component tests
└── HomePage.test.js      # HomePage integration tests
```

### Running Frontend Tests

From the `frontend/` directory:

```bash
# Install dependencies first (if not already installed)
npm install

# Run all tests in watch mode
npm test

# Run all tests once (CI mode)
npm test -- --watchAll=false

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test ProductCard.test.js

# Update snapshots (if using snapshot testing)
npm test -- -u
```

### Frontend Test Coverage

The frontend tests cover:

✅ **ProductCard Component**
- Renders product information correctly
- Displays product images conditionally
- Handles "Add to Cart" button clicks
- Formats prices properly
- Accessibility attributes

✅ **Navbar Component**
- Renders navigation links
- Shows/hides links based on authentication state
- Displays cart badge with item count
- Handles logout functionality
- Shows admin link for staff users

✅ **Notification Component**
- Renders success notifications
- Renders error notifications
- Handles empty/null messages
- CSS class application

✅ **HomePage Component**
- Displays loading state
- Renders product list after data loads
- Handles error states
- Shows empty state message

---

## Test Scripts

Convenience scripts for running tests:

### Backend Test Script

Create `backend/run_tests.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"

echo "🧪 Running Backend Tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# Run tests with coverage
pytest -v --cov=shop --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests complete! Coverage report saved to htmlcov/index.html"
```

Make it executable:
```bash
chmod +x backend/run_tests.sh
```

### Frontend Test Script

Create `frontend/run_tests.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"

echo "🧪 Running Frontend Tests..."
echo ""

# Run tests with coverage
npm test -- --coverage --watchAll=false

echo ""
echo "✅ Tests complete! Coverage report saved to coverage/lcov-report/index.html"
```

Make it executable:
```bash
chmod +x frontend/run_tests.sh
```

### Run All Tests Script

Create `scripts/test.sh` in the project root:

```bash
#!/bin/bash

echo "🍁 Maple Syrup Store - Running All Tests"
echo "=========================================="
echo ""

# Backend tests
echo "📦 Backend Tests"
echo "----------------"
cd backend
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi
pytest -v --cov=shop --cov-report=term-missing
BACKEND_EXIT=$?
cd ..

echo ""
echo "🎨 Frontend Tests"
echo "-----------------"
cd frontend
npm test -- --coverage --watchAll=false
FRONTEND_EXIT=$?
cd ..

echo ""
echo "=========================================="
if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
```

Make it executable:
```bash
chmod +x scripts/test.sh
```

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=shop --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
```

---

## Best Practices

### Writing Good Tests

1. **Arrange-Act-Assert Pattern**
   ```python
   def test_example():
       # Arrange: Set up test data
       user = UserFactory()
       
       # Act: Perform the action
       result = some_function(user)
       
       # Assert: Verify the result
       assert result == expected_value
   ```

2. **Test One Thing Per Test**
   - Each test should verify a single behavior
   - Makes it easier to identify failures

3. **Use Descriptive Test Names**
   - Good: `test_checkout_fails_with_insufficient_inventory`
   - Bad: `test_checkout_2`

4. **Mock External Dependencies**
   - Mock email sending, external APIs, etc.
   - Keep tests fast and isolated

5. **Keep Tests Independent**
   - Tests should not depend on each other
   - Each test should be able to run in isolation

### Coverage Goals

- **Target**: 80%+ coverage for critical paths
- **Focus Areas**:
  - Business logic (checkout, inventory, shipping)
  - Authentication and authorization
  - Data validation
  - Error handling

---

## Common Issues & Solutions

### Backend

**Issue**: `ModuleNotFoundError: No module named 'shop'`
```bash
# Solution: Make sure you're in the backend/ directory
cd backend
pytest
```

**Issue**: `django.db.utils.OperationalError: database is locked`
```bash
# Solution: Use pytest-django's database setup
# Already configured in pytest.ini
```

### Frontend

**Issue**: `Cannot find module '@testing-library/react'`
```bash
# Solution: Install test dependencies
npm install
```

**Issue**: Tests fail with Apollo Client errors
```bash
# Solution: Use MockedProvider in tests
# Examples in test files show proper setup
```

---

## Next Steps

After setting up tests:

1. ✅ **Run tests locally** to verify everything works
2. ⚙️ **Set up CI/CD** to run tests automatically
3. 📊 **Monitor coverage** and add tests for uncovered code
4. 🔄 **Run tests before commits** (use git hooks)
5. 📝 **Write tests for new features** as you add them

## Running Tests in Docker

To run tests in the containerized environment:

```bash
# Backend tests
kubectl exec -it deployment/backend -- pytest

# Or via docker directly
docker run --rm maple-syrup-store-backend pytest
```

---

Happy testing! 🧪🍁
