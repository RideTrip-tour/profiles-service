from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # Security
    # =========================
    jwt_secret: str = "secretsecretsecretsecret"
    jwt_algorithm: str = "HS256"
    gateway_name: str = "Gate"
    debug: bool = False

    # =========================
    # Database
    # =========================
    db_host: str = Field(validation_alias="DB_PROFILE_SERVICE_HOST", default="postgres")
    db_port: int = Field(validation_alias="DB_PROFILE_SERVICE_PORT", default=5432)
    db_name: str = Field(
        validation_alias="DB_PROFILE_SERVICE_NAME", default="profile_db"
    )
    db_user: str = Field(validation_alias="DB_PROFILE_SERVICE_USER", default="user")
    db_pass: str = Field(
        validation_alias="DB_PROFILE_SERVICE_PASS", default="password123"
    )
    db_driver: str = "postgresql+asyncpg"
    test_db_name: str = Field(
        validation_alias="TEST_DB_PROFILE_SERVICE_NAME", default="profile_db_test"
    )

    # =========================
    # Config
    # =========================
    app_name: str = "profile-service"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.db_driver}://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def TEST_DATABASE_URL(self) -> str:
        return (
            f"{self.db_driver}://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.test_db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        secrets_dir="/run/secrets",
    )


settings = Settings()
