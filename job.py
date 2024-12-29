import time
from pymongo import MongoClient
import os 
 
from .populate_database import main as createVectorEmeddings
from dotenv import load_dotenv 
import hashlib
from datetime import datetime
import time
load_dotenv()
 
MONGO_URI = os.getenv("MONGO_DB_URI")  
DATABASE_NAME = os.getenv("DB_NAME")  
REPORT_COLLECTION = os.getenv("REPORT_COLLECTION")  
document_collection = os.getenv("DOCUMENT_COLLECTION")
 
def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return client, db

def generate_unique_id():
 
    epoch_time_ms = str(int(time.time() * 1000))
   
    hash_object = hashlib.sha256(epoch_time_ms.encode())
    hex_dig = hash_object.hexdigest()
    
   
    unique_id = hex_dig[:16]
    
    return unique_id
 
def process_inprogress():
    
 try:   
    while True:
        client, db  = get_db()
        inprogress_docs = list(db[REPORT_COLLECTION].find({"reportStatus": "INPROGRESS"}).limit(1))
        client.close()
        
        if len(inprogress_docs) > 0:
             
            for doc in inprogress_docs:
                
                # db[REPORT_COLLECTION].update_one({"_id": doc["_id"]}, {"$set": {"reportStatus": "FINISHED"}})
                result = createVectorEmeddings(doc['fileName'])
                print(result)
                
                if "Error" in result:
                    sts = "FAILED"
                    
                if "Success" in result:
                    sts = "SUCCESS"
                client, db  = get_db()
                db[REPORT_COLLECTION].update_one({"reportId": doc["reportId"]}, {"$set": {"reportStatus": sts}})
                docsResult = db[document_collection].insert_one({ 
                "doumentId": f"D{generate_unique_id()}",
                "userMail": doc["userMail"],
                "documentName": doc['fileName'],
                "createdDate": datetime.now(),
                "doucmentStatus": "ACTIVE"
                })    
                print(docsResult,"This docs Result")
                print(f"Updated document {doc['_id']} to status 'FINISHED'.")
                break
        else:
            print("No 'INPROGRESS' documents found. Sleeping for 10 seconds.")
           
            time.sleep(10)   

        client, db  = get_db() 
        inprogress_docs = list(db[REPORT_COLLECTION].find({"reportStatus": "INPROGRESS"}))
        client.close()
        if len(inprogress_docs) == 0:
            print("No more 'INPROGRESS' documents. Waiting for new data.")
            time.sleep(10)
 except Exception as e: 
    
       print(e)
if __name__ == "__main__":
    process_inprogress()
