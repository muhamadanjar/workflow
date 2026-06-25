#!/usr/bin/env python3
"""Generate skill.md files from manifest.json for all skills."""

import json
import os
from pathlib import Path


def load_manifest():
    """Load manifest.json."""
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path) as f:
        return json.load(f)


def generate_guides_list(guides):
    """Format guides as markdown list."""
    return "\n".join(f"- {guide}" for guide in guides)


def generate_tags(tags):
    """Format tags."""
    return f"[{', '.join(tags)}]"


def generate_platforms(platforms):
    """Format platforms."""
    return f"[{', '.join(platforms)}]"


def generate_skill_md(skill):
    """Generate skill.md content from skill metadata."""
    template_path = Path(__file__).parent / ".skill.template.md"
    with open(template_path) as f:
        template = f.read()

    guides_list = generate_guides_list(skill.get("guides", []))
    tags = generate_tags(skill.get("tags", []))
    platforms = generate_platforms(skill.get("platforms", []))

    content = template
    content = content.replace("{{ID}}", skill["id"])
    content = content.replace("{{NAME}}", skill["name"])
    content = content.replace("{{VERSION}}", skill.get("version", "1.0.0"))
    content = content.replace("{{DESCRIPTION}}", skill["description"])
    content = content.replace("{{CATEGORY}}", skill.get("category", "general"))
    content = content.replace("{{TAGS}}", tags)
    content = content.replace("{{PLATFORMS}}", platforms)
    content = content.replace("{{GUIDES_LIST}}", guides_list)

    return content


def main():
    """Generate skill.md for all skills in manifest."""
    manifest = load_manifest()
    skills_dir = Path(__file__).parent

    generated = []
    skipped = []

    for skill in manifest.get("skills", []):
        skill_id = skill["id"]
        skill_path = skills_dir / skill_id

        # Skip symlinks (external skills)
        if skill_path.is_symlink():
            skipped.append(f"{skill_id} (symlink)")
            continue

        # Skip if folder doesn't exist
        if not skill_path.exists():
            skipped.append(f"{skill_id} (no folder)")
            continue

        # Generate skill.md
        content = generate_skill_md(skill)
        skill_md_path = skill_path / "skill.md"

        with open(skill_md_path, "w") as f:
            f.write(content)

        generated.append(skill_id)
        print(f"✓ {skill_id}")

    print(f"\n✅ Generated: {len(generated)} skill.md files")
    if skipped:
        print(f"⏭️  Skipped: {len(skipped)}")
        for item in skipped:
            print(f"   - {item}")


if __name__ == "__main__":
    main()
