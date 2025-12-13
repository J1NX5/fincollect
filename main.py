import logging
import time
from lib.jobcenter import Jobcenter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log.txt'), 
        logging.StreamHandler()
    ]
)

jc = Jobcenter()
jc.start()

try:
    while True:
        logging.info("fincollect is running :)")
        time.sleep(3600)
except KeyboardInterrupt:
    logging.info("Programm wurde manuell beendet")
