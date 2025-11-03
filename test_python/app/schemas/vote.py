import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

class Vote(BaseModel):
    user_id: int
    survey_id: int
    option_ids: List[int]
    timestamp: Optional[str] = None  # stored as ISO string

    @validator("timestamp", pre=True, always=True)
    def set_timestamp(cls, v):
        if v is None:
            return datetime.datetime.utcnow().isoformat()
        if isinstance(v, datetime.datetime):
            return v.isoformat()
        if isinstance(v, str):
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return v
        return v

    
