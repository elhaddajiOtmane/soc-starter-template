# Penetration Test Findings — [TARGET_DOMAIN]

**Owner:** [OWNER]  
**Tester:** [YOUR_NAME]  
**Date:** [DATE]  
**Authorized:** Yes  

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH     | 0 |
| MEDIUM   | 0 |
| LOW      | 0 |

---

## Findings

> Copy this block for each finding.

---

### [C1] Finding Title

**Severity:** CRITICAL  
**Status:** CONFIRMED  
**Endpoint:** `METHOD /path`  
**MITRE:** T0000 — Technique Name  

**Description:**  
What the vulnerability is and why it exists.

**Evidence:**
```
Paste exact response, header, or error output here
```

**Proof of Concept:**
```bash
curl -X DELETE https://[TARGET_DOMAIN]/login
# Expected: 405 debug page containing APP_KEY
```

**Impact:**  
What an attacker can do with this — be specific.

**Fix:**  
One-line remediation (e.g. "Set APP_DEBUG=false in .env and redeploy").

---

## Extracted Secrets

| Secret | Value | Impact |
|--------|-------|--------|
| | | |

## Test Accounts Created

| Email | Password | Notes |
|-------|----------|-------|
| | | |

## Attack Chain

> Document multi-step exploit chains here.

```
Step 1: [action] → [result]
Step 2: [action] → [result]
Step 3: [action] → [result]
Impact: [what was achieved]
```
