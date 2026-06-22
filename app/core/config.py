from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Soband Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "1019"
    DB_NAME: str = "sobang_db"

    SECRET_KEY: str = "보안키"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    model_config = SettingsConfigDict (
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()