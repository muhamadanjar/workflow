# Pi AI Assistant Integration Guide

Use AI Coding Skills with Pi AI Assistant.

## Setup

### Pi Web Interface

**Step 1: Access Pi**
```
pi.ai → Sign In → Conversations
```

**Step 2: Enable Skills**
```
Settings → AI Capabilities → Code Skills
→ Enable "Custom Skills from URLs"
```

**Step 3: Add Skill Source**
```
Add Repository:
https://github.com/yourname/ai-coding-skills

Or Raw Files:
https://raw.githubusercontent.com/yourname/ai-coding-skills/main/manifest.json
```

### Pi Mobile App

**Similar setup:**
```
Settings → Code Assistance
→ Add Skill Repository
```

## Usage

### Mention Syntax

**Basic Skill Reference:**
```
@go-microservices-pro

Show me how to structure a Go service
```

**With Specific Guide:**
```
@go-microservices-pro/GRPC_GUIDE.md

Implement a gRPC service with error handling
```

**Multiple Skills:**
```
@go-microservices-pro @testing-strategies-pro @docker-kubernetes-ops

Create a tested, containerized Go service
```

**Natural Language:**
```
Using skills: go-microservices-pro and docker-kubernetes-ops

I need a production-ready service setup
```

### In Conversations

**Start:**
```
I want to build a REST API.

[Available skills: api-design-patterns, testing-strategies-pro, python-async-pro]

Show me REST design patterns from @api-design-patterns
```

**Reference During Chat:**
```
User: Show GRPC implementation

Pi: Based on @go-microservices-pro/GRPC_GUIDE.md:
    [generates code from guide]
```

**Ask Pi to Use Skill:**
```
User: Can you use @testing-strategies-pro to write pytest tests?

Pi: Sure, using UNIT_TESTING.md patterns...
```

## Examples

### Example 1: REST API with Testing

```
I'm building a Python API. Can you help?

Use:
@api-design-patterns/REST_GUIDE.md for API design
@fastapi-clean-architecture for structure
@testing-strategies-pro/UNIT_TESTING.md for tests

Generate:
1. API endpoint with REST conventions
2. Clean architecture service layer
3. Pytest unit tests
```

### Example 2: Go Microservice with DevOps

```
Help me create a production Go service

Skills:
@go-microservices-pro - for service patterns
@docker-kubernetes-ops - for deployment
@testing-strategies-pro - for tests

Include:
- Layered architecture
- gRPC API
- Docker container
- Kubernetes manifests
```

### Example 3: React App

```
Building React dashboard

Using:
@frontend-design-pro for design patterns
@api-design-patterns/AUTH_PATTERNS.md for auth
@testing-strategies-pro for E2E tests

Generate:
- TypeScript React component
- Zustand store
- API integration
- E2E test
```

## Feature Integration

### Skills Discovery

**Ask Pi directly:**
```
What skills are available?

Pi lists all skills from manifest.json with descriptions
```

**Search:**
```
@skills: testing

Pi shows: testing-strategies-pro with guides
```

**Recommendations:**
```
I'm building a gRPC service

Pi suggests:
- @go-microservices-pro (GRPC_GUIDE)
- @testing-strategies-pro (UNIT_TESTING)
- @docker-kubernetes-ops
```

### Code Generation

**Generate with Context:**
```
@go-microservices-pro

Generate a circuit breaker implementation
based on PATTERNS.md
```

**Iterative Refinement:**
```
User: Add retry logic
Pi: Using PATTERNS.md exponential backoff...
[updates code]

User: Make it production-ready
Pi: Using PRODUCTION.md guidelines...
[adds logging, metrics, etc.]
```

## Best Practices

### Effective References

✅ **Good:**
```
@go-microservices-pro/ARCHITECTURE_GUIDE.md

Show repository pattern for user service
```

❌ **Poor:**
```
Show me architecture

I need a pattern
```

### Skill Chain

```
@fastapi-clean-architecture
@testing-strategies-pro
@docker-kubernetes-ops

Create full FastAPI project with tests and Docker
```

### Get Explanations

```
@api-design-patterns/AUTH_PATTERNS.md

Explain JWT refresh token pattern
```

### Compare Approaches

```
@testing-strategies-pro/UNIT_TESTING.md

Compare mocking approaches:
- unittest.mock (Python)
- testify (Go)
- Jest (React)
```

## Conversation Starters

### For Beginners
```
I'm new to Go microservices.

Show me @go-microservices-pro/ARCHITECTURE_GUIDE.md
with a simple example.
```

### For Experts
```
@go-microservices-pro/PATTERNS.md

Implement saga pattern for distributed transactions
with proper error handling.
```

### For Learning
```
Teach me about testing using @testing-strategies-pro

Compare unit, integration, and E2E approaches
with real code examples.
```

## Mobile Usage

### On Phone

```
"Hey Pi, show me @api-design-patterns/REST_GUIDE.md

What's the right HTTP status code for not found?"

[Pi responds with example]

"Generate an endpoint using that pattern"

[Pi generates code]
```

### Offline Support

Skills can be cached:
```
Settings → Sync Skills Locally
→ Download for offline use
```

## Troubleshooting

### Skills not showing

**Check connection:**
```
Settings → Repository Status
→ Verify URL is accessible
```

**Refresh:**
```
Settings → Skills → Refresh All
```

**Re-add:**
```
Remove and re-add repository
```

### Wrong skill loaded

**Specify explicitly:**
```
@go-microservices-pro (exact name)

NOT: @go-micro or @GoMicroservices
```

**Verify manifest:**
```
Check manifest.json for exact skill IDs
```

### Rate Limiting

Pi has built-in rate limits:
```
If limited, try:
- Shorter prompts
- Specific guides only
- Wait a moment
```

## Tips

### Save Conversations

Conversations with skills are saved:
```
Conversations → [name] 
→ Contains @skill references
→ Reusable
```

### Share Code

Generated code:
```
Copy button → Share via link
Code is attributed to Pi + skills
```

### Export

```
Conversation → Export
→ Markdown with skill references
→ Code, explanations, guides
```

## Command Reference

| Command | Example |
|---------|---------|
| Reference skill | `@skill-name` |
| Specific guide | `@skill/GUIDE.md` |
| Multiple | `@skill1 @skill2` |
| Search | `@skills: keyword` |
| Help | `@help skills` |

## Integration Workflow

### Typical Flow
1. **Start** - Mention relevant skill
2. **Generate** - Pi uses skill guides
3. **Refine** - Ask for modifications
4. **Test** - Generate tests from skills
5. **Deploy** - Use DevOps skills

### Example Workflow
```
Me: I need a REST API

Pi: I can help! Which skills?
Me: @api-design-patterns

Pi: Using REST_GUIDE.md...
[generates code]

Me: Add JWT auth
Pi: Using AUTH_PATTERNS.md...
[updates code]

Me: Write tests
Pi: Using @testing-strategies-pro...
[generates tests]
```

## Support

For issues:
1. Check skill README
2. Verify skill repository URL
3. Review INTEGRATION.md
4. Contact Pi support

Version: 1.0.0
Last Updated: 2024-06-24
Compatible: Pi v1.0+
