# Mermaid CLI Reference

Rendering, automation, integration.

## Installation

### NPM (Recommended)

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Docker (No Local Install)

```bash
docker run --rm -v /path/to/diagrams:/data minlag/mermaid-cli
```

### Homebrew (macOS)

```bash
brew install mermaid-cli
```

## Basic Commands

### Render to PNG (Default)

```bash
mmdc -i diagram.mmd -o diagram.png
```

### Render to SVG (Vector)

```bash
mmdc -i diagram.mmd -o diagram.svg
```

### Render to PDF (Printing)

```bash
mmdc -i diagram.mmd -o diagram.pdf
```

### Render Multiple Files

```bash
mmdc -i diagrams/*.mmd -o output/
```

## Advanced Options

### Output Format

```bash
# PNG (default)
mmdc -i diagram.mmd -o output.png

# SVG (vector, preferred for documents)
mmdc -i diagram.mmd -o output.svg

# PDF (for printing)
mmdc -i diagram.mmd -o output.pdf

# PNG with scale 2x
mmdc -i diagram.mmd -o output.png -s 2

# PNG with scale 3x (high quality)
mmdc -i diagram.mmd -o output.png -s 3
```

### Theme

```bash
# Default theme
mmdc -i diagram.mmd -o output.png -t default

# Dark theme
mmdc -i diagram.mmd -o output.png -t dark

# Forest theme
mmdc -i diagram.mmd -o output.png -t forest

# Neutral theme
mmdc -i diagram.mmd -o output.png -t neutral
```

### Custom Config

```bash
# With config file
mmdc -i diagram.mmd -o output.png -c config.json

# Config file example:
{
  "theme": "dark",
  "flowchart": {
    "htmlLabels": true,
    "useMaxWidth": true
  },
  "logLevel": "info"
}
```

### Quiet Mode

```bash
# Suppress output
mmdc -i diagram.mmd -o output.png -q

# Verbose logging
mmdc -i diagram.mmd -o output.png --logLevel debug
```

## Batch Processing

### Render All Diagrams

```bash
#!/bin/bash
# render.sh

for file in diagrams/*.mmd; do
    output="output/$(basename "$file" .mmd).png"
    mmdc -i "$file" -o "$output"
    echo "Rendered: $output"
done
```

Usage:
```bash
chmod +x render.sh
./render.sh
```

### Render with Different Themes

```bash
#!/bin/bash
# render-themes.sh

THEMES=("default" "dark" "forest" "neutral")

for theme in "${THEMES[@]}"; do
    mmdc -i diagram.mmd -o "output/diagram-${theme}.png" -t "$theme"
done
```

## Watch Mode (Auto-Render)

```bash
# Re-render on file changes
mmdc -w -i diagrams/*.mmd -o output/
```

## Docker Usage

### Single File

```bash
docker run --rm \
  -v /path/to/diagrams:/data \
  minlag/mermaid-cli \
  -i /data/diagram.mmd -o /data/diagram.png
```

### Batch Process

```bash
docker run --rm \
  -v /path/to/diagrams:/data \
  minlag/mermaid-cli \
  /data/*.mmd -o /data/output/
```

## GitHub Actions Integration

### Auto-Render on Push

```yaml
# .github/workflows/render-diagrams.yml
name: Render Diagrams

on:
  push:
    paths:
      - '**.mmd'

jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Mermaid CLI
        run: npm install -g @mermaid-js/mermaid-cli
      
      - name: Render Diagrams
        run: mmdc -i diagrams/*.mmd -o docs/diagrams/
      
      - name: Commit Changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/diagrams/
          git commit -m "Auto-render diagrams" || true
          git push
```

## Validation

### Check Syntax

```bash
# Render with validation
mmdc -i diagram.mmd -o /dev/null

# Verbose output
mmdc -i diagram.mmd -o /dev/null --logLevel debug
```

### Validate Multiple Files

```bash
#!/bin/bash
# validate.sh

for file in diagrams/*.mmd; do
    if mmdc -i "$file" -o /dev/null 2>/dev/null; then
        echo "✓ $file"
    else
        echo "✗ $file"
    fi
done
```

## Performance Optimization

### High Quality Rendering

```bash
# Scale 2x for retina displays
mmdc -i diagram.mmd -o diagram.png -s 2

# SVG for documents (no scaling needed)
mmdc -i diagram.mmd -o diagram.svg
```

### Optimize Large Diagrams

```bash
# Custom config for performance
{
  "flowchart": {
    "htmlLabels": false,
    "useMaxWidth": true
  },
  "sequence": {
    "messageAlign": "left"
  }
}

mmdc -i large-diagram.mmd -o output.png -c optimize.json
```

## Integration Examples

### GitLab CI

```yaml
# .gitlab-ci.yml
render-diagrams:
  stage: build
  image: node:18
  script:
    - npm install -g @mermaid-js/mermaid-cli
    - mmdc -i diagrams/*.mmd -o public/diagrams/
  artifacts:
    paths:
      - public/diagrams/
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Render Diagrams') {
            steps {
                sh 'npm install -g @mermaid-js/mermaid-cli'
                sh 'mmdc -i diagrams/*.mmd -o docs/diagrams/'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'docs/diagrams/**'
        }
    }
}
```

### Make Target

```makefile
# Makefile

.PHONY: diagrams
diagrams:
	mmdc -i diagrams/*.mmd -o docs/diagrams/

.PHONY: watch-diagrams
watch-diagrams:
	mmdc -w -i diagrams/*.mmd -o docs/diagrams/

.PHONY: clean-diagrams
clean-diagrams:
	rm -rf docs/diagrams/*.png

.PHONY: diagrams-hq
diagrams-hq:
	mmdc -i diagrams/*.mmd -o docs/diagrams/ -s 2
```

Usage:
```bash
make diagrams          # Render all
make watch-diagrams    # Auto-render on change
make diagrams-hq       # High quality
```

## Troubleshooting

### Port Already in Use

```bash
# Change port if needed (for server mode)
mmdc --port 8080 --host 0.0.0.0
```

### Memory Issues (Large Diagrams)

```bash
# Increase Node memory
NODE_OPTIONS=--max-old-space-size=4096 mmdc -i large.mmd -o output.png
```

### SVG Rendering Issues

```bash
# Use default theme for SVG
mmdc -i diagram.mmd -o output.svg -t default
```

## Quick Scripts

### Auto-generate Index

```bash
#!/bin/bash
# generate-index.sh

echo "# Diagrams" > README.md
echo "" >> README.md

for file in diagrams/*.mmd; do
    base=$(basename "$file" .mmd)
    echo "## $base" >> README.md
    echo "![${base}](output/${base}.png)" >> README.md
    echo "" >> README.md
done
```

### Validate & Render

```bash
#!/bin/bash
# validate-and-render.sh

FAILED=0

for file in diagrams/*.mmd; do
    echo "Processing: $file"
    if mmdc -i "$file" -o "output/$(basename "$file" .mmd).png" 2>&1; then
        echo "✓ Success"
    else
        echo "✗ Failed"
        FAILED=$((FAILED + 1))
    fi
done

if [ $FAILED -gt 0 ]; then
    echo "$FAILED diagram(s) failed"
    exit 1
fi

echo "All diagrams rendered successfully"
```

## Help & Documentation

```bash
# Show help
mmdc --help

# Check version
mmdc --version

# Online editor
https://mermaid.live

# Official docs
https://mermaid.js.org
```

## Tips

1. **Use SVG for documents** — Better quality, scalable
2. **Use PNG for web** — Smaller file size
3. **Watch mode for development** — Auto-renders on save
4. **High quality rendering** — Use `-s 2` or `-s 3`
5. **Version control .mmd files** — Not images
6. **Generate images in CI/CD** — Keep DRY principle
7. **Test locally first** — Before committing
