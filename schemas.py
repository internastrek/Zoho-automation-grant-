from pydantic import BaseModel

class GrantDetails(BaseModel):
    oppurtunity_name: str
    website: str
    type_of_oppurtunity: str
    amount: str
    submission_deadline: str
    first_draft_date: str
    description: str