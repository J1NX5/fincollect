import requests
import os
from dotenv import load_dotenv

class BavestCollector:

    def __init__(self):
        load_dotenv()
        

    def call_symbols(self):
        url = "https://api.bavest.co/v0/list/symbols"
        payload = { "page": 1 }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": os.getenv('BAVEST_KEY')
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)


    # get error maybe error on api side or i need a special token
    def call_earning_confirmed(self):
        url = "https://api.bavest.co/v0/calender/earnings_confirmed"

        payload = {
            "from": 1761988093,
            "to": 1764580093,
            "event": "earnings"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key":os.getenv('BAVEST_KEY')
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response)
    

if __name__ == '__main__':
    bco = BavestCollector()
    # bco.call_symbols()
    bco.call_earning_confirmed()