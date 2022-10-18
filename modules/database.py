"""
import psycopg2
from modules import globals


def initializeDatabase():
    globals.database = psycopg2.connect(
        host=globals.postgresql_host,
        user=globals.postgresql_username,
        password=globals.postgresql_password,
        database="stockbot"
    )
    dbCursor = globals.database.cursor()
"""
