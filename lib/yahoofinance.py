import yfinance as yf

class YF_Collector:

    def __init__(self):
        pass
    #     # self.sbc = SupabaseClient()
    #     self.date_format = "%Y-%m-%d"
    #     self.date_today = datetime.today().strftime('%Y-%m-%d')
    #     self.date_yesterday = self._get_date_delta_by_days(14)

    def get_earning_by_ticker(self, symbol):
        ticker = yf.Ticker(symbol)
        data = ticker.get_calendar()
        print(data)



if __name__ == "__main__":
    clltr = YF_Collector()
    clltr.get_earning_by_ticker("IBM")