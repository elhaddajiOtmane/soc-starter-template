# Live Findings — [TARGET_DOMAIN]

> This file is the compact, session-ready version of findings.
> Full details → targets/[TARGET]/reports/findings.md
> Update this file every session. OpenCode loads it as context automatically.

## Confirmed Vulnerabilities

| ID | Severity | Finding | Endpoint | MITRE |
|----|----------|---------|----------|-------|
| C1 | CRITICAL | | | |
| H1 | HIGH     | | | |
| M1 | MEDIUM   | | | |

## Unconfirmed (need verification)

| ID | Severity | Finding | Endpoint | Next Step |
|----|----------|---------|----------|-----------|
| | | | | |

## Ruled Out

| Finding | Reason |
|---------|--------|
| SQLi | PDO prepared statements — clean |
| Stored XSS | Not reflected on any page we can read |

## Current Attack Chain Status

```
[describe multi-step chain progress here]
e.g:
Step 1: DONE — extracted APP_KEY via debug page
Step 2: DONE — created 150k accounts, 0 rate limiting
Step 3: TODO — forge session cookie for user_id=1
Step 4: TODO — verify is_admin field stored in DB
```

## Open Questions (next session priority)

1. [question] → run [script]
2. [question] → run [script]
