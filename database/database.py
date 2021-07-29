import psycopg2
from utils.base import api_message
from utils.config import AppState

class PGDatabase:

    def __init__(self) -> None:
        self._conn = None

    def connect(self):
        if self._conn is None:
            try:
                self._conn = psycopg2.connect(
                    host=AppState.Database.HOST,
                    user=AppState.Database.USER,
                    password=AppState.Database.PASS,
                    port=AppState.Database.PORT,
                    dbname=AppState.Database.NAME
                )
            except psycopg2.DatabaseError as e:
                api_message("d", f'Failed to connect to PostgreSQL database, error : {e}')
                raise e
            finally:
                api_message("d", f'Success to connect to PostgreSQL database')
        return self._conn

db = PGDatabase()
conn = db.connect()
