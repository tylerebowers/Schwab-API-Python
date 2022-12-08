import psycopg2 as psql
from psycopg2 import sql
from modules import globals


# Note that nothing here is done and probably doesnt work.

def initializeDatabase():
    globals.database = psql.connect(
        host=globals.postgresql_host,
        user=globals.postgresql_username,
        password=globals.postgresql_password,
        database="stockdata"
    )
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS stocks AUTHORIZATION {user}".format(user=sql.Identifier(globals.postgresql_username)))
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS options AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS futures AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS forex AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS forexOptions AUTHORIZATION stockbot")
    dbCursor.execute("CREATE SCHEMA IF NOT EXISTS headlines AUTHORIZATION stockbot")
    globals.database.commit()


def addQuote(ticker):
    dbCursor = globals.database.cursor()
    #dbCursor.execute("")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS stock."+ticker)
    return


def addOption(ticker):
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS options."+ticker)
    return


def addFutures(ticker):
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS futures."+ticker)
    return


def addForex(ticker):
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS forex."+ticker)
    return


def addFuturesOptions(ticker):
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS forexOptions."+ticker)
    return


def testfunc():
    dbCursor = globals.database.cursor()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS AMD (epoch VARCHAR(255), price FLOAT)")
    sql = "INSERT INTO AMD (epoch, price) VALUES (%s, %s)"
    val = (1001, None)
    dbCursor.execute(sql, val)


initializeDatabase()
#addStockToDatabase("AMD")
