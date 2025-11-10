## Migrate AMP -> Gemini Plan

### Scope
- Replace AMP job/monitor for: market analysis, news analysis, trade suggestion generation.
- Preserve execution: risk rules and order routing remain deterministic and separate from LLM.

### Integration Strategy
1) Create `api/services/gemini_service.py` adapter (already present) and add `enhanced_gemini_service.py` batching/caching.
2) Introduce caching layer using Redis with keys hashed from prompts to avoid repeated charges.
3) Add rate limiter (RPM) via token bucket in Redis. Env: `GEMINI_RATE_LIMIT_RPM`.
4) Batch symbols/news into a single structured prompt when feasible.
5) Validate Gemini outputs against schema; discard unsafe trades.

### Cost Controls
- Cache all prompt->response pairs for 24h unless data freshness requires otherwise.
- Use `gemini-1.5-flash` for routine tasks; escalate to `pro` only on-demand.
- Enforce max tokens per request and early truncate inputs.
- Nightly summarization jobs, not per-tick.

### Risk Separation
- Keep risk sizer, max concurrent trades, max leverage, and session filters in `core/risk_management/*`.
- Gemini proposes trades -> `TradingService` validates against risk rules -> only then calls broker API.

### Rollout
- Phase 1: Shadow mode (log Gemini suggestions, do not execute).
- Phase 2: Paper/demo account execution with tight size caps.
- Phase 3: Live execution after 2 weeks stable.

