from src.dao.cpu_dao import CpuDAO
from src.schemas.cpu_schema import CpuBase


class CpuService:

    @staticmethod
    async def save(**data: object) -> tuple[dict[str, object], int]:
        prd_code = data.get("prd_code")
        if not prd_code:
            return {"error": "Field 'prd_code' is required"}, 400

        existing = await CpuDAO.get_by_prd_code(str(prd_code))
        cpu_schema = CpuBase(**data)

        if existing:
            cpu_schema.id = existing.id
            updated_id = await CpuDAO.update_cpu(cpu_schema)
            return {"id": updated_id, "prd_code": prd_code}, 200
        else:
            new_id = await CpuDAO.create_cpu(cpu_schema)
            return {"id": new_id, "prd_code": prd_code}, 201

    @staticmethod
    async def filter(**filters: object) -> tuple[list[dict[str, object]], int]:
        cpus = await CpuDAO.filter(**filters)
        result = [CpuBase.model_validate(c).model_dump() for c in cpus]
        return result, 200

    @staticmethod
    async def update(**data: object) -> tuple[dict[str, object], int]:
        cpu_id = data.get("id")
        if not cpu_id:
            return {"error": "Field 'id' is required for update"}, 400

        existing = await CpuDAO.get_by_id(int(cpu_id))
        if not existing:
            return {"error": f"CPU with id {cpu_id} not found"}, 404

        cpu_schema = CpuBase(**data)
        updated_id = await CpuDAO.update_cpu(cpu_schema)
        return {"id": updated_id}, 200

    @staticmethod
    async def delete(**data: object) -> tuple[dict[str, object], int]:
        cpu_id = data.get("id")
        if not cpu_id:
            return {"error": "Field 'id' is required for deletion"}, 400

        existing = await CpuDAO.get_by_id(int(cpu_id))
        if not existing:
            return {"error": f"CPU with id {cpu_id} not found"}, 404

        await CpuDAO.delete_cpu(int(cpu_id))
        return {"id": int(cpu_id)}, 200
