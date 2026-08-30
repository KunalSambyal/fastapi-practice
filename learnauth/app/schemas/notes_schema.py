from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(..., description="Title of the note between 3-100 chracters.", max_length=100, min_length=3)
    content: str = Field(..., description="Note")

    model_config = {"from_attributes": True}


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    model_config = {"from_attributes": True}


class NoteResponse(BaseModel):
    note_id: int
    title: str
    content: str
    created_at: datetime
    user_id: int

    model_config = {"from_attributes": True}