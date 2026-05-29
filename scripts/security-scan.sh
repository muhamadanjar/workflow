#!/usr/bin/env bash
# Security scanner — runs appropriate tools per detected stack
# Usage: bash ~/.claude/scripts/security-scan.sh [project_dir]

set -euo pipefail

DIR="${1:-.}"
REPORT_DIR="${DIR}/.security-audit"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${REPORT_DIR}/report_${TIMESTAMP}.txt"

mkdir -p "${REPORT_DIR}"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "${REPORT_FILE}"; }
section() { echo -e "\n========== $* ==========" | tee -a "${REPORT_FILE}"; }
check_tool() { command -v "$1" >/dev/null 2>&1; }

cd "${DIR}"

section "SECURITY AUDIT STARTED"
log "Project: $(pwd)"
log "Date: $(date)"

# ── Stack Detection ──────────────────────────────────────────────
section "STACK DETECTION"
STACKS=()
[[ -f "requirements.txt" || -f "pyproject.toml" || -f "Pipfile" ]] && STACKS+=("python") && log "✓ Python detected"
[[ -f "package.json" ]] && STACKS+=("node") && log "✓ Node/JS detected"
[[ -f "composer.json" ]] && STACKS+=("php") && log "✓ PHP/Laravel detected"
[[ -f "go.mod" ]] && STACKS+=("go") && log "✓ Go detected"
[[ -f "Cargo.toml" ]] && STACKS+=("rust") && log "✓ Rust detected"
[[ -f "Gemfile" ]] && STACKS+=("ruby") && log "✓ Ruby detected"
[[ -f "pom.xml" || -f "build.gradle" ]] && STACKS+=("java") && log "✓ Java detected"
[[ -f "Dockerfile" || -f "docker-compose.yml" ]] && STACKS+=("docker") && log "✓ Docker detected"
[[ ${#STACKS[@]} -eq 0 ]] && log "⚠ No recognized stack found" && exit 0

# ── Tool Availability ────────────────────────────────────────────
section "AVAILABLE TOOLS"
TOOLS_FOUND=()
for t in bandit safety pip-audit semgrep gosec trivy grype govulncheck cargo-audit bundler-audit; do
  check_tool "$t" && TOOLS_FOUND+=("$t") && log "✓ $t" || log "✗ $t (not installed)"
done

# ── Dependency Scans ─────────────────────────────────────────────
section "DEPENDENCY CVE SCANS"

if [[ " ${STACKS[*]} " =~ " python " ]]; then
  log "--- Python ---"
  if check_tool pip-audit; then
    pip-audit --format json 2>/dev/null | python3 -c "
import json,sys
data=json.load(sys.stdin)
vulns=data.get('dependencies',[]) if isinstance(data,dict) else data
for d in vulns:
  for v in d.get('vulns',[]):
    print(f\"  [CVE] {d.get('name')} {d.get('version')} — {v.get('id')} ({v.get('fix_versions',[])})\")
" 2>/dev/null | tee -a "${REPORT_FILE}" || log "pip-audit scan failed"
  elif check_tool safety; then
    safety check --json 2>/dev/null | tee -a "${REPORT_FILE}" || log "safety scan failed"
  else
    log "⚠ No Python dep scanner. Run: pip install pip-audit"
  fi
fi

if [[ " ${STACKS[*]} " =~ " node " ]]; then
  log "--- Node/NPM ---"
  npm audit --json 2>/dev/null | python3 -c "
import json,sys
try:
  data=json.load(sys.stdin)
  vulns=data.get('vulnerabilities',{})
  for name,v in vulns.items():
    sev=v.get('severity','?')
    via=[x.get('source','?') if isinstance(x,dict) else str(x) for x in v.get('via',[])]
    print(f'  [{sev.upper()}] {name} via {via}')
except: print('  (parse error — run npm audit manually)')
" 2>/dev/null | tee -a "${REPORT_FILE}" || log "npm audit failed"
fi

if [[ " ${STACKS[*]} " =~ " php " ]]; then
  log "--- PHP/Composer ---"
  if check_tool composer; then
    composer audit --format=json 2>/dev/null | python3 -c "
import json,sys
try:
  data=json.load(sys.stdin)
  for pkg,info in data.get('advisories',{}).items():
    for a in info:
      print(f\"  [CVE] {pkg} — {a.get('advisoryId','?')} {a.get('title','?')}\")
except: print('  (no advisories or parse error)')
" 2>/dev/null | tee -a "${REPORT_FILE}" || log "composer audit failed"
  else
    log "⚠ composer not installed"
  fi
fi

if [[ " ${STACKS[*]} " =~ " go " ]]; then
  log "--- Go ---"
  if check_tool govulncheck; then
    govulncheck ./... 2>&1 | grep -E "^vuln|^Vulnerability|^pkg|^Found" | tee -a "${REPORT_FILE}" || true
  else
    log "⚠ govulncheck not installed. Run: go install golang.org/x/vuln/cmd/govulncheck@latest"
  fi
fi

if [[ " ${STACKS[*]} " =~ " rust " ]]; then
  log "--- Rust ---"
  if check_tool cargo; then
    cargo audit 2>&1 | grep -E "error|warning|Crate|Version|Advisory|RUSTSEC" | tee -a "${REPORT_FILE}" || true
  fi
fi

if [[ " ${STACKS[*]} " =~ " ruby " ]]; then
  log "--- Ruby ---"
  if check_tool bundle; then
    bundle exec bundle-audit check --update 2>&1 | tee -a "${REPORT_FILE}" || true
  fi
fi

# Universal: trivy or semgrep
section "UNIVERSAL SCANNERS"
if check_tool trivy; then
  log "Running trivy fs scan..."
  trivy fs --scanners vuln,secret --format table . 2>/dev/null | tee -a "${REPORT_FILE}" || true
elif check_tool semgrep; then
  log "Running semgrep..."
  semgrep --config=auto --no-rewrite-rule-ids . 2>/dev/null | tail -50 | tee -a "${REPORT_FILE}" || true
else
  log "⚠ trivy and semgrep not installed — manual code scan only"
  log "Install trivy: https://aquasecurity.github.io/trivy/"
  log "Install semgrep: pip install semgrep"
fi

# ── Secrets Scan ─────────────────────────────────────────────────
section "SECRETS SCAN"
EXCLUDE_DIRS="-not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*'"

log "Scanning for hardcoded credentials..."

# AWS keys
FOUND=$(eval "find . -type f $EXCLUDE_DIRS" | xargs grep -l "AKIA[0-9A-Z]\{16\}" 2>/dev/null || true)
[[ -n "$FOUND" ]] && log "  [CRITICAL] AWS Access Key pattern found in: $FOUND" || log "  ✓ No AWS keys"

# Private keys
FOUND=$(eval "find . -type f $EXCLUDE_DIRS" | xargs grep -l "BEGIN.*PRIVATE KEY" 2>/dev/null || true)
[[ -n "$FOUND" ]] && log "  [CRITICAL] Private key found in: $FOUND" || log "  ✓ No private keys"

# Hardcoded passwords (not from env)
FOUND=$(eval "find . -type f \( -name '*.py' -o -name '*.php' -o -name '*.go' -o -name '*.js' -o -name '*.ts' -o -name '*.rb' \) $EXCLUDE_DIRS" | \
  xargs grep -n "password\s*=\s*['\"][^'\"]\{3,\}['\"]" 2>/dev/null | \
  grep -iv "test\|example\|dummy\|placeholder\|os\.getenv\|process\.env\|config\." || true)
[[ -n "$FOUND" ]] && echo "  [HIGH] Possible hardcoded password:" && echo "$FOUND" | head -10 | tee -a "${REPORT_FILE}" || log "  ✓ No obvious hardcoded passwords"

# Committed .env files
FOUND=$(find . -name ".env" -not -path "*/.git/*" -not -name ".env.example" -not -name ".env.sample" 2>/dev/null || true)
[[ -n "$FOUND" ]] && log "  [HIGH] .env files found (should not be committed): $FOUND" || log "  ✓ No committed .env files"

# ── Auth & Config Issues ─────────────────────────────────────────
section "AUTH & CONFIG ISSUES"

# Debug mode
FOUND=$(eval "find . -type f \( -name '*.py' -o -name '*.php' -o -name '*.env' \) $EXCLUDE_DIRS" | \
  xargs grep -n "DEBUG\s*=\s*True\|APP_DEBUG\s*=\s*true" 2>/dev/null | \
  grep -v "#\|test" || true)
[[ -n "$FOUND" ]] && echo "  [HIGH] Debug mode enabled:" && echo "$FOUND" | tee -a "${REPORT_FILE}" || log "  ✓ No debug mode issues"

# CORS wildcard
FOUND=$(eval "find . -type f $EXCLUDE_DIRS" | \
  xargs grep -n "Access-Control-Allow-Origin.*\*" 2>/dev/null | \
  grep -v "#\|test" || true)
[[ -n "$FOUND" ]] && echo "  [MEDIUM] CORS wildcard:" && echo "$FOUND" | head -5 | tee -a "${REPORT_FILE}" || log "  ✓ No CORS wildcard"

# MD5/SHA1 for passwords
FOUND=$(eval "find . -type f \( -name '*.py' -o -name '*.php' -o -name '*.go' -o -name '*.rb' \) $EXCLUDE_DIRS" | \
  xargs grep -n "md5\|sha1" 2>/dev/null | \
  grep -i "password\|hash\|passwd" | grep -v "test\|#" || true)
[[ -n "$FOUND" ]] && echo "  [HIGH] Weak password hashing (MD5/SHA1):" && echo "$FOUND" | head -5 | tee -a "${REPORT_FILE}" || log "  ✓ No weak password hashing detected"

# Docker issues
if [[ " ${STACKS[*]} " =~ " docker " ]]; then
  FOUND=$(grep -n "FROM.*:latest" Dockerfile* 2>/dev/null || true)
  [[ -n "$FOUND" ]] && echo "  [LOW] Docker :latest tags:" && echo "$FOUND" | tee -a "${REPORT_FILE}" || log "  ✓ No :latest Docker tags"

  FOUND=$(grep -n "USER root" Dockerfile* docker-compose* 2>/dev/null || true)
  [[ -n "$FOUND" ]] && echo "  [HIGH] Docker running as root:" && echo "$FOUND" | tee -a "${REPORT_FILE}" || log "  ✓ No Docker root user"
fi

# ── Summary ──────────────────────────────────────────────────────
section "AUDIT COMPLETE"
log "Full report saved: ${REPORT_FILE}"
log "For deeper analysis, run this project directory through the security-auditor Claude agent."
