# External Pipeline Monitor Runbook

> Owner: DevOps (9th persona). Single source of truth for remote-access setup.
> Update this file on any operational change + record in `docs/learn-logs/devops.md`.

[Back to runbooks index](preview-deploy.md)

## Overview

Exposes the local Windows pipeline dashboard (`pipeline_dashboard.py`, port 8790)
to the founder's browser anywhere via **Cloudflare Tunnel + Zero Trust Access**.
No inbound firewall rules. No VPS involvement. PII-free payload confirmed.

```
[Founder's browser (mobile/anywhere)]
        |  https://pipeline.n9n.co.kr
        v
[Cloudflare edge]
        |  Cloudflare Access gate (email OTP — <FOUNDER_EMAIL> only)
        v
[cloudflared daemon on Windows laptop]  <-- outbound-only tunnel
        |  http://127.0.0.1:8790
        v
[pipeline_dashboard.py (Python stdlib, no LLM, PII-free)]
```

**Topology constraint (non-negotiable):**
- Tunnel runs on local Windows, NOT on the preview VPS. VPS stays lean.
- Port 8790 is exclusive to this dashboard (port 8787 is reserved for HEADROOM).
- Access policy is mandatory — no public exposure even though data is PII-free
  (operational/BI state must not leak).

---

## Phase 1 — Prerequisites (one-time, founder's machine)

### 1.1 Install cloudflared

Open PowerShell as administrator:

```powershell
winget install cloudflare.cloudflared
# Verify:
cloudflared --version
```

Alternative (manual): download the Windows x64 .msi from
`https://github.com/cloudflare/cloudflared/releases/latest` and install.

### 1.2 Authenticate cloudflared to your Cloudflare account

This step opens a browser. Run in PowerShell (interactive — founder must execute):

```powershell
cloudflared tunnel login
```

- A browser window opens to Cloudflare login.
- Select the zone `n9n.co.kr`.
- On success, `cert.pem` is written to `%USERPROFILE%\.cloudflared\cert.pem`.
  This file is a secret — do not share or commit it.

---

## Phase 2 — Tunnel Creation (one-time)

### 2.1 Create the named tunnel

```powershell
cloudflared tunnel create pipeline-monitor
```

Output includes a **Tunnel ID** (UUID format, e.g. `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
Note it — you will use it as `<TUNNEL_ID>` throughout.

A credentials JSON file is written to:
```
%USERPROFILE%\.cloudflared\<TUNNEL_ID>.json
```

### 2.2 Move credentials to the vault

```powershell
# Move to gitignored vault (infra/secrets/ is already gitignored)
Move-Item "$env:USERPROFILE\.cloudflared\<TUNNEL_ID>.json" `
          "infra\secrets\<TUNNEL_ID>.json"
```

Register the asset in `infra/registry/cloudflared.yaml` (reference only, no plaintext):

```yaml
# infra/registry/cloudflared.yaml
tunnel_name: pipeline-monitor
tunnel_id_vault_ref: "infra/secrets/<TUNNEL_ID>.json"   # vault ref only
cert_vault_ref: "%USERPROFILE%\\.cloudflared\\cert.pem"
hostname: pipeline.n9n.co.kr
local_target: http://127.0.0.1:8790
created_at: "YYYY-MM-DD"
```

### 2.3 Create the config file from the template

Copy the example template and fill in `<TUNNEL_ID>`:

```powershell
Copy-Item infra\cloudflared\config.example.yml infra\cloudflared\config.yml
# Edit infra\cloudflared\config.yml: replace <TUNNEL_ID> with the real UUID
```

`infra/cloudflared/config.yml` is gitignored (see `.gitignore` addition in Phase 4).

### 2.4 Route DNS

```powershell
cloudflared tunnel route dns pipeline-monitor pipeline.n9n.co.kr
```

This writes a CNAME record to Cloudflare DNS automatically.
**No manual Cloudflare dashboard action needed for DNS.**

Verify in Cloudflare dashboard: DNS > `pipeline.n9n.co.kr` should show a CNAME
to `<TUNNEL_ID>.cfargotunnel.com` with orange-cloud proxy (Cloudflare-managed
tunnel endpoints use the proxy — this is correct and differs from VPS preview
subdomains which must stay grey-cloud).

---

## Phase 3 — Cloudflare Zero Trust Access (founder action, interactive)

This phase requires clicking in the Cloudflare Zero Trust dashboard.
Go to: `https://one.dash.cloudflare.com/` > your account > `n9n.co.kr`.

### 3.1 Enable Zero Trust (if not already)

Zero Trust > Get Started. Free plan covers this use case.

### 3.2 Create a Self-Hosted Application

1. Zero Trust sidebar > **Access** > **Applications** > **Add an application**.
2. Select **Self-Hosted**.
3. Fill in:
   - **Application name**: `Pipeline Monitor`
   - **Subdomain**: `pipeline`
   - **Domain**: `n9n.co.kr`
   - **Application domain (result)**: `pipeline.n9n.co.kr`
4. Leave session duration at 24 hours (or set to your preference).
5. Click **Next**.

### 3.3 Add an Access Policy

1. **Policy name**: `founder-only`
2. **Action**: Allow
3. **Include** rule:
   - Selector: **Emails**
   - Value: `<FOUNDER_EMAIL>`  (use your actual gmail address)
4. Click **Next** then **Add application**.

### 3.4 Verify Access is Active

Navigate to `https://pipeline.n9n.co.kr` in an incognito window.
You should see a Cloudflare Access login page (email OTP), NOT the dashboard.
Only after OTP verification does the dashboard appear.

If the dashboard loads without OTP: the Access application is not wired to the
hostname. Re-check step 3.2 — ensure the domain matches exactly.

---

## Phase 4 — Normal Operation

### 4.1 Recommended: use the convenience launcher

```powershell
# From repo root:
.\scripts\workflow\serve_dashboard.ps1
```

This starts the dashboard on port 8790 and the tunnel in a second window.
See `scripts/workflow/serve_dashboard.ps1` for details.

### 4.2 Manual launch (two terminals)

Terminal 1 — dashboard:
```powershell
python scripts/workflow/pipeline_dashboard.py --port 8790
```

Terminal 2 — tunnel:
```powershell
cloudflared tunnel --config infra\cloudflared\config.yml run pipeline-monitor
```

### 4.3 Optional: Register cloudflared as a Windows service

Runs the tunnel automatically on boot (no terminal needed):

```powershell
# One-time registration (admin PowerShell):
cloudflared service install --config "D:\AI\workspace\compounding-stack-harness\infra\cloudflared\config.yml"

# Control:
net start cloudflared
net stop cloudflared

# Remove service:
cloudflared service uninstall
```

Note: if registered as a service, also configure the dashboard to start on boot
(Task Scheduler or a separate service wrapper) so both start together.

---

## Phase 5 — Teardown / Revoking Access

### Temporary pause (keep tunnel registered):

```powershell
# Stop the tunnel process / service
net stop cloudflared   # if running as service
# Or just close the terminal running cloudflared
```

### Permanent teardown:

```powershell
# 1. Delete the CNAME record in the Cloudflare dashboard:
#    DNS > Records > pipeline.n9n.co.kr (CNAME -> <TUNNEL_ID>.cfargotunnel.com) > Delete.
#    (cloudflared has no DNS-route delete subcommand; remove it in the dashboard.)
# 2. Delete the tunnel (must be stopped + DNS removed first)
cloudflared tunnel delete pipeline-monitor
# 3. Remove credentials from vault
Remove-Item "infra\secrets\<TUNNEL_ID>.json"
# 4. In Cloudflare Zero Trust dashboard: Access > Applications > delete Pipeline Monitor
# 5. Remove config.yml
Remove-Item "infra\cloudflared\config.yml"
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `pipeline.n9n.co.kr` returns Cloudflare 1033 error | Tunnel is not running | Start `cloudflared tunnel run` or `net start cloudflared` |
| Dashboard loads without OTP prompt | Access application not created or wrong domain | Re-do Phase 3 |
| OTP email not arriving | Email in Access policy does not match sender | Check policy email value; check spam |
| Dashboard shows stale data | `--once` flag not used; data freshness is a UI concern | Reload browser (dashboard auto-refreshes) |
| `cloudflared` reports `cert.pem` not found | `cloudflared tunnel login` not completed | Re-run Phase 1.2 |
| Port conflict on 8790 | Another process on 8790 | `netstat -ano | findstr 8790`; adjust `--port` and config.yml |
| 8787 is unavailable | Expected — HEADROOM service | Dashboard uses 8790 exclusively; do not change |

---

## Security Notes

- **Access gate is mandatory.** Even though the dashboard is PII-free, operational
  pipeline state (case counts, SLA breach status, deploy failures) is internal BI.
- **Credentials never committed.** `infra/secrets/` is gitignored. `config.yml`
  (containing the tunnel ID) is also gitignored — only `config.example.yml` is tracked.
- **Outbound-only tunnel.** Windows firewall requires no changes. No inbound ports opened.
- **VPS not involved.** The preview VPS (Hostinger, Coolify) is completely separate.
  Do not install cloudflared on the VPS (topology constraint).
- **Single-email Access policy.** Only `<FOUNDER_EMAIL>` is allowed. Do not add
  wildcards or domain-wide rules for this application.

---

## Cost

| Item | Cost |
|---|---|
| Cloudflare Tunnel | $0 (free tier, unlimited) |
| Cloudflare Access (1 application, 1 user) | $0 (free tier covers up to 50 users) |
| n9n.co.kr DNS (already managed in Cloudflare) | $0 (already paid) |

Total additional monthly cost: **$0**.
