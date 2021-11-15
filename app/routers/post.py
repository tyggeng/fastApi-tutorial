from sqlalchemy.sql import func
from .. import models, schema, oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from typing import List, Optional


router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get('/', response_model=List[schema.PostOut])
def get_posts(db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user), limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()

    results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results


@ router.get('/{id}', response_model=schema.PostOut)
def get_post(id: int, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s;""", str(id))
    # post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Id: {id} does not exist")
        # response.status_code = status.HTTP_404_NOT_FOUND
    return post


@ router.post("/", status_code=HTTP_201_CREATED, response_model=schema.PostResponse)
def create_post(post: schema.PostCreate, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published)
    #                     VALUES (%s, %s, %s) RETURNING *;""", (post.title, post.content, post.published))

    # new_post = cursor.fetchone()
    # conn.commit()  # we need to push out the changes
    new_post = models.Post(**post.dict(), owner_id=user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@ router.delete('/{id}', status_code=HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *;", str(id))
    # post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id ==
                                        id)

    if post.first() is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail=f'ID: {id} could not be found')

    if post.first().owner_id != user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized access by id: {user.id}')
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=HTTP_204_NO_CONTENT)


@ router.put('/{id}', response_model=schema.PostResponse)
def update_post(id: int, updated: schema.PostCreate, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;""",
    #                (updated.title, updated.content, updated.published, str(id)))

    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail=f'ID: {id} could not be found')
    print(post.id, user.id)
    if post.owner_id != user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized access by id: {user.id}')

    post_query.update(updated.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
