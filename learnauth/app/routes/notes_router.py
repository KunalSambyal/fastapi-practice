from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import List

from app.auth import get_current_user
from app.database import get_db
from app.schemas.notes_schema import NoteCreate, NoteResponse, NoteUpdate
from app.models.notes_model import Note
from app.models.user_model import User

notes_router = APIRouter(prefix="/api/notes", tags=["notes"])


@notes_router.get("", response_model=List[NoteResponse], status_code=status.HTTP_200_OK)
async def get_notes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    query = select(Note).where(Note.user_id == current_user.id)
    result = (await session.execute(query)).scalars().all()

    return result


@notes_router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    new_note = Note(
        title=payload.title, content=payload.content, user_id=current_user.id
    )

    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)

    return new_note


@notes_router.put(
    "/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK
)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    query = select(Note).where(Note.note_id == note_id, Note.user_id == current_user.id)
    note = (await session.execute(query)).scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    session.add(note)
    await session.commit()
    await session.refresh(note)

    return note


@notes_router.delete(
    "/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK
)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    query = select(Note).where(Note.note_id == note_id, Note.user_id == current_user.id)
    note = (await session.execute(query)).scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    await session.delete(note)
    await session.commit()

    return note
