""" File config and settings to the project """
from dotenv import load_dotenv
from envparse import Env

env = Env()
load_dotenv()

HOME_DIRECTORY = env.str("HOME_DIRECTORY")

DB_HOST = env.str("DB_HOST")

DB_PORT_PROD = env.str("DB_PORT_PROD")
DB_NAME_PROD = env.str("DB_NAME_PROD")
DB_USER_PROD = env.str("DB_USER_PROD")
DB_PASS_PROD = env.str("DB_PASS_PROD")


# connect string to main database
PROD_DATABASE_URL = env.str(
    "PROD_DATABASE_URL",
    default=f"postgresql+asyncpg://{DB_USER_PROD}:{DB_PASS_PROD}"
    f"@{DB_HOST}:{DB_PORT_PROD}"
    f"/{DB_NAME_PROD}",
)


# connect string to test database
DB_PORT_TEST = env.str("DB_PORT_TEST")
DB_NAME_TEST = env.str("DB_NAME_TEST")
DB_USER_TEST = env.str("DB_USER_TEST")
DB_PASS_TEST = env.str("DB_PASS_TEST")

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default=f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}"
    f"@{DB_HOST}:{DB_PORT_TEST}"
    f"/{DB_NAME_TEST}",
)


ACCESS_TOKEN_EXPIRE_MINUTES = env.str("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = env.str("ALGORITHM", default="HS256")
