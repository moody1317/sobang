from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Soband Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str
    DB_NAME: str = "sobang_db"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    STATION_API_KEY: str
    STATION_API_BASE_URL: str

    VWORLD_API_KEY: str

    POPULATION_API_KEY: str         
    POPULATION_API_BASE_URL: str = "http://apis.data.go.kr/1741000/stdgSexdAgePpltn/selectStdgSexdAgePpltn" 

    EMS_API_KEY: str
    EMS_API_BASE_URL: str = "https://www.bigdata-119.kr/fsdpApi/rest/v1/ems-incidents"

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