import sqlite3

class DBManager:
    def __init__(self):
        self.db_path: str = "data.db"
        self.conn = self._create_connection(self.db_path)
        self.create_earning_table_for_fmp()

    def _create_connection(self, db_file):
        connection = sqlite3.connect(db_file)
        return connection
    
    # In this section are the functions for financialmodelingprep

    def create_earning_table_for_fmp(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fmp_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                eps_actual REAL NULL,
                eps_estimated REAL NULL,
                revenue_actual INTEGER NULL,
                revenue_estimated INTEGER NULL,
                last_updated TEXT NOT NULL,
                call_date TEXT NOT NULL,
                active INTEGER DEFAULT 0
            ); 
        ''')
        # By setting unique it is not possible to have two entrys with the same symbol and date
        # Only one dataset for one date. date means date of the report
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS unique_symbol_date ON fmp_table(symbol, date);
        ''')
        return self.conn.commit()

    # A func which get the earning report in delay of 1 day
    def insert_daily_earning_report(
        self, 
        symbol: str, 
        date: str, 
        eps_actual: float, 
        eps_estimated: float, 
        revenue_actual: int, 
        revenue_estimated: int, 
        last_updated: str, 
        call_date: str, 
        active: int
        ):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO fmp_table(
                symbol,
                date,
                eps_actual,
                eps_estimated, 
                revenue_actual,
                revenue_estimated,
                last_updated,
                call_date,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (  symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active )
        ) 
        return self.conn.commit()

    # A func 

    # In this section are the functions for alphavantage


    # def insert_earning_report(self, symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active):
    #     cursor = self.conn.cursor()
    #     cursor.execute('''
    #         INSERT OR IGNORE INTO earnings (symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active)
    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    #         ''', (  symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active )
    #     ) 
    #     return self.conn.commit()

    # def update_dataset_by_symbol_date_active(self, symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active):
    #     cursor = self.conn.cursor()
    #     cursor.execute('''
    #         UPDATE earnings SET 
    #             eps_actual = ?, 
    #             eps_estimated = ?, 
    #             revenue_actual = ?, 
    #             revenue_estimated = ?, 
    #             last_updated = ?, 
    #             call_date = ?, 
    #             active = ?
    #         WHERE 
    #         symbol = ? AND date = ? AND active = ?;''', 
    #         ( eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active, symbol, date, active )
    #     )
    #     return cursor.fetchone()
    
    # def check_onwait(self, symbol, date, active: int):
    #     cursor = self.conn.cursor()
    #     cursor.execute('''
    #         SELECT * FROM earnings WHERE symbol = ? AND date = ? AND active = ?;
    #         ''', (symbol, date, active)
    #     )
    #     return cursor.fetchone()

    # # returns None if nothing found
    # def find_by_symbol(self, symbol):
    #     cursor = self.conn.cursor()
    #     cursor.execute('''
    #         SELECT * FROM earnings WHERE symbol = ?;
    #     ''', (symbol,))
    #     return cursor.fetchall()
    

    # def find_symbol_list(self):
    #     cursor = self.conn.cursor()
    #     cursor.execute('SELECT DISTINCT symbol FROM earnings;')
    #     return cursor.fetchall()