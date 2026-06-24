# AI Coding Skills - Professional Development Kit

Professional AI coding skills for fullstack engineering. Works with **Claude**, **Codex**, **OpenCode**, and **Pi**.

## 🎯 What's Inside

11 comprehensive skills covering:
- **Backend**: Python async, FastAPI, Go microservices, APIs
- **Frontend**: React, TypeScript, Design systems
- **Infrastructure**: Docker, Kubernetes, Redis, Databases
- **DevOps**: CI/CD, monitoring, deployment
- **Testing**: Unit, integration, E2E, performance
- **Architecture**: Patterns, microservices, clean code

## 🚀 Quick Start

### For Claude Users
```bash
# Skills auto-load from ~/.claude/skills/
# Already set up!

/use go-microservices-pro
```

### For GitHub Copilot
```bash
git clone https://github.com/yourname/ai-coding-skills .skills

# Reference in code comments:
# @ai-coding-skills/go-microservices-pro/GRPC_GUIDE.md
```

### For OpenCode
```
Settings → Skills → Add Repository
https://github.com/yourname/ai-coding-skills
```

### For Pi
```
Settings → Code Skills → Add Repository
https://github.com/yourname/ai-coding-skills
```

## 📚 Skills Overview

| Skill | Description | Guides | Category |
|-------|-------------|--------|----------|
| **python-async-pro** | Advanced Python async patterns | 3 | Backend |
| **fastapi-clean-architecture** | FastAPI + Clean Architecture | 2 | Backend |
| **frontend-design-pro** | React + TypeScript + Design systems | 6 | Frontend |
| **pubsub-messaging** | RabbitMQ, Redis messaging | 2 | Backend |
| **mermaid-diagrams** | Architecture & flow diagrams | 6 | Documentation |
| **redis-caching** | Caching patterns & optimization | 6 | Infrastructure |
| **database-design** | SQL schema & performance | 8 | Infrastructure |
| **go-microservices-pro** | Go services & gRPC | 5 | Backend |
| **docker-kubernetes-ops** | Containers & orchestration | 4 | DevOps |
| **api-design-patterns** | REST, OAuth, integrations | 4 | Backend |
| **testing-strategies-pro** | Unit, integration, E2E testing | 3 | Testing |

**Total**: 11 skills, 50+ comprehensive guides

## 🔧 Platform Integration

### Claude
- Auto-discover from `~/.claude/skills/`
- Use `/use skill-name` command
- Full context integration
- [Setup Guide](./adapters/claude.md)

### Codex (GitHub Copilot)
- Comment references: `// @ai-coding-skills/...`
- Works in VS Code Copilot Chat
- OpenAI API support
- [Setup Guide](./adapters/codex.md)

### OpenCode
- Cloud-based skill management
- Auto-recommendations
- Full IDE integration
- [Setup Guide](./adapters/opencode.md)

### Pi
- Conversational skill references
- Mobile app support
- Rich code generation
- [Setup Guide](./adapters/pi.md)

## 💡 Usage Examples

### Build Go Service
```
/use go-microservices-pro docker-kubernetes-ops testing-strategies-pro

Create production Go service with:
1. Layered architecture
2. gRPC API
3. Docker container
4. K8s manifests
5. Comprehensive tests
```

### Full Stack React App
```
/use frontend-design-pro api-design-patterns testing-strategies-pro

Build React dashboard with:
1. shadcn components + Zustand
2. JWT auth + REST API
3. E2E tests with Playwright
```

### Python REST API
```
/use fastapi-clean-architecture api-design-patterns testing-strategies-pro

FastAPI service with:
1. Clean architecture layers
2. REST design + OAuth
3. pytest unit + integration tests
```

## 📖 Documentation

- **[INTEGRATION.md](./INTEGRATION.md)** - All platform setup guides
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to add skills
- **[LICENSE](./LICENSE)** - MIT
- **[manifest.json](./manifest.json)** - Skill metadata

### Platform Guides
- **[Claude Guide](./adapters/claude.md)** - Claude Code, Claude.ai
- **[Codex Guide](./adapters/codex.md)** - GitHub Copilot, OpenAI
- **[OpenCode Guide](./adapters/opencode.md)** - Anthropic OpenCode
- **[Pi Guide](./adapters/pi.md)** - Pi AI Assistant

## ✨ Features

### Comprehensive Guides
- **50+ detailed .md files**
- **Real-world examples**
- **Best practices & anti-patterns**
- **Multiple languages** (Python, Go, JavaScript)

### Production-Ready
- **Tested patterns**
- **Security included**
- **Performance optimized**
- **Scalability considered**

### Cross-Platform
- **Works with 4 AI assistants**
- **Consistent format**
- **Easy integration**
- **Regular updates**

### Well-Organized
- **Logical structure**
- **Clear navigation**
- **Easy to reference**
- **Skill chaining**

## 🎓 Learning Path

### Beginner
1. Start with skill README
2. Read BASICS guide
3. Try examples
4. Run code locally

### Intermediate
1. Read PATTERNS guide
2. Implement patterns
3. Write tests
4. Deploy with DevOps

### Advanced
1. Study PRODUCTION guide
2. Optimize performance
3. Scale architecture
4. Contribute improvements

## 🔌 Installation

### Option 1: GitHub Clone
```bash
git clone https://github.com/yourname/ai-coding-skills
cd ai-coding-skills
```

### Option 2: NPM Package
```bash
npm install @yourname/ai-coding-skills
```

### Option 3: Symlink (Claude)
```bash
ln -s ~/ai-coding-skills ~/.claude/skills
```

### Option 4: Direct Copy
```bash
cp -r ai-coding-skills ~/.claude/skills
```

## 📊 Statistics

- **11** skills
- **50+** comprehensive guides
- **4** AI platforms supported
- **3** programming languages
- **100%** MIT licensed

## 🤝 Contributing

Want to add a skill or improve guides?

1. Fork repository
2. Create feature branch
3. Add skill/update guides
4. Submit PR

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📋 Manifest

Check `manifest.json` for:
- All skill details
- Guide mappings
- Platform support
- Version info

```json
{
  "version": "1.0.0",
  "skills": [
    {
      "id": "go-microservices-pro",
      "name": "Go Microservices Pro",
      "guides": ["README.md", "ARCHITECTURE_GUIDE.md", ...]
    }
    // ... 11 total
  ]
}
```

## 🆘 Troubleshooting

### Skills not showing?
- Check platform setup guide
- Verify file paths
- Reload/restart app
- Clear cache

### Examples not working?
- Review guide prerequisites
- Check language/framework version
- Test individually
- See platform-specific troubleshooting

## 📞 Support

### Documentation
- Platform-specific guides in `/adapters/`
- Skill README files
- Guide content itself

### Issues
- GitHub issues for bugs
- Discussions for questions
- See CONTRIBUTING.md

### Community
- Share skills you create
- Contribute improvements
- Star if helpful!

## 📄 License

**MIT License** - Free to use, modify, distribute

See [LICENSE](./LICENSE) file.

## 🗺️ Roadmap

### v1.1 (Planned)
- [ ] React Native patterns
- [ ] Kubernetes advanced patterns
- [ ] GraphQL production patterns

### v1.2 (Planned)
- [ ] LLM integration patterns
- [ ] Mobile DevOps
- [ ] Terraform/IaC patterns

### v2.0 (Planned)
- [ ] Interactive examples
- [ ] Video tutorials
- [ ] Community skills marketplace

## 🙏 Acknowledgments

Built for the AI coding assistant ecosystem.

Works with:
- Claude (Anthropic)
- Codex / GitHub Copilot (OpenAI)
- OpenCode (Anthropic)
- Pi (Inflection)

---

**Version**: 1.0.0  
**Updated**: 2024-06-24  
**License**: MIT  

🚀 Start building with AI coding skills!
