from .. import models, schema, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

from app import database


router = APIRouter(
    prefix="/vote",
    tags=["vote"]
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schema.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id ==
                                              vote.post_id)

    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post {vote.post_id} was not found')

    vote_query = db.query(models.Vote).filter(
        models.Vote.user_id == current_user.id, models.Vote.post_id == vote.post_id)

    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'User {current_user.id} has already voted on post {vote.post_id}')
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully upvoted"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Post {vote.post_id} was not voted')
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully deleted vote"}
