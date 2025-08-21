
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    database_ssl_mode: str = "prefer"
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # OpenAI
    openai_api_key: str
    
    # Xero OAuth
    xero_client_id: str
    xero_client_secret: str
    xero_redirect_uri: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Security
    secret_key: str

    # External Auth Providers
    auth0_domain: Optional[str] = None
    auth0_audience: Optional[str] = None
    firebase_project_id: Optional[str] = None
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
