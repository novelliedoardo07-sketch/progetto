from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status


from app.dependencies import get_current_user
from app.schemas.survey import Option, OptionUpdate, SurveyCreate, SurveyUpdate
from app.schemas.user import User
from app.services import survey as survey_service
from app.utils.auth import is_admin

router = APIRouter(prefix="/survey", tags=["survey"])


@router.get("/", response_model=List[SurveyCreate])
def get_active_surveys():
    active_surveys = survey_service.get_active_surveys()
    if not active_surveys:
        raise HTTPException(status_code=404, detail="No active surveys found")
    return active_surveys


@router.get("/all", response_model=List[SurveyCreate])
def get_all_surveys(current_user: Annotated[User, Depends(get_current_user)]):
    is_admin(current_user)
    return survey_service.get_all_surveys()


@router.get("/{survey_id}", response_model=SurveyCreate)
def get_survey_by_id(
    survey_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    is_admin(current_user)
    survey = survey_service.get_survey_by_id(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@router.post("/", response_model=SurveyCreate)
def create_survey(
    survey: SurveyCreate, current_user: Annotated[User, Depends(get_current_user)]
):
    is_admin(current_user)
    return survey_service.create_survey(survey)


@router.put("/{survey_id}", response_model=dict)
def update_survey(
    survey_id: int,
    updates: SurveyUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    is_admin(current_user)
    updated_survey = survey_service.update_survey(survey_id, updates)
    if not updated_survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {
        "message": f"Survey {survey_id} updated successfully",
        "survey": updated_survey,
    }


@router.delete("/{survey_id}", response_model=dict)
def delete_survey(
    survey_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    is_admin(current_user)
    deleted = survey_service.delete_survey(survey_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": f"Survey {survey_id} deleted successfully"}


@router.post("/{survey_id}/activate", response_model=dict)
def activate_survey(
    survey_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    is_admin(current_user)
    activated = survey_service.activate_survey(survey_id)
    if not activated:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": f"Survey {survey_id} activated successfully"}


@router.get("/{survey_id}/option", response_model=List[Option])
def get_options(
    survey_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    is_admin(current_user)
    options = survey_service.get_options(survey_id)
    if options is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return options


@router.post("/{survey_id}/option", response_model=dict)
def add_option(
    survey_id: int,
    option: Option,
    current_user: Annotated[User, Depends(get_current_user)],
):
    is_admin(current_user)
    new_option = survey_service.add_option(survey_id, option)
    if not new_option:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Option added successfully", "option": new_option}


@router.put("/{survey_id}/option/{option_id}", response_model=dict)
def update_option(
    survey_id: int,
    option_id: int,
    option_update: OptionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    is_admin(current_user)
    updated_option = survey_service.update_option(survey_id, option_id, option_update)
    if not updated_option:
        raise HTTPException(status_code=404, detail="Option or survey not found")
    return {"message": "Option updated successfully", "option": updated_option}


@router.delete("/{survey_id}/option/{option_id}", response_model=dict)
def delete_option(
    survey_id: int,
    option_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    is_admin(current_user)
    deleted = survey_service.delete_option(survey_id, option_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Option or survey not found")
    return {"message": f"Option {option_id} deleted from survey {survey_id}"}
