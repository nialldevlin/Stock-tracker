#!./stracker/bin/python3

from screener import Screener
import pandas as pd
import sqlite3
import os

if __name__ == '__main__':
	#screener = Screener()
	#data = screener.data
	data = pd.DataFrame({'Test': [1, 2, 3], 'Test 1': [4, 5, 6], 'Test 2': [7, 8, 9]})
	
	conn = sqlite3.connect("stockdb.sqlite")
	c = conn.cursor()

	sql = "DROP TABLE IF EXISTS stockdb"
	c.execute(sql)

	sql = "CREATE TABLE stockdb ("
	for col in data.columns:
		sql += col
		sql += ", "
	sql = sql[:-1]
	sql += ')'
	c.execute(sql)
	
	data.to_sql('stockdb', con=conn, if_exists='replace')
	
