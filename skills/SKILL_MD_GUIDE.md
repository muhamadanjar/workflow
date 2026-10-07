# Skill.md Format Guide

## Overview

Each skill now includes a `skill.md` file for standardized discovery and loading across platforms (Claude, Pi, Codex, OpenCode).

## Structure

```
skills/
├── python-async-pro/
│   ├── skill.md           ← Platform-agnostic skill definition
│   ├── README.md
│   ├── GUIDE.md
│   └── claude.md          ← (Legacy platform-specific)
├── go-microservices-pro/
│   ├── skill.md
│   └── ...
```

## Skill.md Format

### Frontmatter

```yaml
---
id: skill-id
name: Skill Display Name
version: 1.0.0
description: One-line skill description
category: backend|frontend|devops|testing|documentation|infrastructure|data-science
tags: [tag1, tag2, tag3]
platforms: [claude, codex, opencode, pi]
---
```

### Content Sections

1. **Title** - Skill name
2. **Overview** - What this skill covers
3. **Guides** - List of markdown files in skill directory
4. **Quick Start** - Basic usage across platforms
5. **Features** - Key capabilities
6. **Usage with Platforms** - Platform-specific examples
7. **Integration Points** - Works well with other skills
8. **Resources** - Where to find more info

## Platform Usage

### Claude Code
```
I need async patterns.
Use @python-async-pro for:
- asyncio best practices
- Concurrent execution patterns
```

### Pi
```
@python-async-pro

Show me async programming patterns
```

### With Multiple Skills
```
@python-async-pro @testing-strategies-pro

Create async code with tests
```

## Generation & Updates

### Auto-Generate from manifest.json
```bash
cd skills/
python3 generate-skill-md.py
```

Regenerates all skill.md files from manifest.json metadata.

### Edit skill.md Directly
Edit individual skill.md files for:
- Enhanced descriptions
- Better usage examples
- Platform-specific guidance

**Template**: `.skill.template.md`

## Integration

### For Claude Code
- Platforms detect skill.md
- Reference format: `@skill-id`
- Specific guide: `@skill-id/GUIDE_NAME.md`

### For Pi
- Reads skill.md from manifest
- Uses metadata for discovery
- Guides listed in skill.md

### For Codex / OpenCode
- Reference in context
- Uses guide list for suggestions

## Best Practices

### skill.md Content
✅ Keep descriptions concise  
✅ Link to guides clearly  
✅ Show platform-specific examples  
✅ List compatible skills  

❌ Duplicate manifest.json info  
❌ Long prose in overview  
❌ Platform-specific setup instructions (use platform-specific files)  

### Updating Skills
1. Edit skill folder guides/content
2. Update manifest.json if metadata changes
3. Run `generate-skill-md.py` to refresh
4. Or manually edit skill.md for enhancements

## File Inventory

Generated files:
- ✅ python-async-pro
- ✅ fastapi-clean-architecture
- ✅ frontend-design-pro
- ✅ pubsub-messaging
- ✅ mermaid-diagrams
- ✅ redis-caching
- ✅ database-design
- ✅ go-microservices-pro
- ✅ docker-kubernetes-ops
- ✅ api-design
- ✅ testing-strategies-pro
- ✅ object-storage-patterns
- ✅ data-manipulation-pandas
- ✅ geospatial-analytics
- ✅ task-queues-jobs
- ✅ monitoring-observability
- ✅ websockets-realtime

## References

- `manifest.json` - Source of truth for skill metadata
- `.skill.template.md` - Template for generation
- `generate-skill-md.py` - Generation script
- Individual `skill.md` files - Platform-compatible skill definitions
