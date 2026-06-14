# serve_dashboard.ps1 -- Convenience launcher: pipeline dashboard + cloudflared tunnel
#
# Starts two processes side-by-side so the founder can open pipeline.n9n.co.kr
# from anywhere after running this script on the local Windows machine.
#
# PREREQUISITES (one-time, see docs/runbooks/external-pipeline-monitor.md):
#   1. cloudflared installed (winget install cloudflare.cloudflared)
#   2. cloudflared tunnel login   -- done in browser
#   3. cloudflared tunnel create pipeline-monitor  -- credentials in infra/secrets/
#   4. infra/cloudflared/config.yml exists (copy from config.example.yml, fill TUNNEL_ID)
#   5. Cloudflare Zero Trust Access app created (pipeline.n9n.co.kr, email OTP policy)
#
# USAGE
#   From repo root in PowerShell:
#     .\scripts\workflow\serve_dashboard.ps1
#
# STOPPING
#   Close both terminal windows, or Ctrl-C in each.
#   If cloudflared is registered as a Windows service, use:
#     net stop cloudflared
#
# SECURITY
#   No credentials or tokens are inlined here.
#   The tunnel config references infra/cloudflared/config.yml (gitignored).
#   The dashboard binds to 127.0.0.1 only -- cloudflared proxies it; never expose 8790 publicly.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve repo root (two levels up from scripts/workflow/)
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path

# ---------------------------------------------------------------------------
# Validate prerequisites
# ---------------------------------------------------------------------------
$ConfigFile = Join-Path $RepoRoot "infra\cloudflared\config.yml"
if (-not (Test-Path $ConfigFile)) {
    Write-Error @"
ERROR: infra\cloudflared\config.yml not found.
Copy infra\cloudflared\config.example.yml to infra\cloudflared\config.yml
and replace <TUNNEL_ID> with your tunnel UUID.
See docs/runbooks/external-pipeline-monitor.md Phase 2.
"@
    exit 1
}

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Error @"
ERROR: cloudflared not found in PATH.
Install with: winget install cloudflare.cloudflared
See docs/runbooks/external-pipeline-monitor.md Phase 1.
"@
    exit 1
}

$PythonCmd = "python"
if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: python not found in PATH."
    exit 1
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
$DashboardScript = Join-Path $RepoRoot "scripts\workflow\pipeline_dashboard.py"
$DashboardPort   = 8790
$TunnelConfig    = $ConfigFile

# ---------------------------------------------------------------------------
# Launch dashboard in a new window
# ---------------------------------------------------------------------------
Write-Host "Starting pipeline dashboard on http://127.0.0.1:$DashboardPort ..."
$DashProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$RepoRoot'; python '$DashboardScript' --port $DashboardPort"
) -PassThru

Write-Host "Dashboard PID: $($DashProcess.Id)"

# Brief pause to let the HTTP server bind before the tunnel connects.
Start-Sleep -Seconds 2

# ---------------------------------------------------------------------------
# Launch cloudflared tunnel in a new window
# ---------------------------------------------------------------------------
Write-Host "Starting cloudflared tunnel (config: $TunnelConfig) ..."
$TunnelProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cloudflared tunnel --config '$TunnelConfig' run pipeline-monitor"
) -PassThru

Write-Host "Tunnel PID: $($TunnelProcess.Id)"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Both processes started."
Write-Host "  Dashboard : http://127.0.0.1:$DashboardPort"
Write-Host "  Public URL: https://pipeline.n9n.co.kr  (after Cloudflare Access OTP)"
Write-Host ""
Write-Host "Close the two spawned windows to stop both processes."
Write-Host "Dashboard PID=$($DashProcess.Id)  Tunnel PID=$($TunnelProcess.Id)"
