import os, logging, pathlib, git

GIT_CURRENT_TAG: str
try:
    REPOSITORY          = git.Repo(pathlib.Path().absolute())
    GIT_CURRENT_TAG     = str(next((tag for tag in REPOSITORY.tags if tag.commit == REPOSITORY.head.commit), "v0.0.1-dev"))
except Exception as e:
    print(f'[WARN] Failed to get Git repository, error : {e}')
    GIT_CURRENT_TAG = "v0.0.1-dev"

LOG_LEVEL = {
    "critical"  : logging.CRITICAL,
    "error"     : logging.ERROR,
    "warning"   : logging.WARNING,
    "info"      : logging.INFO,
    "debug"     : logging.DEBUG
}

class AppState:
    """ Describe application variable state """
    PID: int        = os.getpid()
    PATH: str       = pathlib.Path().absolute()

    TAG: str        = GIT_CURRENT_TAG.split('-')[1]
    VERSION: list   = GIT_CURRENT_TAG[1:].split('-')[0].split(".")

    HOST: str       = os.environ.get('APP_HOST', '127.0.0.1')
    PORT: int       = int(os.environ.get('APP_PORT', 8080))

    # If is None -> logging level deactivate
    LOGGING_LEVEL   = LOG_LEVEL["debug"]
    LOGGING_ENABLE: bool  = True
    STDERR_ENABLE: bool   = True
    STDOUT_ENABLE: bool   = True

    """
    class Mode(Enum):
        DEBUG_LOCAL     = 0
        DEBUG_REMOTE    = 1
        PROD_LOCAL      = 2
        PROD_REMOTE     = 3
    """

    class Tools:
        """ Describe other package configuration """
        JSONSCHEMA_VERSION = "http://json-schema.org/draft-07/schema#"

    class Database:
        """ Describe SQL Database Credentials """
        CONN = None
        TYPE: str = "postgres"
        NAME: str = os.environ.get("DB_NAME", "tests")
        HOST: str = os.environ.get("DB_HOST", "127.0.0.1")
        PORT: int = int(os.environ.get("DB_PORT", 5432))
        USER: str = os.environ.get("DB_USER", "postgres")
        PASS: str = os.environ.get("DB_PASS", "root")
        
    class AccountToken:
        """ Describe Account token authentification controller credentials """
        TYPE: str       = 'HS256'
        SECRET: str     = 'secret'
        PUBLIC: bytes   = b''
        PRIVATE: bytes  = b''


# Apply a configuration according to the tag
if AppState.TAG in 'dev':
    AppState.LOGGING_LEVEL = logging.DEBUG
    AppState.AccountToken.TYPE = 'RS256'
    AppState.AccountToken.SECRET = 'secret'
elif AppState.TAG in 'test':
    AppState.AccountToken.TYPE = 'HS256'
    AppState.LOGGING_LEVEL = logging.DEBUG
elif AppState.TAG in ['alpha', 'beta', 'stable']:
    AppState.Database.TYPE = "postgresql"
    AppState.LOGGING_LEVEL  = logging.WARNING
    AppState.LOGGING_ENABLE = True
    AppState.STDERR_ENABLE  = False
    AppState.STDOUT_ENABLE  = False


# Detect if app is on heroku environment and apply configuration if true
if "DATABASE_URL" in os.environ:
    AppState.PORT = int(os.environ.get("PORT"))
    AppState.HOST = "0.0.0.0"
    DB_URL: str = os.environ.get("DATABASE_URL").split("://")[1]
    AppState.Database.TYPE = "postgresql"
    AppState.Database.USER = DB_URL.split(":")[0]
    AppState.Database.PORT = int(DB_URL.split(":")[2].split("/")[0])
    AppState.Database.PASS = DB_URL.split(":")[1].split("@")[0]
    AppState.Database.HOST = DB_URL.split("@")[1].split(":")[0]
    AppState.Database.NAME = DB_URL.split("/")[-1]