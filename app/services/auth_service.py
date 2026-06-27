from sqlalchemy.orm import Session

from app.core.security import create_access_token, generate_temp_password, hash_password, verify_password, check_brute_force, record_failed_attempt, clear_attempts
from app.models.user import User, UnitType
from app.schemas.user import UserCreate, ProfileUpdateRequest

from app.models.station import Station
from app.models.safety_center import SafetyCenter

def generate_firefighter_number(db: Session, station_id: int) -> str:
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise ValueError("존재하지 않는 소방서입니다.")
    
    seq = db.query(User).filter(User.station_id == station_id).count() + 1

    while True:
        candidate = f"{station.station_code}{seq:04d}"
        if not get_user_by_firefighter_number(db, candidate):
            return candidate
        seq += 1
\

def change_password(db: Session, user:User, current_password: str, new_password: str):
    if not verify_password(current_password, user.password_hash):
        raise ValueError("현재 비밀번호가 올바르지 않습니다.")
    
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    
    db.commit()
    db.refresh(user)
    return user

def get_user_by_firefighter_number(db: Session, firefighter_number: str):
    return (
        db.query(User)
        .filter(User.firefighter_number == firefighter_number)
        .first()
    )

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, firefighter_number: str, password: str):
    check_brute_force(firefighter_number)

    user = get_user_by_firefighter_number(db, firefighter_number)

    if not user or not verify_password(password, user.password_hash):
        record_failed_attempt(firefighter_number)
        return None
    
    if not user.is_active:
        return None
    
    clear_attempts(firefighter_number)
    return user

def create_user_token(user: User) -> str:
    payload = {
        "sub": user.firefighter_number,
        "user_id": user.id,
        "role": user.role,
    }

    return create_access_token(payload)

def create_user(db: Session, user_data: UserCreate) -> tuple[User, str]:
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("이미 사용 중인 이메일입니다.")

    safety_center_id = None
    if user_data.unit_type == UnitType.SAFETY_CENTER:
        if user_data.safety_center_id is not None:
            center = db.query(SafetyCenter).filter(
                SafetyCenter.id == user_data.safety_center_id,
                SafetyCenter.station_id == user_data.station_id,
            ).first()
            if not center:
                raise ValueError("선택한 안전센터가 해당 소방서 소속이 아닙니다.")
            safety_center_id = user_data.safety_center_id
                
    firefighter_number = generate_firefighter_number(db, user_data.station_id)
    temp_password = generate_temp_password()

    new_user = User(
        firefighter_number=firefighter_number,
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(temp_password),   
        role=user_data.role,
        rank=user_data.rank,
        phone_number=user_data.phone_number,
        station_id=user_data.station_id,
        unit_type=user_data.unit_type,
        safety_center_id=safety_center_id,
        is_active=True,
        must_change_password=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user, temp_password

def reset_user_password(db: Session, firefighter_number: str) -> tuple[User, str]:
    user = get_user_by_firefighter_number(db, firefighter_number)
    if not user:
        raise ValueError("존재하지 않는 대원번호입니다.")

    temp_password = generate_temp_password()
    user.password_hash = hash_password(temp_password)
    user.must_change_password = True

    db.commit()
    db.refresh(user)

    return user, temp_password

def update_profile(db: Session, user: User, data: "ProfileUpdateRequest") -> User:
    if not verify_password(data.current_password, user.password_hash):
        raise ValueError("현재 비밀번호가 올바르지 않습니다.")
    
    if data.email is not None:
        existing = get_user_by_email(db, data.email)
        if existing and existing.id != user.id:
            raise ValueError("이미 사용 중인 이메일입니다.")
        user.email = data.email

    if data.phone_number is not None:
        user.phone_number = data.phone_number
        
    db.commit()
    db.refresh(user)
    return user

def get_users_by_station(db: Session, station_id: int):
    return (
        db.query(User)
        .filter(User.station_id == station_id)
        .order_by(User.created_at.desc())
        .all()
    )