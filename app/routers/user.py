from .. import models, schema, utils
from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.UserOut)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)  # hash the password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{id}', response_model=schema.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User {id} not found!')

    return user
