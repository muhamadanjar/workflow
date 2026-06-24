# Contributing Guide

Contributions welcome! Help expand AI Coding Skills for all platforms.

## Getting Started

### Fork & Clone
```bash
git clone https://github.com/yourname/ai-coding-skills
cd ai-coding-skills
```

### Skill Directory Structure
```
skill-name/
├── README.md              # Overview (required)
├── GUIDE_1.md            # Detailed guides
├── GUIDE_2.md
├── GUIDE_N.md
├── skill.yaml            # Metadata (required)
└── templates/            # Optional code examples
    └── example.go
```

## Creating a New Skill

### Step 1: Create Folder
```bash
mkdir my-new-skill
cd my-new-skill
```

### Step 2: Write README.md
```markdown
# My New Skill

Brief description of what this skill covers.

## Topics
- Topic 1
- Topic 2
- Topic 3

## Quick Start
See guides:
- `GUIDE_1.md` - Description

## Use This When
When to use this skill
```

### Step 3: Write Guides
Create detailed `.md` files for each guide:
- `BASICS.md` - Fundamentals
- `PATTERNS.md` - Common patterns
- `PRODUCTION.md` - Production practices
- etc.

**Guide Structure:**
```markdown
# Guide Title

## Core Concept
Explanation

## Example
Code examples

## Best Practices
- Practice 1
- Practice 2

## Anti-Patterns
- Bad 1
- Bad 2
```

### Step 4: Create skill.yaml
```yaml
id: my-new-skill
name: "My New Skill"
version: "1.0.0"
description: "Full description of skill"
category: "backend"  # or frontend/devops/testing/documentation
tags: ["tag1", "tag2"]
author: "Your Name"
license: "MIT"
platforms: ["claude", "codex", "opencode", "pi"]
guides:
  - README.md
  - GUIDE_1.md
  - GUIDE_2.md
keywords: ["keyword1", "keyword2"]
```

### Step 5: Update manifest.json
Add to `manifest.json`:
```json
{
  "id": "my-new-skill",
  "name": "My New Skill",
  "version": "1.0.0",
  "description": "...",
  "category": "backend",
  "tags": ["tag1", "tag2"],
  "guides": ["README.md", "GUIDE_1.md"],
  "platforms": ["claude", "codex", "opencode", "pi"]
}
```

## Guidelines

### Content Quality
- ✅ Clear, concise writing
- ✅ Code examples work
- ✅ Real-world applicable
- ✅ Up-to-date info
- ✅ All platforms considered

### Code Examples
- Language-specific sections
- Executable examples
- Error handling shown
- Comments explain why
- Link to full code

### Structure
- Logical progression
- Clear headings
- Table of contents
- Cross-references
- Troubleshooting section

### Testing
- Code examples tested
- Edge cases covered
- Performance notes
- Security considerations
- Version compatibility

## Submitting Changes

### Before PR
```bash
# Validate manifest
python scripts/validate_manifest.py

# Check formatting
npm run lint

# Review guides
grep -r "TODO\|FIXME" .
```

### Create PR
```bash
git add .
git commit -m "Add new skill: my-new-skill"
git push origin feature/my-new-skill
```

**PR Title:** `Add: my-new-skill` or `Update: existing-skill`

**PR Description:**
```
## Summary
Brief overview of changes

## Changes
- Added new skill X
- Updated guide Y
- Fixed issue Z

## Testing
Tested with:
- Claude ✓
- Codex ✓
- OpenCode ✓
- Pi ✓

## Checklist
- [ ] Manifest.json valid
- [ ] All guides proofread
- [ ] Code examples tested
- [ ] Skill.yaml complete
- [ ] README.md written
- [ ] License included
```

## Enhancement Ideas

### Looking for Contributions

- New skill: `skill-category-feature`
- Guide expansion: More examples, edge cases
- Code examples: Different languages
- Documentation: Better explanations
- Platform support: Better integration

### High Priority
- React Native patterns
- Kubernetes advanced patterns
- GraphQL production patterns
- LLM integration patterns
- Mobile DevOps

## Code Review

Reviews check for:
- **Content**: Accurate, helpful, current
- **Examples**: Working, realistic code
- **Structure**: Clear organization
- **Format**: Consistent with others
- **Platforms**: Works across all
- **Completeness**: No TODOs

## Maintenance

### Monthly
- Check for outdated info
- Verify code examples still work
- Update version numbers
- Add new patterns discovered

### Quarterly
- Review user feedback
- Add missing topics
- Improve documentation
- Test all platforms

## Licensing

All contributions must use MIT License.

Include license header in new files:
```
/*
Copyright (c) 2024 AI Coding Skills Contributors
MIT License - See LICENSE file
*/
```

## Community

### Questions?
- Open discussion issue
- Ask in PRs
- Email maintainers

### Ideas?
- Create feature request
- Propose in discussions
- Tag with `enhancement`

### Issues?
- Report with minimal example
- Include platform/version
- Tag with `bug`

## Recognition

Contributors listed in:
- CONTRIBUTORS.md
- GitHub contributors
- Skill author field

## Code of Conduct

Be respectful, inclusive, helpful.

Report issues to: `conduct@example.com`

## Resources

### Templates
- `templates/skill-template/` - Copy to start
- Guides use GitHub Flavored Markdown
- Examples in multiple languages

### Tools
```bash
# Validate YAML
yamllint skill.yaml

# Check links
markdown-link-check *.md

# Format
prettier --write "**/*.md"
```

### Documentation
- [Markdown Guide](https://commonmark.org/)
- [YAML Spec](https://yaml.org/)
- [Platform Guides](./adapters/)

## Changelog

Maintain CHANGELOG.md:
```markdown
## [1.1.0] - 2024-06-25
### Added
- New skill: X
- Guide: Y

### Fixed
- Bug in Z

### Changed
- Updated approach for W
```

## Questions?

1. Check existing skills
2. Review INTEGRATION.md
3. Open discussion
4. Ask maintainer

Thanks for contributing! 🙏

Version: 1.0.0
Last Updated: 2024-06-24
