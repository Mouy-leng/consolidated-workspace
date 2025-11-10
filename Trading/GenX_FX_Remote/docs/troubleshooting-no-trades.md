## Troubleshooting: No Trades Being Placed

### 1. Check account and broker
- Verify demo/live status and credentials.
- Confirm API keys valid (FXCM token, Bybit key/secret).
- Ensure correct server URLs (demo vs live endpoints).

### 2. App health and logs
- API health: curl http://HOST:8000/health
- Check container logs for `api`, `websocket_feed`, `scheduler`.

### 3. Filters blocking execution
- Session/time filters active? News filter blocking? Risk sizer rejecting sizes?
- Validate symbols match broker (e.g., XAUUSD vs GOLD, suffixes like .i).

### 4. Order validation
- Lot size within broker min/max; precision correct.
- Sufficient margin; leverage set.

### 5. Network and firewall
- Outbound to broker API reachable from container: ping, curl auth endpoint.
- Ports open: 80/443 outbound; 8000 ingress if needed.

### 6. Dry run on demo
- Switch to demo account and place a 0.01 lot test trade.
- Observe broker logs for rejects.

### 7. LLM integration
- Ensure Gemini calls are cached and not rate limited unexpectedly.
- If LLM down, fallback to baseline strategy to generate signals.

