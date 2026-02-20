from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_url: str
    agent_api_key: str

    model_config = {"env_file": ".env"}


settings = Settings()
