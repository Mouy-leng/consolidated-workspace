## GenX_FX Network & Service Map

### Services and Hosts
- **API (FastAPI, Python)**: Container `api` on MCP/VPS. Exposes port 8000 (HTTP). Internal network connects to Postgres, Redis, Mongo.
- **Discord Bot**: Container `discord_bot`. Talks to API via `http://api:8000`. Outbound to Discord API only.
- **Telegram Bot**: Container `telegram_bot`. Talks to API via `http://api:8000`. Outbound to Telegram API only.
- **WebSocket Feed**: Container `websocket_feed`. Outbound to market data sources and broker APIs. Uses Redis for pub/sub caching.
- **Scheduler**: Container `scheduler`. Periodically calls API endpoints, triggers strategies/trade checks.
- **AI Trainer**: Container `ai_trainer`. Access to filesystem volumes `ai_models/`, `data/`, and DBs.
- **Nginx**: Optional edge proxy. Exposes 80/443 to public internet and reverse-proxies API 8000.
- **Databases**: `postgres` (5432), `mongo` (27017), `redis` (6379) – internal network only.
- **Monitoring**: `prometheus` (9090), `grafana` (3000) – restrict to admin IPs.

### Ports and Connectivity
- Public ingress: 80, 443 (Nginx), optionally 8000 if exposing FastAPI directly.
- Internal-only: 5432 Postgres, 6379 Redis, 27017 Mongo, 9090 Prometheus, 3000 Grafana.
- Outbound egress: Broker APIs (FXCM, Bybit), Gemini API, Discord/Telegram, package repos.

### Data Flows
1) Bots/Scheduler -> API `/trading/*` routes -> TradingService -> Broker SDK/API.
2) Websocket/Market data -> Redis cache -> API/Strategies.
3) API -> Postgres (orders, accounts, signals), Mongo (logs/models), Redis (cache/rate-limit).
4) Nginx -> API 8000 (reverse proxy, TLS termination).

### Registries and CI/CD
- Images built by GitHub Actions (free tier) and pushed to GHCR (free for public; private with free allowances).
- Deployment via SSH to MCP/VPS; `docker compose -f docker-compose.production.yml up -d`.

### Broker/Third-party
- FXCM REST/WebSocket: `api-fxpractice.fxcm.com` (demo) or `api.fxcm.com` (live). Auth via `X-Auth-Token`.
- Bybit: `api.bybit.com` or `api-testnet.bybit.com` with HMAC keys.
- Gemini (LLM): `https://generativelanguage.googleapis.com` with API key.

### Cost-Saving Notes
- Prefer GHCR + GitHub Actions. Avoid paid runners.
- Cache model artifacts and API responses in Redis; schedule heavy jobs during off-peak.
- Rate-limit Gemini usage and batch prompts; persist results to Postgres/Mongo.
- Use one VPS with multiple containers on a bridge network vs multiple VMs.

### Potential Paid Services and Alternatives
- Managed Postgres/Mongo: Prefer self-hosted containers initially; consider Railway/Render free tiers with caution.
- Container registry: GHCR or Docker Hub free tiers.
- Monitoring: Prometheus/Grafana self-hosted instead of paid APM initially.

