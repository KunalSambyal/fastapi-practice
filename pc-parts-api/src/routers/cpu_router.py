from collections.abc import Sequence
from fastapi import APIRouter, Request, status
from src.controllers.cpu_controller import cpu_controller
from src.dao.cpu_dao import CpuDAO
from src.schemas.cpu_schema import Cpu

router = APIRouter(prefix="/cpus", tags=["CPU"])


@router.get(
    "",
    response_model=Sequence[Cpu],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="List all CPUs",
)
async def list_cpus() -> Sequence[Cpu]:
    """Retrieve all CPUs from the database."""
    return await CpuDAO.get_all()


@router.post(
    "",
    summary="Create or Upsert CPU",
    status_code=status.HTTP_201_CREATED,
)
async def create_cpu(request: Request):
    """Create a new CPU or update existing by prd_code."""
    return await cpu_controller(request)


@router.put(
    "",
    summary="Update CPU",
    status_code=status.HTTP_200_OK,
)
async def update_cpu(request: Request):
    """Update an existing CPU by ID."""
    return await cpu_controller(request)


@router.delete(
    "",
    summary="Delete CPU",
    status_code=status.HTTP_200_OK,
)
async def delete_cpu(request: Request):
    """Delete a CPU by ID."""
    return await cpu_controller(request)
