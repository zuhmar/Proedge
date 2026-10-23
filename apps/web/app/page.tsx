"use client";
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Bell,
  Bookmark,
  CalendarDays,
  Check,
  ChevronRight,
  Database,
  Flame,
  LayoutDashboard,
  LogOut,
  Menu,
  Search,
  Settings,
  ShieldCheck,
  Target,
  TrendingUp,
  Trophy,
  Users,
  X,
  Zap,
} from "lucide-react";
import type { Game, User } from "../../../packages/shared-types";
import { Button } from "../components/ui/button";
import { filteredGames } from "../components/ui-utils";
const nav = [
  ["Dashboard", LayoutDashboard],
  ["NBA", Trophy],
  ["NFL", Flame],
  ["Player Props", Users],
  ["Game Predictions", BarChart3],
  ["Edge Finder", Zap],
  ["Matchup Analyzer", Target],
  ["Model Performance", TrendingUp],
  ["Watchlist", Bookmark],
  ["Settings", Settings],
] as const;
type List = { id: number; name: string; games: Game[] };
type Status = {
  sources: {
    name: string;
    status: string;
    last_success_at: string;
    license_notes: string;
  }[];
};
export default function Dashboard() {
  const [resetToken, setResetToken] = useState("");
  const [page, setPage] = useState("Dashboard"),
    [sport, setSport] = useState("ALL"),
    [day, setDay] = useState("2026-10-23"),
    [search, setSearch] = useState(""),
    [games, setGames] = useState<Game[]>([]),
    [status, setStatus] = useState<Status | null>(null),
    [user, setUser] = useState<User | null>(null),
    [csrf, setCsrf] = useState(""),
    [lists, setLists] = useState<List[]>([]),
    [modal, setModal] = useState<
      "login" | "register" | "reset" | "confirm" | null
    >(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(true),
    [menu, setMenu] = useState(false),
    [selected, setSelected] = useState<Game | null>(null),
    [timezone, setTimezone] = useState("America/New_York"),
    [odds, setOdds] = useState("american");
  const api = useCallback(
    async function api(path: string, options: RequestInit = {}) {
      const r = await fetch(`/api/v1${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "x-csrf-token": csrf,
          ...options.headers,
        },
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(
          typeof d.detail === "string" ? d.detail : "Please check your input.",
        );
      }
      return r.status === 204 ? null : r.json();
    },
    [csrf],
  );
  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("reset");
    if (token) {
      setResetToken(token);
      setModal("confirm");
      window.history.replaceState({}, "", window.location.pathname);
    }
    fetch("/api/v1/auth/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d) {
          setUser(d.user);
          setCsrf(d.csrf_token);
        }
      })
      .catch(() => {});
    fetch("/api/v1/data/status")
      .then((r) => {
        if (!r.ok) throw new Error("Data source status unavailable");
        return r.json();
      })
      .then(setStatus)
      .catch((e) => setError(e.message));
  }, []);
  useEffect(() => {
    let active = true;
    setLoading(true);
    fetch(`/api/v1/games?selected_date=${day}`)
      .then(async (r) => {
        if (!r.ok)
          throw new Error("Schedule unavailable. Check the API connection.");
        return r.json();
      })
      .then((d) => {
        if (active) setGames(d.items);
      })
      .catch((e) => {
        if (active) setError(e.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [day]);
  useEffect(() => {
    if (user) {
      api("/watchlists")
        .then(setLists)
        .catch((e) => setError(e.message));
      api("/settings")
        .then((d) => {
          setTimezone(d.timezone);
          setOdds(d.odds_format);
          setSport(d.sport);
        })
        .catch((e) => setError(e.message));
    } else setLists([]);
  }, [user, api]);
  function navigate(name: string) {
    setPage(name);
    if (name === "NBA" || name === "NFL") setSport(name);
    setMenu(false);
    setNotice("");
  }
  async function authenticate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      if (modal === "confirm") {
        await api("/auth/password-reset/confirm", {
          method: "POST",
          body: JSON.stringify({
            token: resetToken,
            password: form.get("password"),
          }),
        });
        setModal("login");
        setNotice("Password updated. Sign in with your new password.");
      } else if (modal === "reset") {
        await api("/auth/password-reset", {
          method: "POST",
          body: JSON.stringify({ email: form.get("email") }),
        });
        setModal(null);
        setNotice(
          "If the account exists, a reset email has been sent. In local development, check Mailpit.",
        );
      } else {
        const d = await api(`/auth/${modal}`, {
          method: "POST",
          body: JSON.stringify({
            email: form.get("email"),
            password: form.get("password"),
          }),
        });
        setUser(d.user);
        setCsrf(d.csrf_token);
        setModal(null);
        setNotice("You are signed in. Your watchlists are private.");
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function saveGame(g: Game) {
    if (!user) {
      setModal("login");
      return;
    }
    try {
      let list = lists[0];
      if (!list) {
        list = await api("/watchlists", {
          method: "POST",
          body: JSON.stringify({ name: "My research" }),
        });
      }
      await api(`/watchlists/${list.id}/items`, {
        method: "POST",
        body: JSON.stringify({ game_id: g.id }),
      });
      setLists(await api("/watchlists"));
      setNotice("Game saved to your watchlist.");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  const visible = filteredGames(games, sport, search),
    saved = new Set(lists.flatMap((l) => l.games.map((g) => g.id)));
  const time = (s: string) =>
    new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
      timeZone: timezone,
      timeZoneName: "short",
    }).format(new Date(s));
  const empty = (title: string, description: string) => (
    <div className="empty">
      <div className="empty-icon">
        <BarChart3 size={28} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      <span className="small-tag">INSUFFICIENT DATA · PHASE 1</span>
    </div>
  );
  const cards = (items: Game[]) =>
    items.map((g) => (
      <article className="game-card" key={g.id}>
        <div className="game-meta">
          <span className={`league ${g.sport.toLowerCase()}`}>{g.sport}</span>
          <span>{time(g.scheduled_at)}</span>
          <span className="demo-label">DEMO</span>
        </div>
        <div className="teams">
          <div>
            <span className="team-mark">
              {g.away_team
                .split(" ")
                .map((w) => w[0])
                .join("")}
            </span>
            <strong>{g.away_team}</strong>
            <small>Away · Record unavailable</small>
          </div>
          <span className="versus">VS</span>
          <div>
            <span className="team-mark home">
              {g.home_team
                .split(" ")
                .map((w) => w[0])
                .join("")}
            </span>
            <strong>{g.home_team}</strong>
            <small>Home · Record unavailable</small>
          </div>
        </div>
        <div className="prediction-row">
          <Activity size={15} />
          <span>Projection unavailable</span>
          <span>—</span>
        </div>
        <div className="card-footer">
          <button onClick={() => setSelected(g)}>
            View matchup <ArrowUpRight size={14} />
          </button>
          <button
            aria-label={`Save ${g.away_team} versus ${g.home_team}`}
            onClick={() => saveGame(g)}
          >
            {saved.has(g.id) ? <Check size={17} /> : <Bookmark size={17} />}
          </button>
        </div>
      </article>
    ));
  return (
    <div className="app-shell">
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <a className="brand" href="/" aria-label="Pro Edge dashboard">
          <span className="brand-icon">
            <Zap fill="currentColor" size={25} />
          </span>
          PRO<span>EDGE</span>
          <i />
        </a>
        <p className="sidebar-label">SPORTS INTELLIGENCE</p>
        <nav>
          {nav.map(([name, Icon]) => (
            <button
              className={page === name ? "active" : ""}
              onClick={() => navigate(name)}
              key={name}
            >
              <Icon size={19} />
              {name}
              {name === "Edge Finder" && <span className="new-tag">NEW</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="system-state">
            <span />
            Local demo environment<small>No live feeds connected</small>
          </div>
          <button
            className="profile"
            onClick={() => (user ? navigate("Settings") : setModal("login"))}
          >
            <span className="avatar">
              {user ? user.email[0].toUpperCase() : "P"}
            </span>
            <span>
              <b>{user ? user.email : "Your research workspace"}</b>
              <small>
                {user ? "Personal account" : "Sign in to save watchlists"}
              </small>
            </span>
            <ChevronRight size={16} />
          </button>
        </div>
      </aside>
      <main>
        <header>
          <div className="breadcrumb">
            <button
              className="mobile-menu"
              aria-label="Toggle navigation"
              onClick={() => setMenu(!menu)}
            >
              <Menu />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <b>{page}</b>
          </div>
          <div className="header-right">
            <span className="connection">
              <span />
              DEMO MODE
            </span>
            <button
              aria-label="Show data source status"
              onClick={() => navigate("Data Status")}
            >
              <Bell size={18} />
            </button>
            {user ? (
              <button
                aria-label="Sign out"
                onClick={async () => {
                  try {
                    await api("/auth/logout", { method: "POST" });
                    setUser(null);
                    setCsrf("");
                    setNotice("Signed out.");
                  } catch (e) {
                    setError((e as Error).message);
                  }
                }}
              >
                <LogOut size={18} />
              </button>
            ) : (
              <Button variant="outline" onClick={() => setModal("login")}>
                Sign in
              </Button>
            )}
          </div>
        </header>
        <div className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">THE RESEARCH ADVANTAGE</div>
              <h1>{page === "Dashboard" ? "Your edge starts here." : page}</h1>
              <p>
                {page === "Dashboard"
                  ? "A clearer view of the game. Built on data, grounded in transparency."
                  : "Explore your sports intelligence workspace."}
              </p>
            </div>
            <div className="date-control">
              <CalendarDays size={16} />
              <input
                aria-label="Selected schedule date in UTC"
                type="date"
                value={day}
                onChange={(e) => {
                  if (e.target.value) setDay(e.target.value);
                }}
              />
              <span>UTC</span>
            </div>
          </div>
          <div className="demo-banner">
            <ShieldCheck size={19} />
            <div>
              <b>Demo workspace</b>
              <span>
                {" "}
                Fictional teams and schedules for exploration. No live data,
                odds, or model predictions.
              </span>
            </div>
            <button onClick={() => navigate("Data Status")}>
              Data status <ArrowUpRight size={14} />
            </button>
          </div>
          {error && (
            <div role="alert" className="message error">
              {error}
              <button aria-label="Dismiss error" onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}
          {notice && (
            <div role="status" className="message">
              {notice}
              <button aria-label="Dismiss notice" onClick={() => setNotice("")}>
                <X size={16} />
              </button>
            </div>
          )}
          {[
            "Dashboard",
            "NBA",
            "NFL",
            "Game Predictions",
            "Matchup Analyzer",
          ].includes(page) && (
            <>
              <div className="stats-grid">
                {[
                  {
                    label: "NBA demo games",
                    value: games.filter((g) => g.sport === "NBA").length,
                    icon: Trophy,
                    foot: "Fictional schedule",
                  },
                  {
                    label: "NFL demo games",
                    value: games.filter((g) => g.sport === "NFL").length,
                    icon: Flame,
                    foot: "Fictional schedule",
                  },
                  {
                    label: "Available projections",
                    value: "—",
                    icon: Activity,
                    foot: "Awaiting historical data",
                  },
                  {
                    label: "Positive-edge opportunities",
                    value: "—",
                    icon: Zap,
                    foot: "No market odds connected",
                  },
                ].map(({ label, value, icon: Icon, foot }) => (
                  <div className="stat" key={label}>
                    <div>
                      <span>{label}</span>
                      <Icon size={18} />
                    </div>
                    <strong>{value}</strong>
                    <small>{foot}</small>
                  </div>
                ))}
              </div>
              <div className="research-layout">
                <section className="schedule">
                  <div className="section-heading">
                    <h2>
                      {page === "NBA" ? "NBA" : page === "NFL" ? "NFL" : "Game"}{" "}
                      slate <span>{visible.length}</span>
                    </h2>
                    <span className="muted">
                      {timezone.replaceAll("_", " ")}
                    </span>
                  </div>
                  <div className="filters">
                    <div className="tabs">
                      {["ALL", "NBA", "NFL"].map((s) => (
                        <button
                          key={s}
                          className={sport === s ? "selected" : ""}
                          onClick={() => setSport(s)}
                        >
                          {s === "ALL" ? "All sports" : s}
                        </button>
                      ))}
                    </div>
                    <label className="search">
                      <Search size={15} />
                      <input
                        aria-label="Search teams"
                        placeholder="Search teams…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                      />
                    </label>
                  </div>
                  {loading ? (
                    <p className="empty">Loading schedule…</p>
                  ) : visible.length ? (
                    <div className="games-grid">{cards(visible)}</div>
                  ) : (
                    empty(
                      "No games for these filters",
                      "Try another team or sport. Bundled fixtures are dated October 23, 2026, in UTC.",
                    )
                  )}
                </section>
                <aside className="insights">
                  <div className="section-heading">
                    <h2>
                      <Zap size={17} /> Research desk
                    </h2>
                    <span className="gold-dot" />
                  </div>
                  <div className="insight-body">
                    <span className="small-tag gold">
                      QUALITY BEFORE QUANTITY
                    </span>
                    <h3>Good decisions start with good data.</h3>
                    <p>
                      Projections and edges will appear when verified historical
                      statistics and matching market prices are available.
                    </p>
                    <div className="checklist">
                      <div>
                        <Check size={15} /> Transparent source tracking
                      </div>
                      <div>
                        <Check size={15} /> Explicit uncertainty
                      </div>
                      <div>
                        <Check size={15} /> No fabricated predictions
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => navigate("Data Status")}
                    >
                      Explore data readiness <ArrowUpRight size={15} />
                    </Button>
                  </div>
                  <div className="model-state">
                    <div>
                      <span className="model-icon">
                        <TrendingUp size={20} />
                      </span>
                      <h3>Model performance</h3>
                    </div>
                    <p>
                      No evaluated predictions yet. Accuracy and calibration
                      require out-of-sample results.
                    </p>
                    <button onClick={() => navigate("Model Performance")}>
                      View model readiness <ChevronRight size={15} />
                    </button>
                  </div>
                </aside>
              </div>
            </>
          )}
          {page === "Player Props" &&
            empty(
              "Player projections are not available yet",
              "The demo does not contain historical player statistics. No probabilities, hit rates, or prop lines are generated.",
            )}
          {page === "Edge Finder" &&
            empty(
              "No market prices connected",
              "Edges require a trained, evaluated model and exact matching odds. Manual odds entry and CSV ingestion are planned for Phase 5.",
            )}
          {page === "Model Performance" &&
            empty(
              "No evaluated models",
              "Chronological backtesting and calibration arrive in Phase 6. No accuracy or profitability is claimed.",
            )}
          {page === "Watchlist" && (
            <section className="panel">
              <div className="section-heading">
                <h2>Your watchlists</h2>
                {user && (
                  <Button
                    variant="outline"
                    onClick={async () => {
                      const name = window.prompt("Watchlist name");
                      if (name)
                        try {
                          await api("/watchlists", {
                            method: "POST",
                            body: JSON.stringify({ name }),
                          });
                          setLists(await api("/watchlists"));
                        } catch (e) {
                          setError((e as Error).message);
                        }
                    }}
                  >
                    New watchlist
                  </Button>
                )}
              </div>
              {!user ? (
                <div className="empty">
                  <Bookmark size={28} />
                  <h3>Keep your research together</h3>
                  <p>Sign in to save games to a private watchlist.</p>
                  <Button onClick={() => setModal("login")}>Sign in</Button>
                </div>
              ) : lists.length ? (
                lists.map((l) => (
                  <div key={l.id}>
                    <h3>{l.name}</h3>
                    {l.games.length ? (
                      <div className="games-grid">
                        {l.games.map((g) => (
                          <div key={g.id}>
                            {cards([g])}
                            <button
                              className="remove"
                              onClick={async () => {
                                try {
                                  await api(
                                    `/watchlists/${l.id}/items/${g.id}`,
                                    { method: "DELETE" },
                                  );
                                  setLists(await api("/watchlists"));
                                } catch (e) {
                                  setError((e as Error).message);
                                }
                              }}
                            >
                              Remove from watchlist
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="muted">
                        Save a game from the dashboard to this list. New game
                        saves currently use your first watchlist.
                      </p>
                    )}
                  </div>
                ))
              ) : (
                empty(
                  "Your watchlist is empty",
                  "Save a game using the bookmark icon on a matchup.",
                )
              )}
            </section>
          )}
          {page === "Settings" && (
            <section className="panel settings">
              <h2>Workspace preferences</h2>
              <p className="muted">
                Display preferences apply immediately. Sign in to persist them
                between visits.
              </p>
              <label>
                Preferred sport
                <select
                  value={sport}
                  onChange={(e) => setSport(e.target.value)}
                >
                  {["ALL", "NBA", "NFL"].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
              <label>
                Timezone
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                >
                  {[
                    "America/New_York",
                    "America/Chicago",
                    "America/Denver",
                    "America/Los_Angeles",
                    "UTC",
                  ].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
              <label>
                Odds format
                <select value={odds} onChange={(e) => setOdds(e.target.value)}>
                  <option value="american">American</option>
                  <option value="decimal">Decimal</option>
                </select>
              </label>
              <Button
                onClick={async () => {
                  if (!user) {
                    setModal("login");
                    return;
                  }
                  try {
                    await api("/settings", {
                      method: "PUT",
                      body: JSON.stringify({
                        sport,
                        timezone,
                        odds_format: odds,
                      }),
                    });
                    setNotice("Preferences saved.");
                  } catch (e) {
                    setError((e as Error).message);
                  }
                }}
              >
                Save preferences
              </Button>
              {user && (
                <p className="muted">
                  Signed in as {user.email} · {user.role}
                </p>
              )}
            </section>
          )}
          {page === "Data Status" && (
            <section className="panel">
              <h2>Data source monitoring</h2>
              <p className="muted">
                The application is operating offline. No external sports
                provider has been enabled.
              </p>
              {status?.sources.map((s) => (
                <div className="source" key={s.name}>
                  <Database />
                  <div>
                    <h3>
                      {s.name} <span className="small-tag">{s.status}</span>
                    </h3>
                    <p>{s.license_notes}</p>
                    <small>
                      Last successful seed:{" "}
                      {new Date(s.last_success_at).toLocaleString("en-US", {
                        timeZone: timezone,
                      })}
                    </small>
                  </div>
                </div>
              ))}
              <p>
                Live data: unavailable · Odds: unavailable · Models: not trained
              </p>
            </section>
          )}
          <footer>
            <span>
              <ShieldCheck size={14} /> Research, with perspective.
            </span>
            <p>
              Sports analytics for informational use. Predictions are uncertain.
              No wagering or guaranteed outcomes.
            </p>
            <b>
              PRO EDGE <span> / FOUNDATION 0.1</span>
            </b>
          </footer>
        </div>
      </main>
      <nav className="bottom-nav">
        {nav
          .filter(([name]) =>
            ["Dashboard", "NBA", "NFL", "Watchlist"].includes(name),
          )
          .map(([name, Icon]) => (
            <button
              className={page === name ? "active" : ""}
              key={name}
              onClick={() => navigate(name)}
            >
              <Icon size={19} />
              <span>{name}</span>
            </button>
          ))}
        <button onClick={() => setMenu(!menu)}>
          <Menu size={19} />
          <span>More</span>
        </button>
      </nav>
      {modal && (
        <div className="overlay" onClick={() => setModal(null)}>
          <section
            role="dialog"
            aria-modal="true"
            aria-label={
              modal === "register"
                ? "Create account"
                : modal === "reset"
                  ? "Password reset"
                  : "Sign in"
            }
            className="dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="close"
              aria-label="Close dialog"
              onClick={() => setModal(null)}
            >
              <X />
            </button>
            <span className="brand-icon">
              <Zap />
            </span>
            <h2>
              {modal === "register"
                ? "Create your workspace"
                : modal === "confirm"
                  ? "Choose a new password"
                  : modal === "reset"
                    ? "Password reset"
                    : "Welcome back."}
            </h2>
            <p className="muted">
              {modal === "reset"
                ? "Request a single-use reset link by email. Local delivery uses Mailpit."
                : "Private watchlists. Clearer research."}
            </p>
            <form onSubmit={authenticate}>
              {modal !== "confirm" && (
                <label>
                  Email
                  <input
                    name="email"
                    type="email"
                    required
                    autoComplete="email"
                  />
                </label>
              )}
              {modal !== "reset" && (
                <label>
                  Password
                  <input
                    name="password"
                    type="password"
                    minLength={12}
                    maxLength={128}
                    required
                    autoComplete={
                      modal === "register" ? "new-password" : "current-password"
                    }
                  />
                  <small>At least 12 characters</small>
                </label>
              )}
              {error && (
                <p role="alert" className="form-error">
                  {error}
                </p>
              )}
              <Button disabled={busy} type="submit">
                {busy
                  ? "Please wait…"
                  : modal === "register"
                    ? "Create account"
                    : modal === "confirm"
                      ? "Update password"
                      : modal === "reset"
                        ? "Send reset link"
                        : "Sign in"}
                <ArrowUpRight size={16} />
              </Button>
            </form>
            <button
              className="text-button"
              onClick={() => {
                setModal(modal === "register" ? "login" : "register");
                setError("");
              }}
            >
              {modal === "register"
                ? "Already have an account? Sign in"
                : "New here? Create an account"}
            </button>
            {modal === "login" && (
              <button
                className="text-button"
                onClick={() => {
                  setModal("reset");
                  setError("");
                }}
              >
                Forgot password?
              </button>
            )}
          </section>
        </div>
      )}
      {selected && (
        <div className="overlay" onClick={() => setSelected(null)}>
          <section
            role="dialog"
            aria-modal="true"
            aria-label="Matchup detail"
            className="dialog matchup"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="close"
              aria-label="Close matchup"
              onClick={() => setSelected(null)}
            >
              <X />
            </button>
            <span className="small-tag">FICTIONAL DEMO · {selected.sport}</span>
            <h2>
              {selected.away_team} <span className="muted">at</span>{" "}
              {selected.home_team}
            </h2>
            <p>
              {new Date(selected.scheduled_at).toLocaleDateString("en-US", {
                timeZone: timezone,
              })}{" "}
              · {time(selected.scheduled_at)}
            </p>
            {empty(
              "Matchup data unavailable",
              "Team records, efficiency, recent form, and score projections require verified historical data.",
            )}
            <Button onClick={() => saveGame(selected)}>
              Save to watchlist <Bookmark size={16} />
            </Button>
          </section>
        </div>
      )}
    </div>
  );
}
