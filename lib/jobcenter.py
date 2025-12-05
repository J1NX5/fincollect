import logging
import lib.logging_config
from apscheduler.schedulers.background import BackgroundScheduler
# from lib.financialmodelingprep import FMP_Collector
from lib.alphavantage import AV_Collector

class Jobcenter:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._get_earning_report_from_fmp, 'interval', minutes=1)

    def _get_earning_report_from_fmp(self):
        avColl = AV_Collector()
        avColl.job()
        return logging.info("_get_earning_report_from_fmp: wurde ausgeführt!")

    def start(self):
        self.scheduler.start()
        return logging.info("Jobcenter hat geöffnet")
