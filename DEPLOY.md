# Deploying Extract AI

The repo builds into a **single Docker image** (root `Dockerfile`) that serves
both the React frontend and the FastAPI API from one origin, plus a managed
**Postgres**. Designed for Railway, but the image runs on any Docker host.

## Railway (single service + Postgres)

### Option A — CLI (fastest to a live URL)

```bash
npm i -g @railway/cli
railway login                       # one-time browser auth
railway init -n extract-ai          # create the project
railway add --database postgres     # managed Postgres (injects DATABASE_URL)
railway variables \
  --set "SECRET_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(48))')" \
  --set "LLM_MOCK=true" \
  --set "ENVIRONMENT=production"
railway up                          # build the Dockerfile + deploy
railway domain                      # generate a public *.up.railway.app URL
```

### Option B — Dashboard (enables auto-deploy / CD)

1. **New Project → Deploy from GitHub repo →** `josntndr/extract-ai`.
   Railway detects the root `Dockerfile` and builds it.
2. **+ New → Database → PostgreSQL.** Railway injects `DATABASE_URL` into the
   service automatically.
3. In the web service **Variables**, add:
   - `SECRET_KEY` — a long random string
   - `LLM_MOCK=true` (free demo; no API key). For real extraction instead set
     `LLM_PROVIDER=openai` (or `anthropic`) and the matching `*_API_KEY`.
   - `ENVIRONMENT=production`
4. **Settings → Networking → Generate Domain.**
5. **Settings → leave "Deploy on push" enabled** → every push to `main`
   redeploys automatically (continuous deployment).

Migrations run automatically on boot (`alembic upgrade head`), and the
`/health` endpoint is the healthcheck.

## Notes & limits

- **RAM:** the image bundles EasyOCR + PyTorch (~1–2 GB). Native-PDF text
  extraction + LLM run on small instances; **scanned-image OCR needs ~1–2 GB
  RAM** — bump the instance size if you upload scanned documents.
- **Storage** is the container filesystem (ephemeral on redeploy). For durable
  uploads, attach a Railway volume at `/app/storage` or switch
  `STORAGE_BACKEND=s3`.
- **Secrets** are platform variables only — never commit `.env`.
