import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv('MONGO_DB_URL')


import certifi
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def csv_to_json_convertor(self,file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True,inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)  # Use `ca` for SSL verification

            db = self.mongo_client[database]           # Select the database
            collection_obj = db[collection]            # Select the collection from the database

            result = collection_obj.insert_many(records)        # Insert the records
            # print(f"Inserted ids: {result.__acknowledged}")
            print("Connected to:", self.mongo_client.list_database_names())
            print("Collections in PRAKHARAI:", self.mongo_client["PRAKHAR_NETWORKSECURITY"].list_collection_names())



            return len(records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

        

if __name__=="__main__":
    FILE_PATH = "Network_Data\phisingData.csv"
    DATABASE = "PRAKHAR_NETWORKSECURITY"
    COLLECTION = "NetworkData"

    networkObj = NetworkDataExtract()

    records = networkObj.csv_to_json_convertor(file_path=FILE_PATH)
    # print(records)
    no_of_records = networkObj.insert_data_mongodb(records=records,database=DATABASE,collection=COLLECTION)
    print(no_of_records)


