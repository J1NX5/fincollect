import os
from dotenv import load_dotenv
import csv
import requests
# from lib.db import DBManager
from lib.supabase import SupabaseClient
from datetime import datetime, timedelta

'''
This is the Collector for financialmodelingprep api.
The api is restricted in free version. 250 Calls per day and not all symbols

The collector only get the current earning reports and controll the data if not complete
'''

class FMP_Collector:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('FMP_API_KEY')
        self.sbc = SupabaseClient()
        self.date_format = "%Y-%m-%d"
        self.date_today = datetime.today().strftime('%Y-%m-%d')
        self.date_yesterday = self._get_date_delta_by_days(14)

    def _get_date_delta_by_days(self,day_delay: int) -> str:
        current_date_obj = datetime.strptime(self.date_today, self.date_format)
        tmp_yesterday = current_date_obj - timedelta(days=day_delay)
        return str(tmp_yesterday.strftime('%Y-%m-%d'))

    
    # A func which get all the earning reports by delay of 1 day
    # The func will called every day by apscheduler in main.py
    def _get_earning_reports_from_to(self,_from: str, _to: str):
        url = f'https://financialmodelingprep.com/stable/earnings-calendar?from={_from}&to={_to}&apikey={self.api_key}'
        with requests.Session() as s:
            data = s.get(url).json()
            for d in range(0,len(data)):
                self.sbc.insert_earning_report(
                    data[d]['symbol'],
                    data[d]['date'],
                    data[d]['epsActual'],
                    data[d]['epsEstimated'],
                    data[d]['revenueActual'], 
                    data[d]['revenueEstimated'], 
                    data[d]['lastUpdated'], 
                    str(self.date_today), 
                    0
                )

    # A func which is similar to the main concept to handle cases
    # In the func is all what is to do every day
    def job(self):
        self._get_earning_reports_from_to(self.date_yesterday, self.date_today)

    # A func which search and insert all historical data from symbols in table