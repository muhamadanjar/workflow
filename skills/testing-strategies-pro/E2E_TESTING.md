# End-to-End Testing Guide

## Playwright for Web Testing

### Basic Test
```python
from playwright.sync_api import sync_playwright, expect

def test_user_registration():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate
        page.goto("http://localhost:3000/register")
        
        # Fill form
        page.fill('input[name="name"]', "John Doe")
        page.fill('input[name="email"]', "john@example.com")
        page.fill('input[name="password"]', "SecurePass123")
        
        # Submit
        page.click('button:has-text("Register")')
        
        # Assert
        expect(page).to_have_title("Welcome, John")
        page.goto("http://localhost:3000/dashboard")
        expect(page.locator("text=john@example.com")).to_be_visible()
        
        browser.close()
```

### Using Fixtures
```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

def test_login(page):
    page.goto("http://localhost:3000/login")
    page.fill('input[name="email"]', "user@example.com")
    page.fill('input[name="password"]', "password")
    page.click('button:has-text("Login")')
    expect(page).to_have_url("http://localhost:3000/dashboard")
```

### Complex Interactions
```python
def test_search_and_filter(page):
    page.goto("http://localhost:3000/products")
    
    # Search
    page.fill('input[placeholder="Search products"]', "laptop")
    page.press('input[placeholder="Search products"]', "Enter")
    
    # Wait for results
    page.wait_for_selector(".product-card")
    
    # Filter
    page.click('input[type="checkbox"][value="electronics"]')
    
    # Verify
    products = page.locator(".product-card")
    count = products.count()
    assert count > 0
    
    # Get specific product
    first_product = products.first
    title = first_product.locator(".product-title").text_content()
    assert "laptop" in title.lower()
```

### Debugging
```python
def test_with_debugging(page):
    page.goto("http://localhost:3000")
    
    # Pause for manual inspection
    page.pause()
    
    # Take screenshot
    page.screenshot(path="screenshot.png")
    
    # Check console errors
    messages = []
    page.on("console", lambda msg: messages.append(msg.text))
    
    page.click("button")
    assert not any("error" in m.lower() for m in messages)
```

## Cypress for React/Frontend

### Test Structure
```javascript
describe('User Dashboard', () => {
    beforeEach(() => {
        cy.visit('http://localhost:3000/dashboard');
        cy.login('user@example.com', 'password');
    });
    
    it('displays user profile', () => {
        cy.get('[data-testid="user-name"]').should('contain', 'John');
        cy.get('[data-testid="user-email"]').should('contain', 'john@example.com');
    });
    
    it('can update profile', () => {
        cy.get('[data-testid="edit-profile"]').click();
        cy.get('input[name="name"]').clear().type('Jane');
        cy.get('button:contains("Save")').click();
        
        cy.get('[data-testid="user-name"]').should('contain', 'Jane');
    });
});
```

### API Mocking in Cypress
```javascript
it('loads user data', () => {
    cy.intercept('GET', '/api/users/me', {
        statusCode: 200,
        body: { id: '1', name: 'John', email: 'john@example.com' }
    }).as('getUser');
    
    cy.visit('/dashboard');
    cy.wait('@getUser');
    cy.get('[data-testid="user-name"]').should('contain', 'John');
});
```

## API Testing with REST Client

### REST Assured (Java) / Postman
```python
# Using requests library
import requests
import json

def test_api_flow():
    # Create user
    response = requests.post(
        "http://localhost:8080/api/users",
        json={"name": "John", "email": "john@example.com"}
    )
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Get user
    response = requests.get(f"http://localhost:8080/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John"
    
    # Update user
    response = requests.put(
        f"http://localhost:8080/api/users/{user_id}",
        json={"name": "Jane"}
    )
    assert response.status_code == 200
    
    # Delete user
    response = requests.delete(f"http://localhost:8080/api/users/{user_id}")
    assert response.status_code == 204
```

## Performance E2E Tests

### Load Testing with Locust
```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def index(self):
        self.client.get("/")
    
    @task
    def users(self):
        self.client.get("/api/users")
    
    @task
    def create_user(self):
        self.client.post("/api/users", json={
            "name": "Test User",
            "email": "test@example.com"
        })
```

Run with: `locust -f locustfile.py --host=http://localhost:8080`

## Screenshot & Visual Regression

```python
def test_homepage_visual(page):
    page.goto("http://localhost:3000")
    
    # Take screenshot
    page.screenshot(path="homepage.png")
    
    # Compare with baseline (using external tool)
    # pixelmatch or resemble.js
```

## E2E Test Organization

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── test_login.py
│   │   ├── test_register.py
│   │   └── test_password_reset.py
│   ├── users/
│   │   ├── test_profile.py
│   │   ├── test_search.py
│   │   └── test_pagination.py
│   └── checkout/
│       ├── test_add_to_cart.py
│       ├── test_payment.py
│       └── test_order_confirmation.py
├── conftest.py          # Fixtures
└── helpers/
    ├── auth_helper.py
    └── api_helper.py
```

## E2E Best Practices

- ✅ Use data-testid attributes
- ✅ Wait for elements, don't sleep
- ✅ Test critical user journeys
- ✅ Use page objects for organization
- ✅ Run in CI/CD with headless browser
- ✅ Capture screenshots on failure
- ✅ Keep tests independent
- ✅ Use meaningful assertions

❌ Don't:
- ❌ Test every UI element
- ❌ Use hard waits (sleep)
- ❌ Share state between tests
- ❌ Test implementation details
- ❌ Create slow, flaky tests
