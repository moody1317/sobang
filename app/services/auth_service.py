from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_firefighter_number(db: Session, firefighter_number: str):
    return (
        db.query(User)
        .filter(User.firefighter_number == firefighter_number)
        .first()
    )

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, firefighter_number: str, password: str):
    user = get_user_by_firefighter_number(db, firefighter_number)

    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user

def create_user_token(user: User) -> str:
    payload = {
        "sub": user.firefighter_number,
        "user_id": user.id,
        "role": user.role,
    }

    return create_access_token(payload)

def create_user(
        db: Session,
        user_data: UserCreate,
        firefighter_number: str,
):
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("이미 사용 중인 이메일입니다.")
    
    existing_firefighter = get_user_by_firefighter_number(db, firefighter_number)
    if existing_firefighter:
        raise ValueError("이미 사용 중인 대원번호입니다.")
    
    new_user = User(
        firefighter_number=firefighter_number,
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        rank=user_data.rank,
        phone_number=user_data.phone_number,
        station_id=user_data.station_id,
        is_active=True,
        must_change_password=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user