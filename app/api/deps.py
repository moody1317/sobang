from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

def get_db_session():
    yield from get_db()

def get_current_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db_session),
):
    # 브라우저는 httpOnly 쿠키로 인증하고, Swagger/외부 API 클라이언트는 Authorization 헤더를 계속 쓸 수 있게 둘 다 허용
    token = request.cookies.get("access_token") or (credentials.credentials if credentials else None)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증에 실패했습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        firefighter_number = payload.get("sub")

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

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="임시 비밀번호입니다. 비밀번호를 먼저 변경해주세요.",
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["station_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user

def require_station_scope(admin_user: User, target_station_id: int):
    if admin_user.role == "station_admin" and admin_user.station_id != target_station_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="소속 소방서의 대원만 관리할 수 있습니다.",
        )