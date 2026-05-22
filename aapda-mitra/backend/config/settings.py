from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Dict


class Settings(BaseSettings):
    # AI
    GEMINI_API_KEY: Optional[str]

    # Firebase
    FIREBASE_PROJECT_ID: Optional[str]
    FIREBASE_PRIVATE_KEY: Optional[str]
    FIREBASE_CLIENT_EMAIL: Optional[str]
    FIREBASE_DATABASE_URL: Optional[str]
    FIREBASE_SERVICE_ACCOUNT_FILE: Optional[str] = None

    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str]
    TWILIO_AUTH_TOKEN: Optional[str]
    TWILIO_PHONE_NUMBER: Optional[str]

    # SendGrid
    SENDGRID_API_KEY: Optional[str]

    # Gupshup
    GUPSHUP_API_KEY: Optional[str]
    GUPSHUP_APP_NAME: Optional[str]

    # NASA
    NASA_FIRMS_API_KEY: Optional[str]

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str]
    CLOUDINARY_API_KEY: Optional[str]
    CLOUDINARY_API_SECRET: Optional[str]

    # App
    SECRET_KEY: Optional[str]
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    # Optional Redis URL for durable queues (redis://...)
    REDIS_URL: Optional[str] = None

    # External API base URLs
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    GLOFAS_BASE_URL: str = "https://cds.climate.copernicus.eu"
    USGS_EARTHQUAKE_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    NASA_FIRMS_URL: str = "https://firms.modaps.eosdis.nasa.gov/api"

    # thresholds and constants
    SEVERITY_RED_THRESHOLD: int = 80
    SEVERITY_YELLOW_THRESHOLD: int = 50
    VERIFICATION_SCORE_VERIFIED: int = 80
    VERIFICATION_SCORE_SUSPICIOUS: int = 50
    RAINFALL_THRESHOLD_MM: float = 50.0
    EARTHQUAKE_MAGNITUDE_THRESHOLD: float = 4.0
    WIND_SPEED_CYCLONE_THRESHOLD: float = 88.0
    FIRE_CONFIDENCE_THRESHOLD: int = 80

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        # Expect a .env file located in backend/ during development
        env_file = ".env"
        case_sensitive = True

    @validator("FIREBASE_PRIVATE_KEY", pre=True)
    def fix_private_key(cls, v: Optional[str]) -> Optional[str]:
        # Some deployment systems replace newlines with literal \n
        if v is None:
            return v
        return v.replace('\\n', '\n')

    def firebase_credentials(self) -> Dict[str, str]:
        private_key = (self.FIREBASE_PRIVATE_KEY or "").replace('\\n', '\n').strip()
        return {
            "type": "service_account",
            "project_id": self.FIREBASE_PROJECT_ID or "",
            "private_key": private_key,
            "client_email": self.FIREBASE_CLIENT_EMAIL or "",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{(self.FIREBASE_CLIENT_EMAIL or '').replace('@', '%40')}",
            "universe_domain": "googleapis.com",
        }


settings = Settings()
