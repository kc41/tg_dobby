from pydantic import BaseSettings


class AppSettings(BaseSettings):
    bot_api_key: str
    http_bind_address: str = "0.0.0.0"
    http_bind_port: int = 8094
    redis_url: str

    class Config:
        env_prefix = 'TG_BOT_'
