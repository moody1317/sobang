from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse, UserResponse
from app.services.auth_service import create_user, reset_user_password

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        new_user, temp_password = create_user(db=db, user_data=user_data)
        return UserCreateResponse(
            **UserResponse.model_validate(new_user).model_dump(),
            temp_password = temp_password,
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.post("/users/{firefighter_number}/reset-password", response_model=UserCreateResponse)
def reset_password(
    firefighter_number: str,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        user, temp_password = reset_user_password(db, firefighter_number)
        return UserCreateResponse(
            **UserResponse.model_validate(user).model_dump(),
            temp_password=temp_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))