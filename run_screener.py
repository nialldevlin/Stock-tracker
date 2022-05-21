#!./stracker/bin/python3

from screener import Screener
import pandas as pd
import sqlite3
import os

if __name__ == '__main__':
	screener = Screener()
	data = screener.data
	
	conn = sqlite3.connect("stockdb.sqlite")
	c = conn.cursor()

	sql = "DROP TABLE IF EXISTS stockdb"
	c.execute(sql)

	sql = "CREATE TABLE IF EXISTS stockdb ("
	for col in data.columns:
		sql += col
		sql += ", "
	sql = sql[:-1]
	c.execute(sql)

	df.to_sql('stockdb', con=conn, if_exists='replace')
	
