"""Fictional fixtures. No real schedules, players, odds, or predictions."""

from datetime import UTC, datetime

from sqlalchemy import select

from .db import SessionLocal
from .models import DataSource, Game, Player, Team


def seed() -> None:
    with SessionLocal.begin() as db:
        if db.scalar(select(Team.id).limit(1)):
            return
        for sport, names in [
            ("NBA", ["Harbor Waves", "Metro Sparks", "Desert Suns", "Alpine Peaks"]),
            ("NFL", ["Coastal Hawks", "Prairie Bison", "River Foxes", "Summit Bears"]),
        ]:
            teams = []
            for index, name in enumerate(names):
                team = Team(
                    sport=sport,
                    league_team_id=f"demo-{sport}-{index}",
                    name=name,
                    abbreviation="".join(w[0] for w in name.split()),
                )
                db.add(team)
                db.flush()
                teams.append(team)
                db.add(
                    Player(
                        sport=sport,
                        league_player_id=f"demo-player-{sport}-{index}",
                        full_name=f"Demo Athlete {sport} {index + 1}",
                        position="G" if sport == "NBA" else "QB",
                        current_team_id=team.id,
                    )
                )
            for index in range(2):
                db.add(
                    Game(
                        sport=sport,
                        source_game_id=f"demo-{sport}-{index}",
                        season=2026,
                        home_team_id=teams[index * 2].id,
                        away_team_id=teams[index * 2 + 1].id,
                        scheduled_at=datetime(2026, 10, 23, 20 + index, tzinfo=UTC),
                    )
                )
        db.add(
            DataSource(
                name="Bundled fictional demo",
                provider_type="demo",
                license_notes="Original fictional fixtures for local development only. Not real sports information.",
                status="demo",
                last_success_at=datetime.now(UTC),
            )
        )


if __name__ == "__main__":
    seed()
