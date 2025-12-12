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
import lib.logging_config



class FinanceScraper:

    def __init__(self):

    # date_today for cvs name
        self.date_today = datetime.today().strftime('%Y-%m-%d')
        # self.service = Service('/usr/local/bin/chromedriver')
        self.service = Service('/usr/bin/chromedriver')
        self.chrome_options = Options()
        # self.chrome_options.binary_location = '/usr/bin/google-chrome'
        self.chrome_options.binary_location = '/usr/bin/chromium-browser'
        # self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0')
        self.chrome_options.page_load_strategy = 'eager'
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.base_url = "https://finance.yahoo.com/calendar/earnings"
        self.fin_base_url = "https://finance.yahoo.com"

    def scrape(self):
        self.driver.get(self.base_url)
        self.driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            for(var btn of buttons) {
                if(btn.textContent.includes('Accept') || btn.textContent.includes('Alle akzeptieren')) {
                    btn.click(); break;
                }
            }
        """)
        page_string = BeautifulSoup(self.driver.page_source, 'html.parser').find(class_="total")

        if page_string is None:
            number_of_pages = "1"
        else:
            number_of_pages = page_string.get_text(strip=True).split()[-1]

        # in earning_data is the final result
        earning_data = dict()
        for offset in range(0, int(number_of_pages)):
            try: 
                self.driver.get(self.base_url)
                time.sleep(2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                section = soup.find('section', class_='main')
                links = section.find_all('a', attrs={'href': re.compile(r'/quote/[A-Z]+/')})
                for l in links:
                    # at this point we need to extract the symbol from the link
                    href = l.get("href")

                    # filter symbol
                    parts = [p for p in href.split("/") if p]
                    symbol = parts[-1]
                    print(f'Symbol: {symbol}')

                    if href and href.startswith("http"):
                        pass
                    else:
                        # print(fin_base_url + href + "financials/")
                        self.driver.get(self.fin_base_url + href + "financials/")
                        soup_l2 = BeautifulSoup(self.driver.page_source, 'html.parser')
                        # print(soup_l2.get_text(strip=True))
                        self.driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var btn of buttons) {
                                if(btn.textContent.includes('Quarterly')){
                                    btn.click(); break;
                                }
                            }
                        """)
                        section_l2 = soup_l2.find('section', class_='finContainer yf-yuwun0')
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
                        file_name = str(symbol + "_" + self.date_today)

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
            except Exception as e:
                logging.INFO("Error in iterating sites")
            time.sleep(2) 
        return driver.quit()

if __name__ == "__main__":
    fso = FinanceScraper()
    fso.scrape()