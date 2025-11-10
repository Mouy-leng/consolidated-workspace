## Secrets and Environment Variables

Move all credentials to GitHub Secrets (for CI) and a server-side `.env` file with `chmod 600`.

### GitHub Secrets (examples)
- `SSH_PRIVATE_KEY`, `SSH_USER`, `SSH_HOST`, `SSH_PORT`
- `DISCORD_TOKEN`, `TELEGRAM_TOKEN`
- `BYBIT_API_KEY`, `BYBIT_API_SECRET`
- `GEMINI_API_KEY`

### Server `.env` file
- Use `.env.example` as a template.
- Store on server at `~/genx/.env` (not committed). Set ownership to deploy user.

### Code usage
- Read secrets via environment variables only. Do not hard-code.
- Rotate keys periodically and on any suspected leak.

