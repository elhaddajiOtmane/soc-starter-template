# Engagement Scope

## Authorization
- **Owner:** [OWNER]
- **Target:** [TARGET_DOMAIN]
- **Origin IP:** [ORIGIN_IP]
- **Stack:** [STACK]
- **Started:** [DATE]
- **Authorized:** YES — this is my application / I have written permission

## In Scope
- [e.g. https://[TARGET_DOMAIN] — all endpoints]
- [e.g. API at https://api.[TARGET_DOMAIN]]

## Out of Scope
- [e.g. third-party CDN provider]
- [e.g. email infrastructure]
- [e.g. other tenants / shared hosting neighbors]

## Test Accounts
| Email | Password | Role |
|-------|----------|------|
| probe_*@mailinator.com | Pa$$w0rd!Probe1 | regular user |

## Known Secrets
| Secret | Value | Source |
|--------|-------|--------|
| [e.g. APP_KEY] | [value] | [e.g. debug page leak] |

## Key Script Rules
- `allow_redirects=False` on ALL requests
- Fresh `requests.Session()` per attempt
- GET page → extract CSRF token → POST (never skip GET step)
- API endpoints may need Bearer token, not session cookie
