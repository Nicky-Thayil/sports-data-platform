from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from shared.db.base import Base


class PLTeam(Base):
    __tablename__ = "pl_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=True)

    home_matches: Mapped[list["PLMatch"]] = relationship(
        back_populates="home_team", foreign_keys="PLMatch.home_team_id"
    )
    away_matches: Mapped[list["PLMatch"]] = relationship(
        back_populates="away_team", foreign_keys="PLMatch.away_team_id"
    )
    standings: Mapped[list["PLStanding"]] = relationship(back_populates="team")


class PLMatch(Base):
    __tablename__ = "pl_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_match_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=True)
    home_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("pl_teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("pl_teams.id"), nullable=False)
    home_goals: Mapped[int] = mapped_column(Integer, nullable=True)
    away_goals: Mapped[int] = mapped_column(Integer, nullable=True)
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_pl_matches_season", "season"),
        Index("ix_pl_matches_date", "match_date"),
    )

    home_team: Mapped["PLTeam"] = relationship(back_populates="home_matches", foreign_keys=[home_team_id])
    away_team: Mapped["PLTeam"] = relationship(back_populates="away_matches", foreign_keys=[away_team_id])


class PLStanding(Base):
    __tablename__ = "pl_standings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("pl_teams.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    won: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    drawn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("season", "round", "team_id", name="uq_pl_standing_season_round_team"),
        Index("ix_pl_standings_season", "season"),
    )

    team: Mapped["PLTeam"] = relationship(back_populates="standings")