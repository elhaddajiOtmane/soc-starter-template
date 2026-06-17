# SOC Starter Template — Quick Start

## 1. Copy this folder to your new project

```
cp -r template/ ~/projects/soc-[target]/
cd ~/projects/soc-[target]/
```

## 2. Fill in every [PLACEHOLDER]

Search for `[` in all files and replace:

| Placeholder | Replace with |
|-------------|-------------|
| `[TARGET_DOMAIN]` | e.g. `target.com` |
| `[OWNER]` | Your name / company |
| `[STACK]` | e.g. `Laravel + nginx` |
| `[ORIGIN_IP]` | Check ACAO header: `curl -I https://target.com` |
| `[DATE]` | Today's date |
| `[SCOPE]` | e.g. `web app only` |
| `[EC2_HOST]` | e.g. `ec2-1-2-3-4.compute-1.amazonaws.com` |
| `[EC2_USER]` | e.g. `ubuntu` |
| `[KEY]` | e.g. `~/.ssh/mykey.pem` |
| `[SERVICE_NAME]` | e.g. `myapp-probe` |
| `[WEBHOOK_ID]` and `[WEBHOOK_TOKEN]` | From Discord channel settings |

## 3. Install Claude Code context (automatic)

Claude Code reads `.claude/CLAUDE.md` automatically when you open the project.
No extra steps needed.

## 4. Install OpenCode context

```json
// opencode.json is already in the root — OpenCode loads it automatically.
// Update the "instructions" array if you add more context files.
```

## 5. Start a probe

```bash
cp targets/TARGET/probes/probe_template.py targets/[target]/probes/[attack]-probe.py
# Edit TARGET and module, then:
python -X utf8 targets/[target]/probes/[attack]-probe.py --module register -n 10
```

## 6. Deploy probe to EC2 with auto-restart

```bash
# Upload probe
scp -i ~/.ssh/[KEY].pem targets/[target]/probes/probe.py ubuntu@[EC2_HOST]:~/

# Create systemd service on the server
ssh -i ~/.ssh/[KEY].pem ubuntu@[EC2_HOST] "
sudo tee /etc/systemd/system/[SERVICE_NAME].service > /dev/null <<EOF
[Unit]
Description=[Target] Probe
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/probe.py
Restart=always
RestartSec=5
StandardOutput=append:/home/ubuntu/probe.log
StandardError=append:/home/ubuntu/probe.log

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable [SERVICE_NAME]
sudo systemctl start [SERVICE_NAME]
sudo systemctl status [SERVICE_NAME]
"
```

## 7. Set up daily Discord report

```bash
# Upload reporter
scp -i ~/.ssh/[KEY].pem tools/probe_report.py ubuntu@[EC2_HOST]:~/

# Edit WEBHOOK, LOG_FILE, SERVICE on the server, then add cron:
ssh -i ~/.ssh/[KEY].pem ubuntu@[EC2_HOST] "
(crontab -l 2>/dev/null; echo '0 8 * * * /usr/bin/python3 /home/ubuntu/probe_report.py >> /home/ubuntu/stats.log 2>&1') | crontab -
"
```

## OpenCode commands available

| Command | What it does |
|---------|-------------|
| `scope` | Show engagement scope and authorization |
| `vulns` | List all confirmed vulnerabilities |
| `report` | Generate full pentest report |
| `audit` | Security audit of probe scripts |
| `next` | What to test next (from open questions) |
| `recon` | Passive recon checklist |
| `headers` | Analyze response headers |
| `session` | Analyze cookie/session security |
| `throttle` | Test rate limiting + XFF bypass |
| `massassign` | Test mass assignment |
| `probe` | Check if EC2 probe is running |
| `stats` | Get live probe stats |
| `discord` | Send Discord report now |
