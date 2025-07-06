from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: schemas.UserCreate, session: Session = Depends(get_db)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    encrypted_password = utils.get_hashed_password(user.password)
    user.password = encrypted_password

    new_user = models.User(**user.dict())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "user created successfully"}


@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username}


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    payload: schemas.PasswordChangeWithCurrent,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not utils.verify_password(payload.current_password, user.password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.password = utils.get_hashed_password(payload.new_password)
    db.commit()
    return {"msg": "Password updated successfully"}


@router.post("/change-username", status_code=status.HTTP_200_OK)
def change_username(
    payload: schemas.UsernameChange,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = payload.new_username
    db.commit()
    return {"msg": "Username updated successfully"}


@router.delete("/delete-preferences", status_code=200)
def delete_preferences(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    db.query(models.LikedMovie).filter(
        models.LikedMovie.user_id == current_user.id
    ).delete()
    db.commit()
    return {"msg": "Preferences deleted successfully."}


@router.delete("/delete-account", status_code=200)
def delete_account(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    db.query(models.LikedMovie).filter(
        models.LikedMovie.user_id == current_user.id
    ).delete()

    db.query(models.User).filter(models.User.id == current_user.id).delete()

    db.commit()

    return {"msg": "Account and preferences deleted successfully."}


@router.post("/complete-onboarding")
def complete_onboarding(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == current_user).first()
    if user:
        user.has_onboarded = True
        db.commit()
        return {"msg": "Onboarding complete"}
    raise HTTPException(status_code=404, detail="User not found")
