import os
import sys
from datetime import datetime
import re
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient, errors
from tqdm import tqdm

_i = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _i not in sys.path:
    # add parent directory to sys.path so utils module is accessible
    sys.path.insert(0, _i)
del _i  # clean up global name space
from shared_code.utils import (
    check_similarity, locate_potential_duplicate,
    insert_services, get_mongo_client
)
from shared_code.base_scraper import BaseScraper

class Summer_Meal_Sites_2020_Scraper(BaseScraper):
    def grab_data(self):
        #Get the data
        data = requests.get('https://opendata.arcgis.com/datasets/9efd2e8ba3104b88921b06fa3f70defb_0.geojson')
        data = data.json()
        data = data['features']
        new_data = []
        for item in data:
            if item['properties']:
                new_data.append(item['properties'])
        df = pd.DataFrame(new_data)

        #Extract useful cols
        df = df.drop([ 'contactFirstName', 'contactLastName', 'contactPhone',
       'sponsoringOrganization', 'startDate', 'endDate', 'daysofOperation',
       'comments', 'breakfastTime', 'lunchTime', 'snackTimeAM', 'snackTimePM',
       'dinnerSupperTime', 'mealTypesServed', 'cycleNumber', 'RecordStatus', 'FNSID', 'Created', 'Season', 'County', 'siteAddress2','ext'],
        axis = 1)

        #Removing schools, and non-homeless related resources
        filter = df['siteName'].str.contains('(school|middle|elementary|high|academy|Academy|learn|Boy|Girl|Fire|Bus|College|Apartment|Route|Magnet)', flags = re.IGNORECASE)
        df = df[~filter]
        df = df.reset_index()
        df = df.drop(['OBJECTID','index'], axis = 1)

        #fix address
        df['siteAddress'].str.split(',').str[0]

        #fix phone number
        df['sitePhone'] = df['sitePhone'].apply(lambda x: "({})-{}-{}".format(x[0:3],x[3:6],x[6:10]))

        return super().grab_data(df = df)

    def scrape_updated_date(self):
        data = requests.get('https://opendata.arcgis.com/datasets/9efd2e8ba3104b88921b06fa3f70defb_0.geojson')
        data = data.headers
        data = data['x-amz-meta-contentlastmodified']
        return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ')  #Should I add that it is 'UTC' somehow?


scraper = Summer_Meal_Sites_2020_Scraper(
    source="Summer_Meal_Sites_2020_Scraper",
    data_url = 'https://opendata.arcgis.com/datasets/9efd2e8ba3104b88921b06fa3f70defb_0.geojson',
    data_page_url = 'https://opendata.arcgis.com/datasets/9efd2e8ba3104b88921b06fa3f70defb_0.geojson',
    data_format = "DF",
    extract_usecols=None,
    drop_duplicates_columns=['siteName', 'siteAddress', 'siteZip', 'siteCity', 'siteState'],
    rename_columns={'siteName':'name', 'siteStatus':'notes','siteAddress':'address1','siteCity':'city',
    'siteState':'state','siteZip':'zip','sitePhone':'phone','Country':'country'
    },
    service_summary="Food Bank",
    check_collection="services",
    dump_collection="tmp_summer_meal_sites_2020_dump",
    dupe_collection="tmp_summer_meal_sites_2020_dupe",
    data_source_collection_name="summer_meal_sites_2020",
    collection_dupe_field='name'
    )


if __name__ == '__main__':
    client=  get_mongo_client()
    scraper.main_scraper(client)
