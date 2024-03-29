import logging
from os import environ
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
   
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  
    
    fh = logging.FileHandler(environ.get("LOG_FILE"))
    fh.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
