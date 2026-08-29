from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Mahadev Nifty Terminal"
    environment: str = "development"
    fyers_client_id: str = ""
    fyers_secret_key: str = ""
    fyers_redirect_uri: str = ""
    fyers_access_token: str = ""
    live_trading_enabled: bool = False
    database_url: str = "sqlite:///./terminal.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
