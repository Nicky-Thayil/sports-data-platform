from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from shared.db.base import Base


class F1Driver(Base):
    __tablename__ = "f1_drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(5), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)

    standings: Mapped[list["F1DriverStanding"]] = relationship(back_populates="driver")
    lap_times: Mapped[list["F1LapTime"]] = relationship(back_populates="driver")


class F1Constructor(Base):
    __tablename__ = "f1_constructors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    constructor_ref: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)


class F1Race(Base):
    __tablename__ = "f1_races"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    circuit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    race_name: Mapped[str] = mapped_column(String(100), nullable=False)
    race_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("season", "round", name="uq_f1_race_season_round"),
        Index("ix_f1_races_season", "season"),
    )

    lap_times: Mapped[list["F1LapTime"]] = relationship(back_populates="race")
    standings: Mapped[list["F1DriverStanding"]] = relationship(back_populates="race")


class F1LapTime(Base):
    __tablename__ = "f1_lap_times"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("f1_races.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("f1_drivers.id"), nullable=False)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_f1_lap_times_season", "season"),
        Index("ix_f1_lap_times_race_driver", "race_id", "driver_id"),
    )

    race: Mapped["F1Race"] = relationship(back_populates="lap_times")
    driver: Mapped["F1Driver"] = relationship(back_populates="lap_times")


class F1DriverStanding(Base):
    __tablename__ = "f1_driver_standings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("f1_races.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("f1_drivers.id"), nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("season", "race_id", "driver_id", name="uq_f1_standing_season_race_driver"),
        Index("ix_f1_driver_standings_season", "season"),
    )

    race: Mapped["F1Race"] = relationship(back_populates="standings")
    driver: Mapped["F1Driver"] = relationship(back_populates="standings")