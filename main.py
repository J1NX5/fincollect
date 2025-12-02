import logging
import lib.logging_config
import time
from lib.jobcenter import Jobcenter

jc = Jobcenter()
jc.start()

try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    logging.info("Programm wurde manuell beendet")
    print("Ciao Kakao")
