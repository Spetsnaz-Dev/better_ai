from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskOutput(BaseModel):
    """Output model for task responses."""
    id: str
    title: str
    description: str
    category: Optional[str] = None
    status: str
    created_at: str

    class Config:
        from_attributes = True
