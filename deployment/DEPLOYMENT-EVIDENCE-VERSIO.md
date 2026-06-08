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

## Health endpoint

`https://procm.oerse-kippies.nl/health` → JSON status + database connection state

## Production setup (operator)

1. Copy `config/config.example.php` → `config/config.php`
2. Set `database.password` and `api.api_key`
3. Run `php scripts/migrate.php` on server
4. Flask UI remains local (`python run.py`) until PHP API port or Python 3 on Versio

## Verify on server

```bash
ssh nol@vserver423.axc.eu 'cd ~/domains/procm.oerse-kippies.nl/procurementManagement && git rev-parse --short HEAD'
```
