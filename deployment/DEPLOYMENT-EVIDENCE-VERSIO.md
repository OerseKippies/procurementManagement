# procM Versio Deployment Evidence

Date: 2026-06-08  
Host: `nol@vserver423.axc.eu`

## Deployed

| Item | Value |
|---|---|
| Path | `~/domains/procm.oerse-kippies.nl/procurementManagement` |
| Commit | `a2cb8bc` |
| Method | `git clone` + `public_html/index.php` health stub |
| Script | `scripts/deploy_procm_versio.sh` |

## Health endpoint (when subdomain active)

`https://procm.oerse-kippies.nl/` → JSON `{"status":"deployed","module":"procM",...}`

## Blockers

1. **DNS/subdomain** — `procm.oerse-kippies.nl` not resolving (DirectAdmin subdomain registration required).
2. **Flask runtime** — Versio host has Python 2.7 only; Flask app needs Python 3.10+ (local: `python run.py`).

## Verify on server

```bash
ssh nol@vserver423.axc.eu 'cd ~/domains/procm.oerse-kippies.nl/procurementManagement && git rev-parse --short HEAD'
```
