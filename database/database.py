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
                # api_message("i", f'encoding : {self._conn.encoding}')
            except psycopg2.DatabaseError as e:
                api_message("d", f'Failed to connect to PostgreSQL database, error : {e}')
                exit(0)

        api_message("d", f'Success to connect to PostgreSQL database')
        return self._conn
