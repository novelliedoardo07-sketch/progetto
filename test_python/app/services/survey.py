import json
import os
from typing import Any, Dict, List, Optional

from app.models.survey import SurveyModel
from app.schemas.survey import Option, OptionUpdate, SurveyCreate, SurveyUpdate

DATA_FILE_SURVEY = "./storage/survey.json"


def _load_survey_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE_SURVEY):
        return {"surveys": []}

    with open(DATA_FILE_SURVEY, "r") as f:
        content = f.read().strip()
        if not content:
            return {"surveys": []}

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore nel file JSON: {e}")

        # Normalize old format
        if isinstance(data, list):
            data = {"surveys": data}

        if not isinstance(data, dict) or "surveys" not in data:
            raise ValueError("Formato dati survey non valido")

        # ✅ Clean malformed options
        for survey in data["surveys"]:
            if "options" in survey:
                valid_options = []
                for opt in survey["options"]:
                    if "name" in opt and "id" in opt:
                        valid_options.append(opt)
                survey["options"] = valid_options

        return data


def _save_survey_data(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(DATA_FILE_SURVEY), exist_ok=True)
    with open(DATA_FILE_SURVEY, "w") as f:
        json.dump(data, f, indent=4)


def get_all_surveys() -> List[SurveyCreate]:
    data = _load_survey_data()
    return data.get("surveys", [])


def get_active_surveys() -> List[SurveyCreate]:
    surveys = get_all_surveys()
    return [s for s in surveys if s.get("active")]


def get_survey_by_id(survey_id: int) -> Optional[SurveyCreate]:
    surveys = get_all_surveys()
    return next((s for s in surveys if s.get("id") == survey_id), None)


def create_survey(survey: SurveyCreate) -> SurveyCreate:
    data = _load_survey_data()
    surveys = data.setdefault("surveys", [])
    max_id = max((s.get("id", 0) for s in surveys), default=0)
    survey.id = max_id + 1

    survey_data = SurveyModel.model_validate(survey.model_dump())
    surveys.append(survey_data.model_dump())
    _save_survey_data(data)
    return survey


def update_survey(survey_id: int, updates: SurveyUpdate) -> Optional[SurveyCreate]:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    survey = next((s for s in surveys if s.get("id") == survey_id), None)
    if not survey:
        return None

    updates_dict = updates.dict(exclude_unset=True)
    for key, value in updates_dict.items():
        survey[key] = value

    _save_survey_data(data)
    return SurveyCreate(**survey)


def delete_survey(survey_id: int) -> bool:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    new_surveys = [s for s in surveys if s.get("id") != survey_id]
    if len(new_surveys) == len(surveys):
        return False

    data["surveys"] = new_surveys

    # If active survey matches, reset it
    if data.get("active_survey") and data["active_survey"].get("id") == survey_id:
        data["active_survey"] = None

    _save_survey_data(data)
    return True


def activate_survey(survey_id: int) -> bool:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    found = False
    for survey in surveys:
        if survey.get("id") == survey_id:
            survey["active"] = True
            found = True
        else:
            survey["active"] = False
    if not found:
        return False

    _save_survey_data(data)
    return True


def get_options(survey_id: int) -> List[Option]:
    survey = get_survey_by_id(survey_id)
    if not survey:
        return []
    return [Option(**opt) for opt in survey.get("options", [])]


def add_option(survey_id: int, option: Option) -> Optional[Option]:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    survey = next((s for s in surveys if s.get("id") == survey_id), None)
    if not survey:
        return None

    existing_options = survey.get("options", [])
    max_option_id = max((opt.get("id", 0) for opt in existing_options), default=0)
    option.id = max_option_id + 1
    option_data = option.dict()
    existing_options.append(option_data)
    survey["options"] = existing_options
    _save_survey_data(data)
    return option


def update_option(
    survey_id: int, option_id: int, option_update: OptionUpdate
) -> Optional[dict]:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    survey = next((s for s in surveys if s.get("id") == survey_id), None)
    if not survey:
        return None

    options = survey.get("options", [])
    option = next((opt for opt in options if opt.get("id") == option_id), None)
    if not option:
        return None

    updates_dict = option_update.dict(exclude_unset=True)
    option.update(updates_dict)

    _save_survey_data(data)
    return option


def delete_option(survey_id: int, option_id: int) -> bool:
    data = _load_survey_data()
    surveys = data.get("surveys", [])
    survey = next((s for s in surveys if s.get("id") == survey_id), None)
    if not survey:
        return False

    original_len = len(survey.get("options", []))
    survey["options"] = [
        opt for opt in survey.get("options", []) if opt.get("id") != option_id
    ]
    if len(survey["options"]) == original_len:
        return False

    _save_survey_data(data)
    return True
