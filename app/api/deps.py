from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

def get_db_session():
    yield from get_db()

def get_current_user(
        token: str,
        db: Session = Depends(get_db_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증에 실패했습니다.",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        firefighter_number: str | None = payload.get("sub")

        if firefighter_number is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = (
        db.query(User)
        .filter(User.firefighter_number == firefighter_number)
        .first()
    )

    if user is None:
        raise credentials_exception
    
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["station_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user