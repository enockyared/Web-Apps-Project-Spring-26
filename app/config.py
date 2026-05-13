import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Ethiopia518210!")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "webapps_assignment4")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

    COGNITO_REGION = os.getenv("COGNITO_REGION")
    COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
    COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
}


def get_config(env: str):
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, DevelopmentConfig)