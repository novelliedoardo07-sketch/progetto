import json
import os
from typing import List

from app.schemas.vote import Vote

DATA_FILE = "./storage/vote.json"


def read_votes_from_file() -> List[Vote]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        votes_data = json.load(f)
        return [Vote(**vote) for vote in votes_data]


def write_votes_to_file(votes: List[Vote]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([vote.model_dump() for vote in votes], f, indent=4)  # 🔧 CORRETTO


def add_vote(vote: Vote) -> Vote:
    votes = read_votes_from_file()
    votes.append(vote)
    write_votes_to_file(votes)
    return vote


def get_votes_by_survey(survey_id: int) -> List[Vote]:
    votes = read_votes_from_file()
    return [vote for vote in votes if vote.survey_id == survey_id]


def get_votes_by_user(user_id: int) -> List[Vote]:
    votes = read_votes_from_file()
    return [vote for vote in votes if vote.user_id == user_id]


def get_all_votes() -> List[Vote]:
    return read_votes_from_file()
