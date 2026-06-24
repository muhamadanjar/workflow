# Integration Guide - Using Skills Across AI Coding Agents

These skills are platform-agnostic and work with multiple AI coding assistants: **Claude**, **Codex**, **OpenCode**, and **Pi**.

## Platform-Specific Setup

Choose your platform:

- **[Claude Integration](./adapters/claude.md)** - Claude Code, Claude.ai
- **[Codex Integration](./adapters/codex.md)** - GitHub Copilot, OpenAI Codex
- **[OpenCode Integration](./adapters/opencode.md)** - Anthropic OpenCode
- **[Pi Integration](./adapters/pi.md)** - Pi AI Assistant

## How Skills Work

Each skill is a collection of guides and documentation organized by topic.

### Structure
```
skill-name/
├── README.md              # Overview
├── GUIDE_1.md             # Detailed guide
├── GUIDE_2.md             # Detailed guide
└── skill.yaml             # Metadata
```

### Using a Skill

All platforms follow similar patterns:

1. **Reference the skill** in your prompt
2. **Mention specific guides** if needed
3. **Ask for code examples** or best practices
4. **Platform generates** contextual responses

### Example: Using Go Microservices Skill

**Claude:**
```
/use go-microservices-pro

I need to build a gRPC service. Can you show me GRPC_GUIDE.md patterns?
```

**Codex:**
```
# Using @go-microservices-pro/GRPC_GUIDE.md

// Show me gRPC implementation
```

**OpenCode:**
```
Skills: go-microservices-pro

Build a gRPC service with proper error handling
```

**Pi:**
```
[skills: go-microservices-pro, GRPC_GUIDE]

Help me implement gRPC streaming
```

## Available Skills

| Skill | Category | Best For |
|-------|----------|----------|
| python-async-pro | Backend | Python async/await patterns |
| fastapi-clean-architecture | Backend | FastAPI + Clean Architecture |
| frontend-design-pro | Frontend | React + TypeScript + Design Systems |
| pubsub-messaging | Backend | RabbitMQ, Redis messaging |
| mermaid-diagrams | Documentation | Architecture diagrams |
| redis-caching | Infrastructure | Caching patterns & optimization |
| database-design | Infrastructure | SQL schema & performance |
| go-microservices-pro | Backend | Go services & gRPC |
| docker-kubernetes-ops | DevOps | Containers & orchestration |
| api-design-patterns | Backend | REST, OAuth, Third-party APIs |
| testing-strategies-pro | Testing | Unit, Integration, E2E tests |

## Skill Manifest

Check `manifest.json` for:
- All available skills
- Guide files per skill
- Platform support
- Version info
- Keywords & categories

## Installation & Distribution

### Option 1: GitHub Repository
```bash
git clone https://github.com/yourname/ai-coding-skills
cd ai-coding-skills
```

### Option 2: NPM Package
```bash
npm install @yourname/ai-coding-skills
```

### Option 3: Local Directory
Copy skills folder to your local Claude/Codex/OpenCode config directory.

## Platform-Agnostic Usage

All platforms can access skills by:

1. **File path**: Reference by folder name
2. **Skill ID**: Use manifest ID
3. **Guide name**: Reference specific .md file

Example patterns:

```
# Claude
/use skill-id
/use go-microservices-pro GRPC_GUIDE.md

# Codex
@skill-id/GUIDE_NAME

# OpenCode
Skills: skill-id, guide-file

# Pi
[skills: skill-id, guide] or @skill-id
```

## Contributing New Skills

To add a skill:

1. Create folder with skill ID (kebab-case)
2. Add README.md + guides
3. Create skill.yaml with metadata
4. Update manifest.json
5. Submit PR

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT - Free to use and distribute

## Support

Each platform has specific setup instructions:
- [Claude](./adapters/claude.md#troubleshooting)
- [Codex](./adapters/codex.md#troubleshooting)
- [OpenCode](./adapters/opencode.md#troubleshooting)
- [Pi](./adapters/pi.md#troubleshooting)
