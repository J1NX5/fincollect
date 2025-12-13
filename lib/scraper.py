from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd
from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log.txt'), 
        logging.StreamHandler()
    ]
)

class FinanceScraper:

    def __init__(self):

        # date_today for cvs name
        self.__date_today = datetime.today().strftime('%Y-%m-%d')

        # url of chromedriver for docker build
        self.__service = Service('/usr/local/bin/chromedriver')
        # url of chromedriver for local testing
        # self.__service = Service('/usr/bin/chromedriver')

        self.__chrome_options = Options()

        # url of browser for docker build
        self.__chrome_options.binary_location = '/usr/bin/google-chrome'
        # url of browser for local testing
        # self.__chrome_options.binary_location = '/usr/bin/chromium-browser'

        self.__chrome_options.add_argument("--headless=new")
        self.__chrome_options.add_argument("--no-sandbox")
        self.__chrome_options.add_argument("--disable-dev-shm-usage")
        # self.__chrome_options.add_argument("--headless")
        self.__chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0')
        self.__chrome_options.page_load_strategy = 'eager'
        self.__driver = webdriver.Chrome(service=self.__service, options=self.__chrome_options)
        self.__base_url = "https://finance.yahoo.com/calendar/earnings"
        self.__fin_base_url = "https://finance.yahoo.com"

    def wait(func):
        def wrapper(*args, **kwargs):
            logging.info("decorator @wait is called")
            time.sleep(2)
            return func(*args, **kwargs)
        return wrapper


    # The decorator is called befor the function is called
    @wait
    def scrape(self):
        logging.info("Start function")
        self.__driver.get(self.__base_url)
        self.__driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for(var btn of buttons) {
                if(btn.textContent.includes('Accept') || btn.textContent.includes('Alle akzeptieren')) {
                    btn.click(); break;
                }
            }
        """)
        page_string = BeautifulSoup(self.__driver.page_source, 'html.parser').find(class_="total")

        if page_string is None:
            number_of_pages = "1"
        else:
            number_of_pages = page_string.get_text(strip=True).split()[-1]

        # in earning_data is the final result
        earning_data = dict()
        for offset in range(0, int(number_of_pages)):
            try: 
                self.__driver.get(self.__base_url)
                time.sleep(2)
                soup = BeautifulSoup(self.__driver.page_source, 'html.parser')

                # The section where data exist is the only one whithout css class
                section = soup.find('section', class_=None)

                # if obj is None means find not worked
                if section is None:
                    raise Exception("Section is None")

                links = section.find_all('a', attrs={'href': re.compile(r'/quote/[A-Z]+/')})
                for l in links:
                    # at this point we need to extract the symbol from the link
                    href = l.get("href")

                    # filter symbol
                    parts = [p for p in href.split("/") if p]
                    symbol = parts[-1]

                    # write to log file which symbol current in work
                    logging.info(f'Call report for symbol: {symbol}')


                    if href and href.startswith("http"):
                        pass
                    else:
                        # print(fin_base_url + href + "financials/")
                        self.__driver.get(self.__fin_base_url + href + "financials/")
                        soup_l2 = BeautifulSoup(self.__driver.page_source, 'html.parser')

                        # catch case obj is None
                        if soup_l2 is None:
                            raise Exception("soup_l2 is None")

                        # accept cookie
                        self.__driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var btn of buttons) {
                                if(btn.textContent.includes('Quarterly')){
                                    btn.click(); break;
                                }
                            }
                        """)
                        
                        # select section where the data exist
                        section_l2 = soup_l2.find('section', class_='finContainer yf-yuwun0')

                        # catch case obj is None
                        if section_l2 is None:
                            raise Exception("section_l2 is None")
                        
                        row = section_l2.find_all(class_="row")
                        data = []
                        for r in row:
                            column = r.select("div.column")
                            values = [c.get_text(strip=True) for c in column]
                            data.append(values)
                        
                        #create struct for pandas
                        header = data[0]
                        data = data[1:]

                        #create pandasframe
                        df = pd.DataFrame(data, columns=header)

                        ## filter for data and create new frame -> only comlum 0 and 2
                        df_filtered = df.iloc[:, [0,2]]

                        #prepare fields for jsons struct
                        date_from_data = df_filtered.columns[1]
                        file_name = str(symbol + "_" + self.__date_today)

                        # create a struct for json export
                        data_struct = {
                            symbol : {
                                date_from_data : {
                                    df_filtered.iloc[i, 0]: df_filtered.iloc[i, 1] for i in range(len(df_filtered))
                                }
                            }
                        }
                        #write in file
                        with open(f'reports/{file_name}', 'w') as f:
                            json.dump(data_struct, f, indent=4)
                        time.sleep(2) 
            except Exception as e:
                logging.info(f'Error:{e}')
            time.sleep(2)
        self.__driver.quit() 
        return logging.info("function is finish and driver has quit")

if __name__ == "__main__":
    fso = FinanceScraper()
    fso.scrape()