from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Session(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    csrf_token: Mapped[str] = mapped_column(String(128))


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("sport", "league_team_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[str] = mapped_column(String(3), index=True)
    league_team_id: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(100))
    abbreviation: Mapped[str] = mapped_column(String(8))
    demo: Mapped[bool] = mapped_column(Boolean, default=True)


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("sport", "league_player_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[str] = mapped_column(String(3), index=True)
    league_player_id: Mapped[str] = mapped_column(String(64))
    full_name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(20))
    current_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    active_status: Mapped[str] = mapped_column(String(20), default="demo")


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (UniqueConstraint("sport", "source_game_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_game_id: Mapped[str] = mapped_column(String(64))
    sport: Mapped[str] = mapped_column(String(3), index=True)
    season: Mapped[int]
    season_type: Mapped[str] = mapped_column(String(20), default="demo")
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    home_score: Mapped[int | None]
    away_score: Mapped[int | None]
    demo: Mapped[bool] = mapped_column(Boolean, default=True)


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    provider_type: Mapped[str] = mapped_column(String(30))
    source_url: Mapped[str | None] = mapped_column(String(512))
    license_notes: Mapped[str] = mapped_column(String(1000))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30))


class Watchlist(Base):
    __tablename__ = "watchlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("watchlist_id", "game_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(
        ForeignKey("watchlists.id", ondelete="CASCADE")
    )
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))


class UserPreference(Base):
    __tablename__ = "user_preferences"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)


class PasswordReset(Base):
    __tablename__ = "password_resets"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
