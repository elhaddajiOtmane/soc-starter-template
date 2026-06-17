# SOC Project — Agent Context Map

## Overview

Security Operations Center (SOC) assessment for **[TARGET_DOMAIN]** — a [STACK] web
application owned by [OWNER]. All testing is **authorized**.

> FILL IN: Replace every `[PLACEHOLDER]` before starting. Delete this line when done.

## Authorization

| Field | Value |
|-------|-------|
| Owner | [OWNER] |
| Target domain | [TARGET_DOMAIN] |
| Origin IP | [ORIGIN_IP — check ACAO header or DNS] |
| Test started | [DATE] |
| Scope | [e.g. web app only / API / infrastructure] |
| Out of scope | [e.g. third-party CDN / email servers] |

## Repository Structure

```
[project-root]/
├── AGENTS.md                         # This file — agent context map
├── opencode.json                     # Project-level OpenCode config
├── .claude/
│   └── CLAUDE.md                     # Master context for Claude sessions
├── targets/
│   └── [TARGET_DOMAIN]/
│       ├── probes/                   # Active Python probe scripts
│       ├── captures/                 # Network captures (HAR, PCAP)
│       └── reports/
│           ├── findings.md           # Detailed findings log
│           └── todo.md               # Open items / next session focus
├── tools/
│   ├── probe_template.py             # Generic HTTP probe (CSRF-aware, threaded)
│   └── probe_report.py              # Daily Discord stats reporter
└── remediation/                      # Hardening configs / patches
    ├── nginx/
    ├── app/
    └── deploy.sh
```

## Vulnerability Register

> Update STATUS as you confirm/rule out each finding.
> Statuses: CONFIRMED | UNCONFIRMED | NOT VULNERABLE | IN PROGRESS

### CRITICAL

| # | Issue | Endpoint | Status | Notes |
|---|-------|----------|--------|-------|
| C1 | Debug mode enabled — full stack traces + secrets | Any error route | | |
| C2 | Secret key / API key leaked in debug output | [endpoint] | | |
| C3 | Session exhaustion — stateless GET creates server-side session | [endpoint] | | |
| C4 | Auth token / APP_KEY / JWT secret extracted | [method] | | |
| C5 | RCE via SSTI / deserialization / command injection | [endpoint] | | |

### HIGH

| # | Issue | Endpoint | Status | Notes |
|---|-------|----------|--------|-------|
| H1 | No rate limit on authentication endpoint | [endpoint] | | |
| H2 | XFF / IP header throttle bypass | All | | |
| H3 | Mass assignment — extra fields accepted on register/update | [endpoint] | | |
| H4 | No email verification — accounts active immediately | [endpoint] | | |
| H5 | No CAPTCHA on login / register / password reset | All forms | | |
| H6 | Credential stuffing — unlimited login attempts | [endpoint] | | |
| H7 | Password reset flood — no rate limit | [endpoint] | | |
| H8 | IDOR — access other users' data by ID | [endpoint] | | |
| H9 | Broken authentication — JWT none algorithm / weak signing | [endpoint] | | |
| H10 | SQLi — unsanitized input in query | [endpoint] | | |

### MEDIUM

| # | Issue | Endpoint | Status | Notes |
|---|-------|----------|--------|-------|
| M1 | Origin IP leaked in CORS / ACAO header — CDN bypass | All | | |
| M2 | Sensitive data in URL params / GET request | [endpoint] | | |
| M3 | Missing security headers (CSP, HSTS, X-Frame-Options) | All | | |
| M4 | Open redirect | [endpoint] | | |
| M5 | Reflected XSS | [endpoint] | | |
| M6 | Stored XSS | [endpoint] | | |
| M7 | CSRF — state-changing request without token | [endpoint] | | |

### LOW / INFO

| # | Issue | Endpoint | Status | Notes |
|---|-------|----------|--------|-------|
| L1 | Duplicate security headers (web server + framework both set) | All | | |
| L2 | Server version disclosed in headers | All | | |
| L3 | Directory listing enabled | [path] | | |
| L4 | Verbose error messages in production | All | | |

## Extracted Secrets

> Fill in as you discover them. Keep this section updated each session.

| Secret | Value | How Obtained | Impact |
|--------|-------|--------------|--------|
| [e.g. APP_KEY / JWT_SECRET] | [value] | [e.g. debug page, git leak] | [e.g. forge sessions] |

## Test Accounts

| Email | Password | Notes |
|-------|----------|-------|
| [account]@mailinator.com | [password] | [role/purpose] |

## Technology Stack

| Component | Value |
|-----------|-------|
| Framework | [e.g. Laravel, Rails, Django, Express] |
| Server | [e.g. nginx, Apache] |
| OS | [e.g. Ubuntu 22.04] |
| Session | [e.g. file-based, cookie, Redis] |
| Auth | [e.g. session cookies, JWT, Sanctum Bearer] |
| Database | [e.g. MySQL, Postgres] |
| CDN / WAF | [e.g. Cloudflare, none] |

## Open Questions

> Replace with actual questions as you discover them. One question = one follow-up script.

1. Does mass assignment store extra fields in DB?
2. Does a Bearer token / API auth endpoint exist?
3. Is SSTI payload rendered on any page after storing in name/bio field?
4. Can extracted secret key be used to forge a session for user_id=1?

## Script Rules

**Critical — violating these breaks scripts.**

- `allow_redirects=False` on ALL requests — many apps redirect auth users to a different domain
- Always GET the page first to extract CSRF token before any POST
- Use a fresh `requests.Session()` per attempt — never reuse sessions across threads
- API endpoints often need Bearer token auth, not session cookies — test both
- Run probes from the `targets/[TARGET]/probes/` directory or set TARGET as absolute URL

## Known Routes

> Fill in as you map the app. Use `probe_template.py` or Caido to discover routes.

| Path | Method | Auth | Notes |
|------|--------|------|-------|
| / | GET | No | |
| /login | GET/POST | No | |
| /register | GET/POST | No | |
| /dashboard | GET | Yes | |
| /api/user | GET | Bearer | |
| /password/reset | GET/POST | No | |
| /admin | GET | Yes | Check if exists |

## What NOT to Re-test

> Update this list across sessions to avoid wasted time.

- [endpoint] → [reason it was ruled out]

## MITRE ATT&CK Mapping

| TTP | Technique | Finding |
|-----|-----------|---------|
| T1078 | Valid Accounts | Credential stuffing / mass account creation |
| T1190 | Exploit Public-Facing Application | Any RCE / auth bypass |
| T1552.001 | Credentials in Files | Secret key leaked in debug output |
| T1082 | System Information Discovery | Debug stack traces / server path disclosure |
| T1562.001 | Disable/Modify Security Tools | XFF throttle bypass |
| T1136.001 | Create Account | Mass registration / mass assignment admin |
