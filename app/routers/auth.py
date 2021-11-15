from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, utils, oauth2, schema


router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schema.Token)
def login(login_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == login_details.username).first()

    print(user.password)
    if not user or not utils.verify(login_details.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Invalid Credentials for email: {login_details.username}')

    # Create a token
    access_token = oauth2.create_access_token(data={'user_id': user.id})
    return {"access_token": access_token, "token_type": "bearer"}
