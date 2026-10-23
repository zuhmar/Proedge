import hashlib
import secrets
import time
from collections import defaultdict, deque
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DB

from .config import settings
from .db import get_db
from .models import (
    DataSource,
    Game,
    PasswordReset,
    Player,
    Session,
    Team,
    User,
    UserPreference,
    Watchlist,
    WatchlistItem,
)

app = FastAPI(title="PRO EDGE Analytics API", version="0.1.0")
passwords = PasswordHash.recommended()
# One process local-development limiter. Production must use a shared gateway limiter.
requests: dict[str, deque] = defaultdict(deque)
DUMMY_HASH = passwords.hash("constant-time-non-user-password")


@app.middleware("http")
async def security(request: Request, call_next):
    now = time.monotonic()
    key = request.client.host if request.client else "unknown"
    bucket = requests[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    limit = 120
    if len(bucket) >= limit:
        return JSONResponse(
            {"detail": "Rate limit exceeded"},
            status_code=429,
            headers={"Retry-After": "60"},
        )
    bucket.append(now)
    origin = request.headers.get("origin")
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and origin:
        from urllib.parse import urlsplit

        if origin not in settings.allowed_origins and urlsplit(
            origin
        ).netloc != request.headers.get("host"):
            return JSONResponse(
                {"detail": "Cross-origin mutation rejected"}, status_code=403
            )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class Named(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class Item(BaseModel):
    game_id: int


class Preferences(BaseModel):
    sport: Literal["ALL", "NBA", "NFL"] = "ALL"
    timezone: str = Field(default="America/New_York", max_length=64)
    odds_format: Literal["american", "decimal"] = "american"


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def current_user(request: Request, db: DB = Depends(get_db)) -> User:
    token = request.cookies.get("proedge_session", "")
    session = db.get(Session, hash_token(token))
    if not session or session.expires_at.replace(tzinfo=UTC) <= datetime.now(UTC):
        raise HTTPException(401, "Sign in required")
    if request.method not in ("GET", "HEAD", "OPTIONS") and not secrets.compare_digest(
        request.headers.get("x-csrf-token", ""), session.csrf_token
    ):
        raise HTTPException(403, "Invalid CSRF token")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "Sign in required")
    return user


def public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "role": user.role}


def issue_session(user: User, response: Response, db: DB) -> dict:
    token, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    db.add(
        Session(
            token_hash=hash_token(token),
            user_id=user.id,
            csrf_token=csrf,
            expires_at=datetime.now(UTC) + timedelta(hours=settings.session_hours),
        )
    )
    db.commit()
    response.set_cookie(
        "proedge_session",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_hours * 3600,
        path="/",
    )
    return {"user": public_user(user), "csrf_token": csrf}


@app.get("/api/v1/health")
def health(db: DB = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok", "demo_mode": settings.demo_mode}


@app.post("/api/v1/auth/register", status_code=201)
def register(data: Credentials, response: Response, db: DB = Depends(get_db)):
    user = User(
        email=str(data.email).lower(), password_hash=passwords.hash(data.password)
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Unable to register this email") from None
    return issue_session(user, response, db)


@app.post("/api/v1/auth/login")
def login(data: Credentials, response: Response, db: DB = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    valid = passwords.verify(data.password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, "Invalid email or password")
    return issue_session(user, response, db)


@app.get("/api/v1/auth/me")
def me(request: Request, user: User = Depends(current_user), db: DB = Depends(get_db)):
    session = db.get(Session, hash_token(request.cookies["proedge_session"]))
    return {"user": public_user(user), "csrf_token": session.csrf_token}


@app.post("/api/v1/auth/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    user: User = Depends(current_user),
    db: DB = Depends(get_db),
):
    session = db.get(Session, hash_token(request.cookies["proedge_session"]))
    db.delete(session)
    db.commit()
    response.delete_cookie("proedge_session", path="/")


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    password: str = Field(min_length=12, max_length=128)


@app.post("/api/v1/auth/password-reset", status_code=202)
def reset(data: ResetRequest, db: DB = Depends(get_db)):
    import smtplib
    from email.message import EmailMessage

    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    # Probe transport for all requests so unavailable delivery does not reveal accounts.
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5) as smtp:
            if user:
                token = secrets.token_urlsafe(48)
                message = EmailMessage()
                message["Subject"] = "Reset your PRO EDGE password"
                message["From"] = settings.mail_from
                message["To"] = user.email
                message.set_content(
                    f"Reset your password within 30 minutes: {settings.web_origin}/?reset={token}\nIf you did not request this, ignore this email."
                )
                smtp.send_message(message)
                db.add(
                    PasswordReset(
                        token_hash=hash_token(token),
                        user_id=user.id,
                        expires_at=datetime.now(UTC) + timedelta(minutes=30),
                    )
                )
                db.commit()
    except (OSError, smtplib.SMTPException):
        db.rollback()
        raise HTTPException(
            503, "Password reset delivery is unavailable. Please try again later."
        ) from None
    return {"message": "If the account exists, a password reset email has been sent."}


@app.post("/api/v1/auth/password-reset/confirm", status_code=204)
def confirm_reset(data: ResetConfirm, db: DB = Depends(get_db)):
    from sqlalchemy import delete

    # Lock the one-use token to prevent concurrent re-use.
    token = db.scalar(
        select(PasswordReset)
        .where(PasswordReset.token_hash == hash_token(data.token))
        .with_for_update()
    )
    if not token or token.expires_at.replace(tzinfo=UTC) <= datetime.now(UTC):
        raise HTTPException(400, "Invalid or expired reset link")
    user = db.get(User, token.user_id)
    user.password_hash = passwords.hash(data.password)
    db.execute(delete(Session).where(Session.user_id == user.id))
    db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id))
    db.commit()


@app.get("/api/v1/sports")
def sports():
    return ["NBA", "NFL"]


def game_dict(g: Game, db: DB) -> dict:
    return {
        "id": g.id,
        "sport": g.sport,
        "home_team": db.get(Team, g.home_team_id).name,
        "away_team": db.get(Team, g.away_team_id).name,
        "scheduled_at": g.scheduled_at.replace(tzinfo=UTC).isoformat(),
        "status": g.status,
        "demo": g.demo,
        "prediction": None,
    }


@app.get("/api/v1/games")
def games(
    sport: Literal["NBA", "NFL"] | None = None,
    selected_date: date | None = None,
    offset: int = 0,
    limit: int = 50,
    db: DB = Depends(get_db),
):
    if offset < 0 or not 1 <= limit <= 100:
        raise HTTPException(422, "Invalid pagination")
    query = select(Game)
    if sport:
        query = query.where(Game.sport == sport)
    if selected_date:
        query = query.where(func.date(Game.scheduled_at) == selected_date)
    rows = db.scalars(
        query.order_by(Game.scheduled_at, Game.id).offset(offset).limit(limit)
    ).all()
    return {
        "items": [game_dict(g, db) for g in rows],
        "offset": offset,
        "limit": limit,
        "demo_mode": settings.demo_mode,
    }


@app.get("/api/v1/games/{game_id}")
def game(game_id: int, db: DB = Depends(get_db)):
    row = db.get(Game, game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    return game_dict(row, db)


@app.get("/api/v1/{sport}/teams")
def teams(sport: Literal["nba", "nfl"], db: DB = Depends(get_db)):
    return [
        {"id": t.id, "name": t.name, "abbreviation": t.abbreviation, "demo": t.demo}
        for t in db.scalars(select(Team).where(Team.sport == sport.upper()))
    ]


@app.get("/api/v1/{sport}/players")
def players(sport: Literal["nba", "nfl"], db: DB = Depends(get_db)):
    return [
        {
            "id": p.id,
            "name": p.full_name,
            "position": p.position,
            "team_id": p.current_team_id,
            "demo": True,
        }
        for p in db.scalars(select(Player).where(Player.sport == sport.upper()))
    ]


@app.get("/api/v1/data/status")
def data_status(db: DB = Depends(get_db)):
    return {
        "demo_mode": settings.demo_mode,
        "sources": [
            {
                "name": s.name,
                "status": s.status,
                "last_success_at": s.last_success_at,
                "license_notes": s.license_notes,
            }
            for s in db.scalars(select(DataSource))
        ],
        "live_data": "unavailable",
        "odds": "unavailable",
        "models": "not trained",
    }


@app.get("/api/v1/watchlists")
def watchlists(user: User = Depends(current_user), db: DB = Depends(get_db)):
    return [
        {
            "id": w.id,
            "name": w.name,
            "games": [
                game_dict(db.get(Game, i.game_id), db)
                for i in db.scalars(
                    select(WatchlistItem).where(WatchlistItem.watchlist_id == w.id)
                )
            ],
        }
        for w in db.scalars(select(Watchlist).where(Watchlist.user_id == user.id))
    ]


@app.post("/api/v1/watchlists", status_code=201)
def create_watchlist(
    data: Named, user: User = Depends(current_user), db: DB = Depends(get_db)
):
    row = Watchlist(user_id=user.id, name=data.name.strip())
    if not row.name:
        raise HTTPException(422, "Name is required")
    db.add(row)
    db.commit()
    return {"id": row.id, "name": row.name}


@app.post("/api/v1/watchlists/{list_id}/items", status_code=201)
def add_item(
    list_id: int,
    data: Item,
    user: User = Depends(current_user),
    db: DB = Depends(get_db),
):
    row = db.get(Watchlist, list_id)
    if not row or row.user_id != user.id:
        raise HTTPException(404, "Watchlist not found")
    if not db.get(Game, data.game_id):
        raise HTTPException(404, "Game not found")
    existing = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == list_id, WatchlistItem.game_id == data.game_id
        )
    )
    if not existing:
        db.add(WatchlistItem(watchlist_id=list_id, game_id=data.game_id))
        db.commit()
    return {"saved": True}


@app.delete("/api/v1/watchlists/{list_id}/items/{game_id}", status_code=204)
def remove_item(
    list_id: int,
    game_id: int,
    user: User = Depends(current_user),
    db: DB = Depends(get_db),
):
    row = db.get(Watchlist, list_id)
    if not row or row.user_id != user.id:
        raise HTTPException(404, "Watchlist not found")
    item = db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == list_id, WatchlistItem.game_id == game_id
        )
    )
    if item:
        db.delete(item)
        db.commit()


@app.get("/api/v1/settings")
def preferences(user: User = Depends(current_user), db: DB = Depends(get_db)):
    row = db.get(UserPreference, user.id)
    return row.preferences if row else Preferences().model_dump()


@app.put("/api/v1/settings")
def save_preferences(
    data: Preferences, user: User = Depends(current_user), db: DB = Depends(get_db)
):
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        ZoneInfo(data.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(422, "Unknown timezone") from None
    row = db.get(UserPreference, user.id)
    if row:
        row.preferences = data.model_dump()
    else:
        db.add(UserPreference(user_id=user.id, preferences=data.model_dump()))
    db.commit()
    return data


@app.get("/api/v1/admin/health")
def admin_health(user: User = Depends(current_user), db: DB = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(403, "Administrator role required")
    return data_status(db)
