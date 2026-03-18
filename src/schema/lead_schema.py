from pydantic import BaseModel, Field
from typing import Optional, List

class Lead(BaseModel):
    username: str
    platform: str
    content: str
    problem: str
    is_relevant: bool = Field(default=True)
    intent_score: float = Field(default=0.0)
    contact_info: Optional[str] = None
    source_link: str
    tags: List[str] = Field(default_factory=list)
    outreach_message: Optional[str] = None

    def to_dict(self):
        return self.model_dump()
