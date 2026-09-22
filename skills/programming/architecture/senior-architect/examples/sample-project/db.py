import sqlite3

def get_conn():
    return sqlite3.connect("app.db")

def query(sql, params):
    conn = get_conn()
    return conn.execute(sql, params).fetchall()
