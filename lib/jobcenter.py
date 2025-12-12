import logging
import lib.logging_config
from apscheduler.schedulers.background import BackgroundScheduler
# from lib.financialmodelingprep import FMP_Collector
from lib.alphavantage import AV_Collector
from lib.scraper import FinanceScraper

class Jobcenter:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        # self.scheduler.add_job(self._start_scraper, 'interval', minutes=1)
        logging.log("Start scraping once for the begin")
        self._start_scraper()
        logging.log("Add job to interval")
        self.scheduler.add_job(self._start_scraper, 'interval', hours=1)

    def start(self):
        self.scheduler.start()
        return logging.info("Jobcenter hat geöffnet")

    def _start_scraper(self):
        logging.log("Build scrpaer-object")
        fso = FinanceScraper()
        logging.log("Start scrape-function on object")
        fso.scrape()
    

    # def _get_earning_report_from_fmp(self):
    #     avColl = AV_Collector()
    #     avColl.job()
    #     return logging.info("_get_earning_report_from_fmp: wurde ausgeführt!")

    
