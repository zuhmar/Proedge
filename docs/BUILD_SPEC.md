# CODEX MASTER BUILD PROMPT
# PRO EDGE — NFL & NBA SPORTS ANALYTICS PLATFORM

## 1. Project Overview

Build a production-ready, mobile-responsive sports analytics web application called **PRO EDGE**.

Pro Edge is an advanced NFL and NBA analytics platform that collects available sports data, analyzes player and team performance, generates statistical projections, estimates outcome probabilities, and identifies potential value when sportsbook odds are available.

The application must be functional, data-driven, and expandable.

**Primary goals:**
- Support both NFL and NBA.
- Use free, publicly available, legally accessible sports data wherever possible.
- Avoid requiring paid APIs for the initial version.
- Build statistical models rather than generating arbitrary predictions.
- Provide player prop projections, game predictions, and potential edge detection.
- Show transparent explanations for every prediction.
- Measure prediction accuracy and model calibration.
- Support historical backtesting.
- Build an attractive, premium sports analytics dashboard.
- Make the platform usable on desktop, tablet, and mobile.
- Build modular infrastructure so premium data providers can be added later.

**Important:** Do not invent player statistics, injuries, betting odds, probabilities, or predictions. When required data is unavailable, clearly display an unavailable or insufficient-data state.

---

## 2. Technology Stack

### Frontend
- Next.js with App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts for data visualization
- Lucide icons
- Responsive mobile-first design

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Background processing for data ingestion and model execution

### Database
- PostgreSQL
- Alembic migrations
- Redis optional for caching and job queues

### Analytics
- pandas
- NumPy
- SciPy
- scikit-learn
- statsmodels
- joblib for model serialization

### Deployment
- Docker and Docker Compose
- Environment-based configuration
- Frontend and backend deployable independently
- Local development must work without paid cloud services

Use a monorepo structure:

```text
pro-edge/
├── apps/
│   └── web/
├── services/
│   └── analytics-api/
├── packages/
│   └── shared-types/
├── infrastructure/
│   └── docker/
├── docs/
├── tests/
├── .env.example
├── docker-compose.yml
└── README.md
```

Implement the simplest reliable architecture that satisfies these requirements. Avoid unnecessary microservices.

---

## 3. Design System

Create a premium, professional sports intelligence platform.

### Visual Identity

Application name: PRO EDGE

Design direction:
- Dark charcoal and near-black backgrounds
- Electric green highlights
- White primary typography
- Muted gray secondary typography
- Green for positive model edge
- Red for negative model edge
- Gold for featured insights
- Subtle gradients
- Rounded dashboard panels
- Modern, readable tables
- Smooth but restrained animations

Use a clean professional style inspired by modern financial trading dashboards and advanced sports statistics platforms.

Do not use copyrighted sportsbook branding or third-party logos without permission.

### Navigation

Desktop: Left sidebar navigation.

Mobile: Bottom navigation with expandable secondary menu.

Main navigation:
1. Dashboard
2. NBA
3. NFL
4. Player Props
5. Game Predictions
6. Edge Finder
7. Matchup Analyzer
8. Model Performance
9. Watchlist
10. Settings

Show the active sport and selected date throughout the application.

---

## 4. Main Dashboard

Create a dashboard showing:

### Top Summary Cards
- Today's NBA games
- Today's NFL games
- Games with available projections
- Available player prop projections
- Potential positive-edge opportunities
- Model accuracy and calibration summary

### Today's Games

For each scheduled game, display:
- Away team
- Home team
- Scheduled start time and timezone
- Team records
- Recent form
- Predicted winner
- Win probability
- Projected final score
- Projected total
- Model version
- Prediction generation timestamp

Include a detailed matchup view.

### Featured Insights

Show the highest-ranked opportunities according to the model's estimated edge, data quality, and uncertainty.

Never display an opportunity as a guaranteed winner.

If market odds are unavailable, show projections without an edge value.

### Filters

Allow filtering by:
- NFL or NBA
- Date
- Team
- Player
- Market type
- Minimum model confidence
- Minimum sample size
- Availability of market odds

---

## 5. NBA Analytics Engine

Collect and store available NBA data, including:

### Team Data
- Wins and losses
- Points scored and allowed
- Offensive rating
- Defensive rating
- Net rating
- Pace
- Home and away splits
- Recent 5 and 10 game performance
- Rest days
- Back-to-back games
- Opponent strength

Calculate advanced metrics from underlying statistics where possible.

### Player Data
- Minutes
- Points
- Rebounds
- Assists
- Three-pointers made
- Steals
- Blocks
- Turnovers
- Field goal attempts
- Three-point attempts
- Free throw attempts
- Usage-related metrics when supported
- Recent performance
- Home and away splits
- Opponent splits

### NBA Player Prop Markets
- Points
- Rebounds
- Assists
- Three-pointers made
- Points + rebounds
- Points + assists
- Rebounds + assists
- Points + rebounds + assists
- Steals
- Blocks

Only enable a market when sufficient historical data exists.

### NBA Projection Factors

Consider:
- Recent player performance
- Season averages
- Expected minutes
- Minutes volatility
- Opponent pace
- Opponent defensive strength
- Matchup-specific defensive tendencies
- Team injuries when verified
- Rotation changes when supported by evidence
- Rest days
- Back-to-back status
- Home-court advantage
- Historical variance

Avoid blindly treating the last five games as more important than a larger reliable sample.

Use regularization and uncertainty-aware modeling.

---

## 6. NFL Analytics Engine

Collect and store available NFL data.

### Team Metrics
- Wins and losses
- Points scored and allowed
- Offensive yards per game
- Defensive yards allowed
- Passing efficiency
- Rushing efficiency
- Turnover differential
- Red-zone efficiency
- Third-down efficiency
- Home and away splits
- Recent performance
- Rest days
- Opponent strength

### Player Metrics
- Passing yards
- Passing touchdowns
- Passing attempts
- Completions
- Interceptions
- Rushing yards
- Rushing attempts
- Receiving yards
- Receptions
- Targets
- Receiving touchdowns
- Touchdowns
- Snap participation when available

### NFL Player Prop Markets
- Passing yards
- Passing touchdowns
- Passing completions
- Passing attempts
- Rushing yards
- Rushing attempts
- Receiving yards
- Receptions
- Anytime touchdown probability
- Interceptions

### NFL Projection Factors

Consider:
- Player role and usage
- Recent workload
- Season-long workload
- Opponent defensive strength
- Offensive efficiency
- Team pace
- Game environment
- Home-field advantage
- Rest
- Weather when verified
- Injuries when verified
- Historical variance

Use different modeling approaches for continuous counting statistics and discrete events.

For example, touchdowns should not automatically use the same distribution as passing yards.

---

## 7. Sports Data Collection — Free-First Architecture

Build a modular sports data ingestion system.

Investigate and document the current accessibility, licensing, reliability, rate limits, and historical coverage of potential free data sources.

Candidate sources include:
- nflverse datasets
- nba_api where permitted and operational
- Publicly accessible NBA statistical datasets
- Official league data made available for permitted use
- Free tiers of sports data providers
- Licensed or openly available historical datasets

Do not assume that a source is free for commercial use merely because it is publicly accessible.

### Requirements

Create a provider interface supporting:
- Fetch teams
- Fetch players
- Fetch schedules
- Fetch game results
- Fetch box scores
- Fetch historical statistics
- Fetch injuries where available
- Fetch odds where available

Each provider must implement:
- Request validation
- Retry and exponential backoff
- Rate limiting
- Source attribution
- Error handling
- Timestamp tracking
- Data normalization
- Duplicate detection
- Data freshness checks

Do not bypass captchas, authentication, paywalls, anti-bot protections, or access restrictions.

Do not implement unauthorized scraping.

If a data source is unavailable, degrade gracefully and allow manual CSV import or a compliant alternative provider.

### Data Refresh

Support configurable refresh jobs for:
- Schedules
- Completed games
- Box scores
- Player statistics
- Team statistics
- Injuries
- Odds

Use incremental updates rather than downloading complete historical datasets on every refresh.

Display the last successful refresh time and any source errors.

### Offline Development Mode

Include a small, clearly labeled demonstration dataset.

The entire application must run locally without external data access.

Demo records must never be presented as live data.

---

## 8. Prediction Engine

Create a real statistical modeling system.

### Model Architecture

Use separate models for:
- NBA game outcomes
- NFL game outcomes
- NBA player statistics
- NFL player statistics
- Player prop probabilities

Start with interpretable baselines before implementing advanced machine learning.

Possible approaches:
- Regularized linear regression
- Logistic regression
- Poisson or negative binomial models
- Gradient boosting
- Monte Carlo simulation
- Hierarchical shrinkage for small samples

Choose distributions based on observed data characteristics and validate their suitability.

### Player Projection Formula

Start with a baseline such as:

Projected Statistic = Expected Opportunity × Expected Production per Opportunity

Examples:
- NBA points = expected minutes × estimated points per minute
- NFL receiving yards = expected targets × estimated yards per target

Adjust for opponent strength, role, pace, and other validated factors.

Use historical data to learn adjustment weights.

Do not hardcode arbitrary universal multipliers.

### Monte Carlo Simulation

Implement configurable simulations to estimate:
- Player stat distributions
- Over/under probabilities
- Game winner probabilities
- Score distributions
- Total points distributions
- Spread cover probabilities

Use reproducible random seeds.

Account for correlations between relevant outcomes.

Display uncertainty intervals and distribution charts.

---

## 9. Player Prop Analyzer

Create a dedicated player prop research screen.

### Player Selection

Users can choose:
- Sport
- Team
- Player
- Upcoming game
- Statistic category
- Prop line

### Analysis Display

Show:
- Projected statistic
- Median projection
- Probability over
- Probability under
- Historical average
- Last 5 and 10 games
- Season average
- Relevant opponent statistics
- Projection interval
- Sample size
- Data freshness
- Model version

### Historical Performance Chart

Create a chart with:
- Historical game-by-game results
- Current prop line
- Season average
- Model projection

### Hit Rates

Calculate:
- Last 5 hit rate
- Last 10 hit rate
- Season hit rate
- Relevant historical matchup hit rate, when sample size permits

Display actual sample counts.

Historical hit rate is descriptive, not equivalent to the model's estimated probability.

### Projection Explanation

Generate a plain-language explanation from actual model inputs.

Example:

"The player's expected minutes are above their season average, and the opponent plays at an above-average pace. These factors contribute to the projection."

Only display explanations when the underlying values support them.

---

## 10. Game Prediction System

Support NBA and NFL game predictions.

For every matchup calculate:
- Home win probability
- Away win probability
- Expected home score
- Expected away score
- Expected total
- Expected scoring margin
- Probability of covering selected spread
- Probability over and under a selected total
- Prediction intervals

### Matchup Analysis

Compare teams using:
- Offensive efficiency
- Defensive efficiency
- Recent performance
- Home/away splits
- Rest
- Strength of schedule
- Available player participation information

Display which factors contribute most strongly to the prediction.

Avoid unsupported causal claims.

---

## 11. Pro Edge Finder

Build an engine that compares estimated model probabilities against available sportsbook market prices.

The system must not fabricate sportsbook odds.

### Odds Data

Implement an optional odds provider interface.

Support:
- Permitted free odds feeds
- Manually entered odds
- User-uploaded CSV odds
- Future paid odds APIs

Every odds record must contain:
- Sportsbook or source
- Market
- Selection
- Line
- American odds
- Decimal odds
- Observation timestamp
- Game identifier
- Player identifier when applicable

### Implied Probability

For negative American odds:

Implied Probability = |Odds| / (|Odds| + 100)

For positive American odds:

Implied Probability = 100 / (Odds + 100)

### Expected Value

For decimal odds D and estimated win probability P:

EV per $1 staked = P × (D - 1) - (1 - P)

Equivalently:

EV = P × D - 1

### Model Edge

Edge = Model Probability - Break-Even Probability

Display both percentage-point probability edge and expected return per dollar staked.

Do not confuse them.

### Edge Ranking

Rank opportunities using:
- Estimated expected value
- Model uncertainty
- Sample size
- Data freshness
- Calibration history
- Market liquidity or quality when available

Never rank opportunities based solely on raw predicted probability.

### Important Market Handling

- Match odds with the exact player, game, market, selection, and line.
- Do not compare odds from different prop lines.
- Handle pushes and voids correctly.
- Account for settlement rules.
- Distinguish raw implied probability from no-vig estimated probability.
- Avoid double-counting correlated selections.
- Flag stale market prices.

### Edge Finder Screen

Show:
- Sport
- Game
- Player or team
- Market
- Selection
- Line
- Available odds
- Model probability
- Break-even probability
- Estimated edge
- Estimated EV
- Data quality indicator
- Last updated timestamp

Include filters and sorting.

Do not provide automated betting or sportsbook account access in the initial release.

---

## 12. Model Confidence and Data Quality

Do not display arbitrary confidence percentages.

Separate:
1. Predicted event probability
2. Statistical uncertainty
3. Data completeness
4. Historical model calibration

Build a data quality score using documented rules.

Examples:
- Missing player statistics
- Small sample sizes
- Stale data
- Missing injury information
- Missing market information
- Unstable player minutes or workload

Label predictions with insufficient data.

Do not interpret a 75% win probability as 75% confidence in model correctness.

---

## 13. Model Validation and Backtesting

This is a critical requirement.

Create a dedicated model evaluation pipeline.

### Data Splitting

Use chronological training, validation, and test sets.

Never use random train/test splits that leak future sports information into historical predictions.

### Walk-Forward Backtesting

Implement:
1. Train using data available before a historical cutoff.
2. Generate predictions for subsequent games.
3. Record those predictions.
4. Compare predictions with actual results.
5. Advance the cutoff.
6. Repeat.

Every feature must be computed as of the prediction timestamp.

### Metrics

For game winner predictions:
- Log loss
- Brier score
- Calibration curves
- Accuracy

For player projections:
- MAE
- RMSE
- Prediction interval coverage

For probabilistic prop predictions:
- Brier score
- Log loss where applicable
- Calibration by probability bucket

For edge estimates:
- Estimated EV
- Realized outcomes
- Closing-line comparison where data is available
- Return calculations using recorded historical prices
- Performance by market and model version

### Baselines

Compare models against:
- Season-average projections
- Recent-average projections
- Simple team strength models
- Market-implied baselines when historical odds are available

Advanced models must demonstrate measurable improvement before replacing baselines.

### Leakage Prevention

Prevent:
- Using postgame statistics in pregame predictions
- Using future injury reports
- Using future odds
- Using final lineup information before it was publicly known
- Using future season averages
- Using revised datasets without respecting historical availability

### Performance Dashboard

Show:
- Predictions evaluated
- Prediction accuracy
- Brier score
- Log loss
- Mean absolute error
- Calibration chart
- Performance by sport
- Performance by market
- Performance over time
- Model version comparisons

Show sample sizes prominently.

Do not imply profitable betting performance without adequate out-of-sample evidence.

---

## 14. Database Design

Use PostgreSQL with normalized relational tables.

Create at least the following entities.

### users
- id
- email
- password_hash or external auth identifier
- role
- created_at
- updated_at

### teams
- id
- sport
- league_team_id
- name
- abbreviation
- conference
- division

### players
- id
- sport
- league_player_id
- full_name
- position
- current_team_id
- active_status

### games
- id
- sport
- season
- season_type
- home_team_id
- away_team_id
- scheduled_at
- status
- home_score
- away_score
- completed_at

### player_game_stats
- id
- game_id
- player_id
- team_id
- minutes_or_snaps
- statistics_json
- source_id
- collected_at

### team_game_stats
- id
- game_id
- team_id
- statistics_json
- source_id
- collected_at

### injuries
- id
- player_id
- game_id
- reported_status
- source_id
- observed_at

### odds_snapshots
- id
- game_id
- player_id
- provider_id
- market_type
- selection
- line
- american_odds
- decimal_odds
- observed_at

### model_versions
- id
- sport
- model_type
- version
- training_cutoff
- feature_schema_version
- artifact_path
- evaluation_metrics_json
- created_at

### predictions
- id
- game_id
- player_id
- model_version_id
- market_type
- predicted_value
- predicted_probability
- lower_interval
- upper_interval
- generated_at
- feature_cutoff_at
- data_quality_score

### prediction_evaluations
- id
- prediction_id
- actual_result
- evaluation_metrics_json
- evaluated_at

### watchlists
- id
- user_id
- name
- created_at

### watchlist_items
- id
- watchlist_id
- game_id
- player_id
- market_type

### data_sources
- id
- name
- provider_type
- source_url
- license_notes
- last_success_at
- status

### ingestion_runs
- id
- source_id
- job_type
- started_at
- completed_at
- status
- records_processed
- error_message

Implement:
- Foreign keys
- Appropriate indexes
- Unique constraints
- Data validation
- Migration scripts
- UTC timestamps internally
- Historical source tracking

Use JSON fields only for flexible sport-specific statistics, not as a replacement for all relational modeling.

---

## 15. Authentication and User Accounts

Implement secure user authentication.

Support:
- Registration
- Login
- Logout
- Password reset
- User profile
- Saved watchlists

Use secure password hashing, HTTP-only cookies where appropriate, input validation, and standard session security.

Provide an admin role for:
- Managing data ingestion
- Monitoring errors
- Managing model versions
- Triggering authorized refreshes
- Viewing system health

Never expose API credentials or administrative actions to normal users.

---

## 16. Additional Application Screens

### NBA Screen
- Schedule
- Standings
- Teams
- Players
- Statistical leaders
- Matchups
- Predictions

### NFL Screen
- Weekly schedule
- Standings
- Teams
- Players
- Statistical leaders
- Matchups
- Predictions

### Matchup Analyzer
- Side-by-side team comparisons
- Efficiency charts
- Historical performance
- Expected scoring
- Win probabilities
- Key model factors

### Watchlist
- Saved players
- Saved games
- Saved markets
- Latest projections
- Historical changes

### Settings
- Preferred sport
- Timezone
- Odds format
- Dashboard preferences
- Notification preferences for future implementation

### Admin Dashboard
- Data source status
- Refresh jobs
- Import history
- Failed requests
- Model training jobs
- Model versions
- Data freshness
- Application health

---

## 17. API Architecture

Build documented REST endpoints.

Examples:

```text
GET /api/v1/sports
GET /api/v1/nba/games
GET /api/v1/nba/teams
GET /api/v1/nba/players
GET /api/v1/nfl/games
GET /api/v1/nfl/teams
GET /api/v1/nfl/players

GET /api/v1/games/{id}
GET /api/v1/games/{id}/prediction
GET /api/v1/games/{id}/matchup

GET /api/v1/players/{id}
GET /api/v1/players/{id}/stats
GET /api/v1/players/{id}/projections

GET /api/v1/props
GET /api/v1/props/{id}/analysis

GET /api/v1/edges
GET /api/v1/models/performance
GET /api/v1/models/calibration

GET /api/v1/watchlists
POST /api/v1/watchlists

GET /api/v1/data/status
```

Include:
- OpenAPI documentation
- Pagination
- Filtering
- Input validation
- Structured errors
- Rate limiting
- Authentication where required
- Automated API tests

---

## 18. Testing Requirements

Build automated tests for:

### Data Processing
- Provider response parsing
- Duplicate detection
- Missing data
- Invalid statistics
- Timestamp handling
- Odds normalization

### Analytics
- Implied probability calculations
- Expected value calculations
- Push and void handling
- Projection calculations
- Probability distributions
- Simulation reproducibility
- Model calibration
- Backtest leakage prevention

### Application
- Authentication
- API responses
- Navigation
- Filtering
- Player selection
- Game selection
- Empty states
- Mobile responsiveness
- Data freshness labels

Use pytest for Python and appropriate TypeScript testing tools for the frontend.

---

## 19. Security, Compliance, and Reliability

Implement:
- Server-side secret management
- Environment variables
- Authentication and authorization
- API rate limiting
- Request validation
- Database access controls
- Structured logging
- Health checks
- Error monitoring
- Dependency vulnerability checks

Follow data provider licenses and usage restrictions.

Treat this as a sports analytics and informational research product.

Do not implement direct sportsbook wagering, deposits, withdrawals, or account automation.

Include appropriate disclaimers about prediction uncertainty.

---

## 20. Implementation Phases

Build the application incrementally.

### Phase 1 — Foundation

Deliver:
- Working monorepo
- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Docker configuration
- Authentication
- Responsive layout
- Navigation
- Dark Pro Edge theme
- Database migrations
- Local demo mode

**Completion criteria:** The entire stack starts locally and the main pages load without errors.

### Phase 2 — Real Sports Data

Deliver:
- NFL provider
- NBA provider
- Team and player normalization
- Historical game import
- Schedule ingestion
- Player statistics ingestion
- Data source monitoring
- CSV import fallback

**Completion criteria:** Real historical data is stored and accessible through API endpoints.

### Phase 3 — Analytics Engine

Deliver:
- NBA player projections
- NFL player projections
- Game outcome models
- Monte Carlo simulation
- Prediction storage
- Probability estimates
- Uncertainty intervals

**Completion criteria:** The system produces reproducible, statistically grounded projections from historical data.

### Phase 4 — Research Screens

Deliver:
- NBA analytics
- NFL analytics
- Player prop analyzer
- Game prediction screens
- Matchup comparison
- Historical performance charts

**Completion criteria:** Users can research actual players and matchups.

### Phase 5 — Edge Finder

Deliver:
- Odds provider abstraction
- Manual odds entry
- Odds CSV upload
- Implied probability calculations
- EV calculations
- Edge ranking
- Stale odds detection

**Completion criteria:** Users can compare model probabilities with matching market odds.

### Phase 6 — Model Validation

Deliver:
- Chronological backtesting
- Walk-forward evaluation
- Calibration charts
- Baseline comparisons
- Model version tracking
- Prediction accuracy dashboard

**Completion criteria:** Every promoted model has documented out-of-sample performance.

### Phase 7 — Production Preparation

Deliver:
- Security review
- Performance optimization
- Responsive QA
- Deployment configuration
- Monitoring
- Documentation
- Automated test suite

**Completion criteria:** The application is deployable with documented operating procedures.

---

## 21. Codex Execution Instructions

You are acting as the lead full-stack engineer, data engineer, and machine learning engineer.

Your job is to implement this application, not simply describe how it could be built.

Follow these rules:

1. Inspect the existing repository before making changes.
2. If the repository is empty, initialize the project.
3. Start with Phase 1.
4. Create real source files and configurations.
5. Write clean, modular, maintainable code.
6. Use TypeScript strict mode.
7. Use Python type hints.
8. Implement database migrations.
9. Provide realistic local demo data, explicitly marked as demo.
10. Do not fabricate real sports data or odds.
11. Do not create fake functional buttons.
12. Make every visible interaction perform a meaningful action.
13. Run available tests, linting, and type checks.
14. Fix errors before moving forward.
15. Keep documentation updated.
16. Track progress in a `PROGRESS.md` file.
17. Record unresolved blockers and data licensing limitations.
18. Do not assume a third-party API is available without verifying it.
19. Do not silently substitute a mock provider for a real provider.
20. Prioritize correct analytics over impressive-looking but misleading predictions.

At the end of each phase, provide:
- Files created or modified
- Features implemented
- Tests executed
- Test results
- Remaining limitations
- Instructions for running the application
- Recommended next phase

Do not skip directly to building an advanced prediction engine before the data pipeline is reliable.

## 22. Begin Implementation

Start implementing **Phase 1 — Foundation** immediately.

First inspect the workspace and establish the monorepo structure.

Then create:
- Frontend application
- Backend API
- Database models and migrations
- Docker development environment
- Authentication foundation
- Responsive Pro Edge dashboard
- Navigation
- Demo dataset
- Documentation
- Initial automated tests

Run the application and validate that the frontend, backend, and database work together.

Continue through Phase 1 until its completion criteria are met.

Do not stop after generating a project plan.