from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# py-demo 项目根目录（config.py 位于 apps/web-service/app/core/）
PROJECT_ROOT = Path(__file__).resolve().parents[4]
ENV_FILE = PROJECT_ROOT / ".env"


def _settings_config(**kwargs) -> SettingsConfigDict:
    return SettingsConfigDict(env_file=ENV_FILE, extra="ignore", **kwargs)


class _BaseSettingsWithEnv(BaseSettings):
    model_config = _settings_config()


# 通用配置
class _CommonSettings(_BaseSettingsWithEnv):
    environment: str = "development"


# web服务配置
class _WebSettings(_BaseSettingsWithEnv):
    app_name: str = "Web Service API"  # 实际读取 WEB_APP_NAME

    model_config = _settings_config(env_prefix="WEB_")


# 数据库配置
class _DBSettings(_BaseSettingsWithEnv):
    host: str = ""
    port: str = ""
    name: str = ""
    user: str = ""
    password: str = ""

    model_config = _settings_config(env_prefix="DB_")


common_settings = _CommonSettings()
web_settings = _WebSettings()
db_settings = _DBSettings()
