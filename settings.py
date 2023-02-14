""" File config and settings to the project """
import os

from dotenv import load_dotenv
from envparse import Env


HOME_DIRECTORY = os.environ.get("HOME_DIRECTORY")

load_dotenv()
DB_HOST = os.environ.get("DB_HOST")

DB_PORT_PROD = os.environ.get("DB_PORT_PROD")
DB_USER_PROD = os.environ.get("DB_USER_PROD")
DB_NAME_PROD = os.environ.get("DB_NAME_PROD")
DB_PASS_PROD = os.environ.get("DB_PASS_PROD")
env = Env()

# connect string to main database
PROD_DATABASE_URL = env.str(
    "PROD_DATABASE_URL",
    default=f"postgresql+asyncpg://\
    {DB_USER_PROD}:{DB_PASS_PROD}@{DB_HOST}:{DB_PORT_PROD}/{DB_NAME_PROD}",
)


# connect string to test database
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default=f"postgresql+asyncpg://\
        {DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST}:{DB_PORT_TEST}/{DB_NAME_TEST}",
)
