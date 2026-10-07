# OpenCode Integration Guide

Use AI Coding Skills with Anthropic's OpenCode platform.

## Setup

### OpenCode Platform

**Step 1: Create Workspace**
```
opencode.anthropic.com → New Workspace
```

**Step 2: Import Skills**

**Option A: GitHub Integration**
```
Settings → Connected Repos
→ Add: https://github.com/yourname/ai-coding-skills
```

**Option B: Manual Upload**
```
Files → Upload
→ Drag .skills/ folder
```

**Option C: Cloud Sync**
```
Settings → Cloud Storage
→ Link to GitHub/GitLab
```

**Step 3: Enable in Workspace**
```
Skills → Available Skills
→ Toggle on: All skills
```

## Usage

### Command Syntax

**Basic:**
```
Skills: go-microservices-pro

Generate a gRPC service
```

**With Guide:**
```
Skills: go-microservices-pro, GRPC_GUIDE.md

Implement streaming gRPC endpoint
```

**Multiple Skills:**
```
Skills: go-microservices-pro, testing-strategies-pro, docker-kubernetes-ops

Create Go service with tests and Docker setup
```

**Specific Section:**
```
Skills: api-design, REST_GUIDE.md, status codes section

Design REST API with proper HTTP status codes
```

### Workspace Configuration

**opencode.yaml**
```yaml
skills:
  enabled:
    - go-microservices-pro
    - testing-strategies-pro
    - api-design
    - docker-kubernetes-ops
  search: true
  context: full
```

### Project Setup

**.opencode/config.json**
```json
{
  "skills": {
    "auto_reference": true,
    "guides": [
      "go-microservices-pro/ARCHITECTURE_GUIDE.md",
      "testing-strategies-pro/INTEGRATION_TESTING.md"
    ]
  }
}
```

## Examples

### Example 1: Build Microservice

```
Skills: go-microservices-pro, docker-kubernetes-ops

I need to build a production-ready Go microservice.

Requirements:
1. Layered architecture (see ARCHITECTURE_GUIDE.md)
2. gRPC API (see GRPC_GUIDE.md)
3. Docker container (see DOCKER_GUIDE.md)
4. Kubernetes deployment (see KUBERNETES_GUIDE.md)

Generate complete scaffolding.
```

### Example 2: API with Authentication

```
Skills: api-design

Build REST API with:
1. Resource-oriented design (REST_GUIDE.md)
2. JWT authentication (AUTH_PATTERNS.md)
3. Third-party integration (THIRD_PARTY.md)

Include error handling and rate limiting.
```

### Example 3: Complete Test Suite

```
Skills: testing-strategies-pro

Generate test suite for Python FastAPI app:
1. Unit tests (UNIT_TESTING.md - Python)
2. Integration tests (INTEGRATION_TESTING.md)
3. E2E tests (E2E_TESTING.md)

Include fixtures, mocks, and factories.
```

## Project Structure

### Recommended Layout
```
project/
├── .opencode/
│   ├── config.json
│   └── skills-manifest.json
├── skills/              # Symlink
│   └── -> ~/.opencode/skills
├── src/
├── tests/
└── README.md
```

### .gitignore
```
.opencode/cache/
.opencode/logs/
skills/ -> symlink only
```

## Features

### Skill Search
```
Search in Skills → "circuit breaker"
→ Finds: go-microservices-pro/PATTERNS.md
```

### Smart Context
```
Skills: [auto-detect from project]
→ OpenCode suggests relevant skills based on:
  - File types (.go, .py, .jsx)
  - Project structure
  - Dependencies
```

### Code Generation
```
Skills: go-microservices-pro, testing-strategies-pro

Generate unit tests for UserService
→ Creates complete test file with:
  - Table-driven tests
  - Mocks
  - Error cases
  - Coverage comments
```

### Documentation
```
Skills: [all]

Generate project README using:
1. Skills overview
2. Architecture patterns
3. Testing approach
4. Deployment guide
```

## Integration Features

### IDE Support

**VS Code OpenCode Extension:**
```
VS Code → Extensions → OpenCode
→ Autocomplete with skills
```

**Keyboard Shortcuts:**
```
Cmd+K → "Skills: " → Shows available
Cmd+Shift+S → Open Skills panel
```

### Terminal Integration

```bash
# Generate with skills
opencode generate --skill go-microservices-pro --guide GRPC_GUIDE.md

# List available
opencode skills list

# Search
opencode skills search "circuit breaker"
```

### API Integration

```python
import opencode

# Use in scripts
client = opencode.Client()
skills = client.get_skills()
grpc_guide = skills['go-microservices-pro']['GRPC_GUIDE.md']

# Generate code
result = client.generate(
    prompt="Implement gRPC service",
    skills=['go-microservices-pro'],
    guides=['GRPC_GUIDE.md']
)
```

## Configuration

### Global Settings

**~/.opencode/config.yaml**
```yaml
default_skills:
  - go-microservices-pro
  - testing-strategies-pro

skill_path: ~/ai-coding-skills
auto_update: true
context_limit: 8000
```

### Project Overrides

**.opencode/settings.json**
```json
{
  "skills": {
    "enabled": ["go-microservices-pro"],
    "disabled": ["mermaid-diagrams"],
    "priority": ["testing-strategies-pro"]
  }
}
```

## Tips & Tricks

### Quick Access
```
# Use skill aliases
Skills: go-micro  # auto-completes to go-microservices-pro

# Context hints
Skills: testing  # shows all testing-related skills
```

### Combine with Workspace

```
Workspace:
- Language: Go
- Framework: gRPC
- Testing: Go testing

Skills: [auto-selected based on workspace]
```

### Export Skill Usage

```
Tools → Export → Skill Usage Report
→ Shows which skills used in project
```

## Troubleshooting

### Skills not loaded

**Check status:**
```
Status → Skills → [list]
```

**Reload:**
```
Settings → Reload Skills
```

**Update:**
```
Skills → Update All
```

### Manifest errors

**Validate:**
```bash
opencode validate-skills manifest.json
```

**Fix:**
```bash
opencode fix-manifest --auto
```

### Performance

If slow:
```
Settings → Skill Context → Reduce
→ Load fewer guides per skill
```

## Best Practices

1. **Enable only needed skills** - Reduces context
2. **Use guides explicitly** - Faster, more focused
3. **Combine related skills** - Better results
4. **Review generated code** - Always verify
5. **Keep skills updated** - `opencode update-skills`

## Support

For issues:
1. Check skill README
2. Run `opencode validate`
3. Review INTEGRATION.md
4. Contact OpenCode support

Version: 1.0.0
Last Updated: 2024-06-24
Compatible: OpenCode v2.0+
