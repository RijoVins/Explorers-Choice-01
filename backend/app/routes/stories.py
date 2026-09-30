"""Public, unauthenticated customer stories.

The frontend public site needs published testimonials. These live outside the
`/api/admin` router so that they are genuinely public and so the admin router
can keep an authenticated list endpoint (which returns drafts too) without one
shadowing the other.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()


@router.get("/customer-stories", response_model=list[schemas.CustomerStoryRead])
def list_public_stories(db: Session = Depends(get_db)):
    """Published customer stories only. No authentication required."""
    return crud.list_customer_stories(db, published_only=True)


@router.get("/customer-stories/{story_id}", response_model=schemas.CustomerStoryRead)
def get_public_story(story_id: int, db: Session = Depends(get_db)):
    story = crud.get_customer_story(db, story_id)
    if story is None or not story.is_published:
        # Do not reveal the existence of unpublished drafts.
        raise HTTPException(status_code=404, detail="Story not found")
    return story
