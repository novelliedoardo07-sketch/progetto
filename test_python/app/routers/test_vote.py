from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.routers.survey import get_survey_by_id
from app.routers.user import User
from app.schemas.vote import Vote
from app.services import vote as vote_service
from app.utils.auth import get_current_user, is_admin

router = APIRouter(prefix="/vote", tags=["vote"])


@router.post("/", response_model=Vote)
def submit_vote(vote: Vote, current_user: User = Depends(get_current_user)):
    if vote.user_id != current_user.id and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only vote for yourself")

    survey = get_survey_by_id(vote.survey_id, current_user)

    if not survey["multiple"] and len(vote.option_ids) > 1:
        raise HTTPException(
            status_code=400, detail="This survey does not allow multiple selections"
        )

    return vote_service.add_vote(vote)


@router.get("/", response_model=List[Vote])
def get_all_votes():
    return vote_service.get_all_votes()


@router.get("/survey/{survey_id}", response_model=List[Vote])
def get_votes_for_survey(survey_id: int):
    votes = vote_service.get_votes_by_survey(survey_id)
    if not votes:
        raise HTTPException(status_code=404, detail="No votes found for this survey")
    return votes


@router.get("/user/{user_id}", response_model=List[Vote])
def get_votes_by_user(user_id: int):
    votes = vote_service.get_votes_by_user(user_id)
    if not votes:
        raise HTTPException(status_code=404, detail="No votes found for this user")
    return votes
