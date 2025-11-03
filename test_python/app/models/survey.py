from typing import Optional

from pydantic import BaseModel


class OptionModel(BaseModel):
    id: int
    name: str
    notes: str = ""


class SurveyModel(BaseModel):
    id: int
    name: str
    expires: Optional[str] = None  # store as string
    multiple: bool = False
    active: bool = False
    options: list[OptionModel]
