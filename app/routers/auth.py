from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
from ..oauth2 import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):

    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )

    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )

    liked_count = (
        db.query(models.LikedMovie).filter(models.LikedMovie.user_id == user.id).count()
    )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    redirect_path = "/dashboard" if liked_count >= 5 else "/onboarding"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
        "redirect": redirect_path,
    }


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):

    blacklisted = models.BlacklistedToken(token=token)
    db.add(blacklisted)
    db.commit()
    return {"message": "Successfully logged out"}
