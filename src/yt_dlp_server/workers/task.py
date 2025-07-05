from pydantic import BaseModel


class Task(BaseModel):
    url: str