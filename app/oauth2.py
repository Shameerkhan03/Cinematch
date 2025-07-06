from jose import JWTError, jwt
from . import schemas, models, database
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


ACCESS_TOKEN_EXPIRE_MINUTES = 1000
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception, db: Session):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")

        if id is None:
            raise credentials_exception

        if is_token_blacklisted(token, db):
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


# jis router ko login protected rakhna hai us k parameter mein get_current_user: int = Depends(oauth2.get_current_user)
# add krdengy
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could Not Validate Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_access_token(token, credentials_exception, db)


def is_token_blacklisted(token: str, db: Session) -> bool:
    return (
        db.query(models.BlacklistedToken)
        .filter(models.BlacklistedToken.token == token)
        .first()
        is not None
    )
