
class SQLHandler:
    def __init__(self):
        

    def createDatabase(self, columns):
        c = self.conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS stockdb ("
        sql += columns[0]
        sql += " PRIMARY KEY, "
        sql += ", ".join(columns[1:])
        sql += ')'

        c.execute(sql)
        sql =   """CREATE TABLE IF NOT EXISTS modifications (
                    table_name TEXT NOT NULL PRIMARY KEY ON CONFLICT REPLACE,
                    action TEXT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );"""
        c.execute(sql)

        sql =   """CREATE TRIGGER IF NOT EXISTS table1_ondelete AFTER DELETE ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','DELETE');
                END;"""
        c.execute(sql)

        c.execute(sql)

        sql =   """CREATE TRIGGER IF NOT EXISTS table1_onupdate AFTER UPDATE ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','UPDATE');
                END;"""
        c.execute(sql)

        sql =   """CREATE TRIGGER IF NOT EXISTS table1_oninsert AFTER INSERT ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','INSERT');
                END;"""
        c.execute(sql)

