from sqlalchemy import Float, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base
from datetime import date


class Cpu(Base):
    __tablename__ = "cpus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prd_code: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    brand: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    core: Mapped[int] = mapped_column(Integer, nullable=False)
    thread: Mapped[int] = mapped_column(Integer, nullable=False)
    base_clk: Mapped[float] = mapped_column(Float, nullable=False)
    boost_clk: Mapped[float | None] = mapped_column(Float, nullable=True)
    socket: Mapped[str] = mapped_column(String, nullable=False)
    tdp: Mapped[int] = mapped_column(Integer, nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    updated_at: Mapped[date] = mapped_column(Date, nullable=False)
