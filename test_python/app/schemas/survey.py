import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Option(BaseModel):
    id: Optional[int] = None
    name: str
    notes: str = ""


class OptionUpdate(BaseModel):
    votes: Optional[int] = None
    notes: Optional[str] = None


class SurveyCreate(BaseModel):
    id: Optional[int] = None
    name: str
    expires: Optional[str] = None  # stored as ISO string
    multiple: bool = False
    active: bool = False
    options: List[Option] = Field(
        default_factory=lambda: [
            Option(name="Apple"),
            Option(name="Banana"),
        ]
    )

    @validator("expires", pre=True, always=True)
    def parse_expires(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime.datetime):
            return v.isoformat()
        if isinstance(v, str):
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return v
        return v


class SurveyUpdate(BaseModel):
    name: Optional[str] = None
    expires: Optional[str] = None
    multiple: Optional[bool] = None
    active: Optional[bool] = None
    options: Optional[List[OptionUpdate]] = None
import json
import os
from typing import List, Optional

from app.models.survey import OptionModel, SurveyModel
from app.schemas.survey import Option, OptionUpdate, SurveyCreate, SurveyUpdate

DATA_FILE_SURVEY = "./storage/survey.json"


def _load_survey_data():
    if not os.path.exists(DATA_FILE_SURVEY):
        return []
    with open(DATA_FILE_SURVEY, "r") as f:
        content = f.read().strip()
        if not content:
            return []
        data = json.loads(content)
        if isinstance(data, list):
            return [SurveyModel.model_validate(item) for item in data]
        if isinstance(data, dict) and "surveys" in data:
            return [SurveyModel.model_validate(item) for item in data["surveys"]]
        raise ValueError("Invalid survey data format")


def _save_survey_data(surveys):
    os.makedirs(os.path.dirname(DATA_FILE_SURVEY), exist_ok=True)
    with open(DATA_FILE_SURVEY, "w") as f:
        json.dump([survey.model_dump() for survey in surveys], f, indent=4)


def get_all_surveys() -> List[SurveyModel]:
    return _load_survey_data()


def get_active_surveys() -> List[SurveyModel]:
    return [s for s in get_all_surveys() if s.active]


def get_survey_by_id(survey_id: int) -> Optional[SurveyModel]:
    return next((s for s in get_all_surveys() if s.id == survey_id), None)


def create_survey(survey: SurveyCreate) -> SurveyModel:
    surveys = _load_survey_data()
    max_id = max((getattr(s, "id", 0) for s in surveys), default=0)
    survey_data_dict = survey.model_dump()
    survey_data_dict["id"] = max_id + 1
    survey_data = SurveyModel.model_validate(survey_data_dict)
    surveys.append(survey_data)
    _save_survey_data(surveys)
    return survey_data


def update_survey(survey_id: int, updates: SurveyUpdate) -> Optional[SurveyModel]:
    surveys = _load_survey_data()
    survey = next((s for s in surveys if s.id == survey_id), None)
    if not survey:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(survey, key, value)
    _save_survey_data(surveys)
    return survey


def delete_survey(survey_id: int) -> bool:
    surveys = _load_survey_data()
    original_len = len(surveys)
    surveys = [s for s in surveys if s.id != survey_id]

    if len(surveys) == original_len:
        return False

    _save_survey_data(surveys)
    return True


def activate_survey(survey_id: int) -> bool:
    surveys = _load_survey_data()
    found = False
    for survey in surveys:
        if survey.id == survey_id:
            survey.active = True
            found = True
        else:
            survey.active = False
    if not found:
        return False
    _save_survey_data(surveys)


def add_option(survey_id: int, option: Option) -> Optional[OptionModel]:
    surveys = _load_survey_data()
    survey = next((s for s in surveys if getattr(s, "id", None) == survey_id), None)
    if not survey:
        return None

    existing_options = getattr(survey, "options", []) or []
    max_option_id = max((getattr(opt, "id", 0) for opt in existing_options), default=0)
    option_data_dict = option.model_dump()
    option_data_dict["id"] = max_option_id + 1
    option_data = OptionModel.model_validate(option_data_dict)
    existing_options.append(option_data)
    survey.options = existing_options
    _save_survey_data(surveys)
    return option_data


def get_options(survey_id: int) -> Optional[List[OptionModel]]:
    surveys = _load_survey_data()
    survey = next((s for s in surveys if getattr(s, "id", None) == survey_id), None)
    if not survey or not getattr(survey, "options", None):
        return None
    return survey.options


def update_option(
    survey_id: int, option_id: int, option_update: OptionUpdate
) -> Optional[OptionModel]:
    surveys = _load_survey_data()
    survey = next((s for s in surveys if s.id == survey_id), None)
    if not survey or not survey.options:
        return None
    option = next((opt for opt in survey.options if opt.id == option_id), None)
    if not option:
        return None

    update_data = option_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(option, key, value)

    _save_survey_data(surveys)
    return option


def delete_option(survey_id: int, option_id: int) -> bool:
    surveys = _load_survey_data()
    survey = next((s for s in surveys if s.id == survey_id), None)
    if not survey or not survey.options:
        return False

    original_len = len(survey.options)
    survey.options = [opt for opt in survey.options if opt.id != option_id]
    if len(survey.options) == original_len:
        return False

    _save_survey_data(surveys)
    return True
