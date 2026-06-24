# GitHub Copilot / Codex Integration Guide

Use AI Coding Skills with GitHub Copilot and OpenAI's Codex.

## Setup

### GitHub Copilot (VS Code)

**Step 1: Install Extension**
```
VS Code Extensions → GitHub Copilot
```

**Step 2: Add Skills to Workspace**
```bash
# Clone or copy to project root
git clone https://github.com/yourname/ai-coding-skills .skills

# Or symlink
ln -s ~/ai-coding-skills .skills
```

**Step 3: Reference in Comments**
```python
# @ai-coding-skills/python-async-pro/GUIDE.md
# Generate async function with proper error handling
```

### OpenAI API / Codex

**Option 1: Via System Prompt**
```python
import openai

skill_content = open('.skills/manifest.json').read()

response = openai.ChatCompletion.create(
    model="gpt-4",
    system=f"You have access to: {skill_content}",
    messages=[
        {"role": "user", "content": "Use go-microservices-pro/GRPC_GUIDE.md..."}
    ]
)
```

**Option 2: Via Files API**
```python
# Upload skill files to OpenAI Files API
# Reference in prompts
```

## Usage

### In Comments (VS Code)

**Single Skill Reference:**
```python
# Using @ai-coding-skills/fastapi-clean-architecture
# Generate a clean architecture service with dependency injection

class UserService:
    # Implement here
    pass
```

**Multiple Skills:**
```go
// @ai-coding-skills/go-microservices-pro/ARCHITECTURE_GUIDE.md
// @ai-coding-skills/testing-strategies-pro/UNIT_TESTING.md
// Build service with tests

type UserService struct {
    // ...
}
```

**Specific Sections:**
```javascript
// Using @ai-coding-skills/frontend-design-pro/ZUSTAND_PATTERNS.md
// Create store with TypeScript

import create from 'zustand';
```

### Command Palette

**Copilot Chat:**
```
Cmd+Shift+A → "Using @ai-coding-skills/..."
```

### Inline Suggestions

Comment with skill reference:
```python
# @ai-coding-skills/testing-strategies-pro/UNIT_TESTING.md
# Write pytest test with fixtures
def test_
```

Copilot will suggest based on skill context.

## Examples

### Example 1: REST API with Auth

```python
# @ai-coding-skills/api-design-patterns/REST_GUIDE.md
# @ai-coding-skills/api-design-patterns/AUTH_PATTERNS.md

from fastapi import FastAPI, Depends

app = FastAPI()

@app.post("/users")
async def create_user(
    user_data: dict,
    auth: str = Depends(verify_jwt)  # From AUTH_PATTERNS
):
    # Implement REST endpoint with JWT auth
    pass
```

### Example 2: Docker + Kubernetes Deployment

```yaml
# @ai-coding-skills/docker-kubernetes-ops/DOCKER_COMPOSE.md
# @ai-coding-skills/docker-kubernetes-ops/KUBERNETES_GUIDE.md

# Local development with Docker Compose
version: '3.8'

services:
  api:
    build: .
    # ... from DOCKER_COMPOSE.md
```

### Example 3: Testing Strategy

```go
// @ai-coding-skills/testing-strategies-pro/UNIT_TESTING.md
// Table-driven tests for all cases

func TestGetUser(t *testing.T) {
    tests := []struct {
        name string
        // ...
    }{
        // Implement table-driven tests
    }
}
```

## File Structure

Recommended project structure:
```
project/
├── .skills/               # Symlink or clone
│   ├── manifest.json
│   ├── go-microservices-pro/
│   ├── testing-strategies-pro/
│   └── ...
├── src/
│   └── main.go           # Reference skills in comments
├── tests/
└── README.md
```

## VS Code Settings

### .vscode/settings.json
```json
{
  "github.copilot.enable": {
    "yaml": true,
    "plaintext": true,
    "markdown": true
  },
  "editor.quickSuggestions": {
    "comments": true
  }
}
```

### .copilot-context.txt (Optional)
```
Available Skills:
- go-microservices-pro (GRPC_GUIDE.md, ARCHITECTURE_GUIDE.md)
- testing-strategies-pro (UNIT_TESTING.md)
- docker-kubernetes-ops

Usage: @ai-coding-skills/skill-name/GUIDE.md
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Accept suggestion | Tab |
| Dismiss | Esc |
| Open in side panel | Cmd+Shift+A |
| Copilot Chat | Cmd+I |

## Tips

### Effective Skill References

✅ **Good:**
```
// @ai-coding-skills/go-microservices-pro/PATTERNS.md
// Implement circuit breaker
```

❌ **Poor:**
```
// Use skills
// Add circuit breaker pattern
```

### Chain Skills

```python
# @ai-coding-skills/fastapi-clean-architecture
# @ai-coding-skills/api-design-patterns/REST_GUIDE.md
# @ai-coding-skills/testing-strategies-pro

# FastAPI endpoint with REST patterns and tests
```

### With Context

```go
// Service handling payment processing
// @ai-coding-skills/api-design-patterns/THIRD_PARTY.md
// @ai-coding-skills/go-microservices-pro/PRODUCTION.md

type PaymentService struct {
    // Implement with third-party API patterns
}
```

## Troubleshooting

### Copilot not suggesting

**Check:**
1. Copilot is enabled
2. Comment format is correct: `// @ai-coding-skills/...`
3. Skill name matches manifest.json
4. File language is supported

**Fix:**
```
VS Code → GitHub Copilot → Sign out
Sign back in
Restart VS Code
```

### Skills not found

**Verify path:**
```bash
ls .skills/manifest.json
# Should exist
```

**Update path:**
- Absolute: `/Users/name/ai-coding-skills`
- Relative: `./.skills`
- Symlink: `ln -s ~/ai-coding-skills .skills`

### API Rate Limits

If using OpenAI API directly:
```python
import time
time.sleep(1)  # Rate limit handling
```

## Best Practices

1. **Be specific** - Include GUIDE_NAME.md
2. **Chain related skills** - Testing + Backend together
3. **Include context** - What you're building
4. **Review suggestions** - Copilot code needs verification
5. **Keep skills updated** - `git pull` in .skills/ directory

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Setup AI Skills
  run: |
    git clone https://github.com/yourname/ai-coding-skills .skills

- name: Generate with Copilot
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    # Use skills in generation
```

## Support

Issues:
1. Check skill README
2. Verify skill path
3. Review INTEGRATION.md
4. Check GitHub issues

Version: 1.0.0
Last Updated: 2024-06-24
