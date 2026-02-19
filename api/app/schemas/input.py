from pydantic import BaseModel, Field


class TaskCreateInput(BaseModel):
    """Input model for creating a task via POST /api/tasks."""
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=2000)
