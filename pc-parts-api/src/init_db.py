import asyncio
from datetime import date
from sqlalchemy import select
from src.database.base import Base
from src.database.connection import AsyncSessionFactory, async_engine
from src.models.cpu_model import Cpu

SAMPLE_CPUS = [
    Cpu(
        prd_code="AMD-7800",
        brand="AMD",
        name="Ryzen 7 7800X3D",
        core=8,
        thread=16,
        base_clk=4.2,
        boost_clk=5.0,
        socket="AM5",
        tdp=120,
        release_date=date(2023, 4, 6),
        price=449.00,
        updated_at=date.today(),
    ),
    Cpu(
        prd_code="INT-1470",
        brand="Intel",
        name="Core i7-14700K",
        core=20,
        thread=28,
        base_clk=3.4,
        boost_clk=5.6,
        socket="LGA1700",
        tdp=125,
        release_date=date(2023, 10, 17),
        price=409.00,
        updated_at=date.today(),
    ),
    Cpu(
        prd_code="AMD-7600",
        brand="AMD",
        name="Ryzen 5 7600X",
        core=6,
        thread=12,
        base_clk=4.7,
        boost_clk=5.3,
        socket="AM5",
        tdp=105,
        release_date=date(2022, 9, 27),
        price=229.00,
        updated_at=date.today(),
    ),
]


async def init_database():
    print("Connecting to database and creating tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    # Seed sample data if table is empty
    async with AsyncSessionFactory() as session:
        async with session.begin():
            stmt = select(Cpu)
            result = await session.execute(stmt)
            existing = result.scalars().all()
            if not existing:
                print("Seeding sample CPU data...")
                session.add_all(SAMPLE_CPUS)
                print("Sample data seeded successfully.")
            else:
                print(
                    f"Table already contains {len(existing)} records. Skipping seed."
                )

    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
