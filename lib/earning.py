import os
from dotenv import load_dotenv
import csv
import requests
from db import DBManager
from datetime import datetime, timedelta

# AAPLE, LH

class Collector:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY')
        self.api_key_2 = os.getenv('API_KEY_2')
        self.dmo = DBManager()
        self.dmo.create_earning_report_table()
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.date_format = "%Y-%m-%d"
        self.current_date_obj = datetime.strptime(self.current_date, self.date_format)
        self.tmp_yesterday = self.current_date_obj - timedelta(days=1)
        self.yesterday_date = str(self.tmp_yesterday.strftime('%Y-%m-%d'))


    def get_data_by_symbol(self,symb: str):
        fetch_data = self.dmo.find_by_symbol(symb)
        return fetch_data

    def get_data_from_ec(self):
        url = f'https://financialmodelingprep.com/stable/earnings-calendar?apikey={self.api_key_2}'
        with requests.Session() as s:
            data = s.get(url).json()
            for d in range(0,len(data)):
                tmp_data = self.dmo.find_by_symbol(data[d]['symbol'])
                if  tmp_data == None:
                    self.dmo.insert_earning_report( data[d]['symbol'],data[d]['date'],data[d]['epsActual'],data[d]['epsEstimated'],data[d]['revenueActual'], data[d]['revenueEstimated'], data[d]['lastUpdated'], str(self.current_date), 1)

    def get_hist_data(self):
        s_in_db = self.dmo.find_symbol_list()
        for d in range(0,len(s_in_db)):
            self._get_hist_earning_by_symbol(s_in_db[d][0])

    def _get_hist_earning_by_symbol(self, symb: str):
        url = f'https://financialmodelingprep.com/stable/earnings?symbol={symb}&apikey={self.api_key_2}'
        tmp_data = self.dmo.find_by_symbol(symb)
        # print(f'Das Symbol:{symb} hat {len(tmp_data)} Datensätze')
        with requests.Session() as s:
            try:
                data = s.get(url).json()
                for d in range(0,len(data)):
                    # print(f'Das Symbol:{data[d]['symbol']} hat {len(tmp_data)} Datensätze')
                    if  tmp_data is None or len(tmp_data) < 10:
                        self.dmo.insert_earning_report( data[d]['symbol'],data[d]['date'],data[d]['epsActual'],data[d]['epsEstimated'],data[d]['revenueActual'], data[d]['revenueEstimated'], data[d]['lastUpdated'], str(self.current_date), 1)
            except Exception as e:
                print(f'Error {e}')

    def _get_earning_by_symbol_from_watch(self, symb: str):
        url = f'https://financialmodelingprep.com/stable/earnings?symbol={symb}&limit=5&apikey={self.api_key_2}'
        with requests.Session() as s:
            try:
                data = s.get(url).json()
                for d in range(0,len(data)):
                    self.dmo.insert_earning_report( data[d]['symbol'],data[d]['date'],data[d]['epsActual'],data[d]['epsEstimated'],data[d]['revenueActual'], data[d]['revenueEstimated'], data[d]['lastUpdated'], str(self.current_date), 1)
            except Exception as e:
                print(f'Error {e}')

    def get_earning_report_by_range(self, _from: str, _to: str):
            url = f'https://financialmodelingprep.com/stable/earnings-calendar?from={_from}&to={_to}&apikey={self.api_key_2}'
            with requests.Session() as s:
                data = s.get(url).json()
                print(data)
                for d in range(0,len(data)):
                    cow = self.dmo.check_onwait(data[d]['symbol'],data[d]['date'], 1)
                    if cow == None:
                        self.dmo.insert_earning_report( data[d]['symbol'],data[d]['date'],data[d]['epsActual'],data[d]['epsEstimated'],data[d]['revenueActual'], data[d]['revenueEstimated'], data[d]['lastUpdated'], str(self.current_date), 1)
                    else:
                        self.update_report( data[d]['symbol'],data[d]['date'],data[d]['epsActual'],data[d]['epsEstimated'],data[d]['revenueActual'], data[d]['revenueEstimated'], data[d]['lastUpdated'], str(self.current_date), 1)

    def update_report(self, symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, call_date, active: int) -> bool:
        try:
            self.dmo.update_dataset_by_symbol_date_active(symbol, date, eps_actual, eps_estimated, revenue_actual, revenue_estimated, last_updated, self.current_date, active)
        except Exception as e:
            print(f'Error: {e}')
        return True

    def watch_symbol(self, symbol: str):
        try:
            self._get_earning_by_symbol(symbol)
        except Exception as e:
            return e

if __name__ == '__main__':
    clltr = Collector()
    clltr.get_earning_report_by_range(clltr.yesterday_date, clltr.current_date)
    clltr.get_hist_data()