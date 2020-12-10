import datetime
import logging
import json
import os
from pymongo import MongoClient, TEXT
from .irs_scraper import start
import azure.functions as func

def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    with open(context.function_directory + '/config.json', 'r') as con:
        config = json.load(con)

    conn_string = os.environ['MONGO_DB_CONNECTION_STRING']
    # temp
    logging.info("Connection string is : " + conn_string[:10])
    
    client = MongoClient(conn_string)['shelter']
    
    main(config, client, 'services', 'tmpIRS_Shri', 'tmpIRSDups_Shri')
     
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function for IRS Scraping ran at utc: %s', utc_timestamp)