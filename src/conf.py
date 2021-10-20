from pydantic import BaseSettings, HttpUrl, root_validator


class MilvusSettings(BaseSettings):
    host: str
    port: int
    collection_nm: str
    timeout: int = 5  # 5 seconds for timeout
    connection_pool_size: int = 100
    base_url: HttpUrl = None

    @root_validator(skip_on_failure=True, allow_reuse=True)
    def initialize_base_url(cls, values):
        return {
            **values,
            "base_url": f"http://{values['host']}:{values['port']}",
        }

    class Config:
        env_prefix = "APP_MILVUS_"


class Settings(BaseSettings):
    milvus: MilvusSettings = MilvusSettings()


settings: Settings = Settings()
