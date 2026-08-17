from typing import Any
from sqlalchemy import select
from src.models.cpu_model import Cpu
from src.schemas.cpu_schema import CpuBase
from src.database.helpers import create, delete_by_id, fetch_all, fetch_one, update


class CpuDAO:

    @staticmethod
    async def get_all() -> list[Cpu]:
        """Fetch all CPUs from the database."""
        query = select(Cpu)
        return await fetch_all(query)

    @staticmethod
    async def get_by_id(cpu_id: int) -> Cpu | None:
        """Fetch a single CPU by its primary key ID."""
        query = select(Cpu).where(Cpu.id == cpu_id)
        return await fetch_one(query)

    @staticmethod
    async def get_by_prd_code(prd_code: str) -> Cpu | None:
        """Fetch a single CPU by its product code."""
        query = select(Cpu).where(Cpu.prd_code == prd_code)
        return await fetch_one(query)

    @staticmethod
    async def get_by_name(name: str) -> Cpu | None:
        """Fetch a CPU with matching name."""
        query = select(Cpu).where(Cpu.name.ilike(name))
        return await fetch_one(query)

    @staticmethod
    async def get_by_brand(brand: str) -> list[Cpu]:
        """Fetch all CPUs matching a specific brand (e.g. AMD, INTEL)."""
        query = select(Cpu).where(Cpu.brand.ilike(brand))
        return await fetch_all(query)

    @staticmethod
    async def filter(**filters: Any) -> list[Cpu]:
        conditions = [
            getattr(Cpu, key) == value
            for key, value in filters.items()
            if hasattr(Cpu, key) and value is not None
        ]

        query = select(Cpu).where(*conditions)
        return await fetch_all(query)

    @staticmethod
    async def create_cpu(cpu_data: CpuBase) -> int:
        model_data = cpu_data.model_dump(exclude_unset=True)
        if "id" in model_data and model_data["id"] is None:
            del model_data["id"]
        model = Cpu(**model_data)
        return await create(model)

    @staticmethod
    async def update_cpu(cpu_data: CpuBase) -> int:
        model = Cpu(**cpu_data.model_dump(exclude_unset=True))
        return await update(model)

    @staticmethod
    async def delete_cpu(cpu_id: int) -> None:
        await delete_by_id(Cpu, record_id=cpu_id)
