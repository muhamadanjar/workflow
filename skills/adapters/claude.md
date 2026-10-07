# Claude Integration Guide

Use AI Coding Skills with Claude Code, Claude.ai, and Claude API.

## Setup

### Claude Code (CLI)

**Option 1: Local Installation**
```bash
# Copy skills to Claude config
cp -r ~/.claude/skills ~/.claude/skills-backup
# Skills auto-discover from ~/.claude/skills/
```

**Option 2: Symlink from GitHub**
```bash
cd ~/.claude
git clone https://github.com/yourname/ai-coding-skills skills
# Skills now auto-load
```

### Claude.ai Web

Skills aren't auto-available in web interface. Instead:

1. Copy relevant guide content
2. Paste into chat context
3. Reference specific sections

Example:
```
I'm using [go-microservices-pro] skill.

[PASTE GRPC_GUIDE.md CONTENT HERE]

Can you show me how to implement streaming gRPC?
```

## Usage

### Invoking Skills in Claude Code

**Direct reference:**
```
I need Go microservices patterns.
```

Claude recognizes available skills automatically.

**Explicit skill invocation:**
```
/use go-microservices-pro

Show me the gRPC implementation pattern
```

**Specific guide:**
```
Using go-microservices-pro/GRPC_GUIDE.md

Implement a gRPC service with proper error handling
```

### Advanced Usage

**Multiple skills:**
```
/use go-microservices-pro testing-strategies-pro

Write a gRPC service with comprehensive tests
```

**Memory/Context:**
Skills integrate with Claude's memory system automatically.

**Search within skills:**
```
Search skills for: "circuit breaker pattern"
```

## Examples

### Example 1: Build Go Service

```
/use go-microservices-pro docker-kubernetes-ops

I need to:
1. Create a gRPC service (see GRPC_GUIDE.md)
2. Containerize it (see DOCKER_GUIDE.md)
3. Deploy to Kubernetes

Generate the complete code.
```

### Example 2: Test Python API

```
/use fastapi-clean-architecture testing-strategies-pro

I have a FastAPI app with clean architecture.
Generate:
1. Unit tests (UNIT_TESTING.md - Python section)
2. Integration tests (INTEGRATION_TESTING.md)
3. API endpoint tests

Use pytest fixtures and mocking.
```

### Example 3: Design React App

```
/use frontend-design-pro api-design

Build a React dashboard that:
1. Calls REST API (REST_GUIDE.md)
2. Uses Zustand for state (ZUSTAND_PATTERNS.md)
3. Implements JWT auth (AUTH_PATTERNS.md)
4. Uses shadcn components (SHADCN_GUIDE.md)

Generate full code with TypeScript.
```

## Configuration

### ~/.claude/settings.json

Add custom skill settings:
```json
{
  "skillOverrides": {
    "go-microservices-pro": "on",
    "testing-strategies-pro": "on"
  }
}
```

### Skill Directories

Check available directories:
```bash
ls ~/.claude/skills/
```

## Keyboard Shortcuts

- `Ctrl+K` - New chat (can reference skills)
- `/` - Command palette (for `/use` commands)
- `@` - File/skill mention in Claude Code

## Troubleshooting

### Skills not appearing

**Check installation:**
```bash
ls ~/.claude/skills/
# Should show: manifest.json, go-microservices-pro/, etc.
```

**Restart Claude:**
```bash
# Close and reopen Claude Code
```

### Skill not recognized

**Verify name:**
```bash
# Use exact folder name from manifest.json
# Use kebab-case: go-microservices-pro
# NOT: GoMicroservicesPro or go_microservices_pro
```

**Clear cache:**
```bash
rm -rf ~/.claude/.cache
```

### Too much context

**Use specific guides:**
```
Instead of: /use go-microservices-pro
Use: go-microservices-pro/GRPC_GUIDE.md only
```

## Tips & Tricks

### Quick Access
```
# Reference by guide name directly
Can you explain the circuit breaker pattern?
# Claude finds it in go-microservices-pro/PATTERNS.md
```

### Combine Skills
```
/use fastapi-clean-architecture docker-kubernetes-ops api-design

Design and implement a production-ready REST API
```

### Generate from Examples
```
/use testing-strategies-pro

Show me table-driven tests (from Go section) applied to Python pytest
```

### Export Skill Content
```bash
# Copy specific guide
cp ~/.claude/skills/go-microservices-pro/GRPC_GUIDE.md ~/my-project/
```

## Platform Details

### Claude Code (CLI)
- ✅ Auto-discovers skills
- ✅ `/use` command support
- ✅ Full skill context available
- ✅ Memory integration

### Claude.ai Web
- ⚠️ Manual skill reference (copy/paste)
- ⚠️ Limited context window
- ✅ Can reference skill names
- ✅ Can share skill links

### Claude API
- ✅ Can pass skill content in system prompt
- ✅ Structured skill metadata via manifest.json
- ✅ Full context available
- ✅ Batch processing supported

## Best Practices

1. **Use specific guides** - Reference GUIDE_NAME.md for focus
2. **Include version** - Check manifest.json for compatibility
3. **Combine related skills** - Testing + Backend patterns work well together
4. **Test the code** - Claude generates working code, but verify
5. **Check examples** - Each guide has examples

## Integration with Projects

### Project .claude/settings.json
```json
{
  "skillOverrides": {
    "testing-strategies-pro": "on",
    "go-microservices-pro": "on"
  }
}
```

### Project CLAUDE.md
```markdown
# Project Skills

Use these skills for this project:
- go-microservices-pro (ARCHITECTURE_GUIDE.md, GRPC_GUIDE.md)
- testing-strategies-pro (UNIT_TESTING.md, INTEGRATION_TESTING.md)
- docker-kubernetes-ops (DOCKER_COMPOSE.md, KUBERNETES_GUIDE.md)
```

## Support

For issues:
1. Check skill README.md
2. Review relevant guide
3. Check INTEGRATION.md
4. Open issue on GitHub

Version: 1.0.0
Last Updated: 2024-06-24
