from pydantic import BaseModel, Field, conint, constr, validator
from typing import Optional, Required

class FilterTheatreDTO(BaseModel):
    # name: Required[str] = None
    searchTerm: Optional[str] = None
    seat_count: Optional[int] = None
    page_number: Optional[conint(ge=1)] = Field(1, description="page_number, must be >= 1")
    page_size: Optional[conint(gt=0)] = Field(10, description="page_size, must be > 0")

    @validator("status", pre=True, always=True)
    def validate_status(cls, v):
        valid_statuses = {"active", "inactive", "archived"}  # Example valid statuses
        if v and v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}.")
        return v
