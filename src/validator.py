from pydantic import BaseModel
from typing import Optional


class Task(BaseModel):
    description: Optional[str]


