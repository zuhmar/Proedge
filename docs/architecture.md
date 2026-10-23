# Foundation architecture

The browser uses relative `/api/v1` URLs. Next.js forwards requests to FastAPI via `API_INTERNAL_URL`; cookies remain first-party. Docker image builds configure the internal destination as `http://api:8000`. Independent frontend deployments must configure a private backend destination when building. Do not expose database credentials to frontend code.

PostgreSQL is the source of truth. Alembic migrations create users, sessions, password resets, teams, players, games, data sources, watchlists, watchlist items and preferences. Relationships, indexes and natural-key constraints protect the foundation. Timestamps use timezone-aware UTC. Demo games have a unique source ID, sport and explicit demo flag. The seed is one transaction and never generates model output.

Schemas for injuries, game statistics, ingestion runs, odds, model versions, predictions and evaluations will be added with the phases that actually implement them. Provider interfaces and background workers are deferred to Phase 2. A static dashboard label is never a substitute for a functioning ingestion service.

Availability is explicit: nullable prediction, no model metrics and no odds. The UI does not convert missing values into zero confidence or a model win probability. Game counts refer to the selected UTC date; display times use the user's timezone. Search and sport filters intersect. Empty-date and error states are separate.

Authentication stores opaque random session tokens as SHA-256 digests. Password verification uses Argon2, including a dummy verification for absent accounts. The reset endpoint returns the same message for present and absent accounts, probes mail transport for both, and never returns the reset token to the browser. Reset redemption locks the token row and revokes all sessions and reset tokens for that user.

Local SMTP intentionally connects only to the development mail sink. A production email adapter with TLS/authentication remains a deployment requirement. The API must run behind a shared rate-limiting gateway before scaling. No public admin registration is provided. Administrators can be assigned using trusted database administration after identity verification.
