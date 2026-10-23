# Data boundaries and Phase 2 prerequisites

Phase 1 uses original fictional fixtures; all demo data is labeled and no third-party API is contacted. Sports provider accessibility, licensing, historical coverage and rate limits have **not yet been verified**. No source is approved for commercial use by this repository.

| Candidate | Phase 2 verification required | Current state |
|---|---|---|
| nflverse | Dataset-specific license and attribution; upstream rights; release URLs, revision history, availability timestamps and historical coverage | Not integrated |
| nba_api / league endpoints | Endpoint terms, operational accessibility, rate limits and permission for intended use | Not integrated |
| Licensed historical CSV | Dataset provenance, permitted use, schema validation, timestamp semantics and duplicate keys | Import not implemented |
| Odds feeds | Exact market identity, source rights, observation timestamps, settlement rules and freshness | Not integrated |

Do not bypass authentication, captchas or anti-bot restrictions. Public accessibility does not imply commercial licensing. Phase 2 must implement validated provider contracts, bounded retries with backoff, rate limits, attribution, incremental normalization, freshness checks and import monitoring. Failure should expose unavailable states and a compliant CSV alternative. Do not train on fictional fixtures or claim demo records represent real historical observations.
