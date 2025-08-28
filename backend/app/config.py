from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    # Pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",   # don't crash if .env has extra keys
    )

    # ===== ENV FIELDS (UPPERCASE to match .env) =====
    # Database
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    DATABASE_SSL_MODE: str = Field("prefer", alias="DATABASE_SSL_MODE")

    # JWT
    JWT_SECRET: str = Field(..., alias="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = Field(None, alias="OPENAI_API_KEY")

    # Xero OAuth (optional)
    XERO_CLIENT_ID: Optional[str] = Field(None, alias="XERO_CLIENT_ID")
    XERO_CLIENT_SECRET: Optional[str] = Field(None, alias="XERO_CLIENT_SECRET")
    XERO_REDIRECT_URI: Optional[str] = Field(None, alias="XERO_REDIRECT_URI")

    # Google OAuth (optional)
    GOOGLE_CLIENT_ID: Optional[str] = Field(None, alias="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(None, alias="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = Field(None, alias="GOOGLE_REDIRECT_URI")

    # Security
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")

    # Redis / Celery
    REDIS_URL: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    WORKER_CONCURRENCY: int = Field(2, alias="WORKER_CONCURRENCY")

    # Metabase (backend may or may not use these)
    MB_SITE_URL: Optional[str] = Field(None, alias="MB_SITE_URL")
    MB_ENCRYPTION_SECRET_KEY: Optional[str] = Field(None, alias="MB_ENCRYPTION_SECRET_KEY")

    # Storage (MinIO / S3)
    STORAGE_PROVIDER: Optional[str] = Field(None, alias="STORAGE_PROVIDER")
    S3_BUCKET: Optional[str] = Field(None, alias="S3_BUCKET")
    S3_UPLOAD_PREFIX: Optional[str] = Field(None, alias="S3_UPLOAD_PREFIX")
    S3_REGION: Optional[str] = Field(None, alias="S3_REGION")
    S3_ENDPOINT_URL: Optional[str] = Field(None, alias="S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: Optional[str] = Field(None, alias="S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = Field(None, alias="S3_SECRET_ACCESS_KEY")

    # CORS
    ALLOWED_ORIGINS: str = Field(
        "http://localhost:3000,http://localhost:5173,http://localhost:8080",
        alias="ALLOWED_ORIGINS",
    )

    # ===== BACK-COMPAT PROPERTIES (lowercase accessors) =====
    # Database
    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def database_ssl_mode(self) -> str:
        return self.DATABASE_SSL_MODE

    # JWT
    @property
    def jwt_secret(self) -> str:
        return self.JWT_SECRET

    @property
    def jwt_algorithm(self) -> str:
        return self.JWT_ALGORITHM

    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def jwt_refresh_token_expire_days(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    # OpenAI / Xero / Google (optional)
    @property
    def openai_api_key(self) -> Optional[str]:
        return self.OPENAI_API_KEY

    @property
    def xero_client_id(self) -> Optional[str]:
        return self.XERO_CLIENT_ID

    @property
    def xero_client_secret(self) -> Optional[str]:
        return self.XERO_CLIENT_SECRET

    @property
    def xero_redirect_uri(self) -> Optional[str]:
        return self.XERO_REDIRECT_URI

    @property
    def google_client_id(self) -> Optional[str]:
        return self.GOOGLE_CLIENT_ID

    @property
    def google_client_secret(self) -> Optional[str]:
        return self.GOOGLE_CLIENT_SECRET

    @property
    def google_redirect_uri(self) -> Optional[str]:
        return self.GOOGLE_REDIRECT_URI

    # Redis / Celery
    @property
    def redis_url(self) -> str:
        return self.REDIS_URL

    @property
    def worker_concurrency(self) -> int:
        return self.WORKER_CONCURRENCY

    # Metabase
    @property
    def mb_site_url(self) -> Optional[str]:
        return self.MB_SITE_URL

    @property
    def mb_encryption_secret_key(self) -> Optional[str]:
        return self.MB_ENCRYPTION_SECRET_KEY

    # Storage
    @property
    def storage_provider(self) -> Optional[str]:
        return self.STORAGE_PROVIDER

    @property
    def s3_bucket(self) -> Optional[str]:
        return self.S3_BUCKET

    @property
    def s3_upload_prefix(self) -> Optional[str]:
        return self.S3_UPLOAD_PREFIX

    @property
    def s3_region(self) -> Optional[str]:
        return self.S3_REGION

    @property
    def s3_endpoint_url(self) -> Optional[str]:
        return self.S3_ENDPOINT_URL

    @property
    def s3_access_key_id(self) -> Optional[str]:
        return self.S3_ACCESS_KEY_ID

    @property
    def s3_secret_access_key(self) -> Optional[str]:
        return self.S3_SECRET_ACCESS_KEY

    # CORS
    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

settings = Settings()
