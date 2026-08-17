from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class CpuBase(BaseModel):
    id: int | None = Field(default=None, description="Unique ID")
    prd_code: str = Field(..., description="Product unique code")
    brand: str | None = Field(default=None, description="Brand name")
    name: str = Field(..., description="CPU name")
    core: int = Field(..., gt=0, description="CPU core count")
    thread: int = Field(..., gt=0, description="CPU thread count")
    base_clk: float = Field(
        default=1.0, ge=1.0, description="CPU base clock speed in GHZ"
    )
    boost_clk: float | None = Field(
        default=None, ge=1.0, description="CPU boost clock speed in GHZ"
    )
    socket: str = Field(..., description="CPU socket type")
    tdp: int = Field(..., gt=0, description="CPU TDP in Watts")
    release_date: date | None = Field(default=None, description="CPU release date")
    price: float = Field(default=0.0, ge=0.0, description="CPU price")
    updated_at: date = Field(default_factory=date.today, description="Last update date")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "prd_code": "INT-1490",
                    "brand": "INTEL",
                    "name": "Intel Core i9-14900K",
                    "core": 24,
                    "thread": 32,
                    "base_clk": 3.2,
                    "boost_clk": 6.0,
                    "socket": "LGA1700",
                    "tdp": 125,
                    "release_date": "2023-10-17",
                    "price": 589.99,
                }
            ]
        },
    )


class Cpu(CpuBase):
    """Schema representing a complete CPU entity."""
    pass


class CpuCreate(CpuBase):
    """Schema for creating a CPU."""
    pass


class CpuResponse(CpuBase):
    """Schema for returning CPU response."""
    id: int = Field(..., description="Unique ID")
    updated_at: date = Field(..., description="Last update date")
