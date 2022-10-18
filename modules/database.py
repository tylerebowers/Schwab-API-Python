import psycopg2
from modules import globals


def initializeDatabase():
    initDatabase()


def initDatabase():
    globals.database = psycopg2.connect(
        host=globals.postgresql_host,
        user=globals.postgresql_username,
        password=globals.postgresql_password,
        database="stockbot"
    )
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS stocks AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS options AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS futures AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS forex AUTHORIZATION stockbot")
    globals.database.commit()


def addStockToDatabase(ticker):
    dbCursor = globals.database.cursor()
    #dbCursor.execute("CREATE TABLE IF NOT EXISTS stock.%s", ticker)
    return

def testfunc():
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS AMD (epoch VARCHAR(255), price FLOAT)")
    sql = "INSERT INTO AMD (epoch, price) VALUES (%s, %s)"
    val = (1001, None)
    dbCursor.execute(sql, val)


initializeDatabase()
#addStockToDatabase("AMD")
