from flask import Flask, request, jsonify
from flask_cors import CORS
import os 
from dotenv import load_dotenv 
from pymongo import MongoClient
from datetime import datetime
import time
import hashlib
from rag import getQuery
import asyncio
from bson import ObjectId

load_dotenv()
monogo_db_uri=os.getenv("MONGO_DB_URI")
db_name =os.getenv("DB_NAME")
report_collection=os.getenv("REPORT_COLLECTION")
user_collection=os.getenv("USER_COLLECTION")
document_collection = os.getenv("DOCUMENT_COLLECTION")
chat_collection = os.getenv("CHAT_COLLECTION")

def get_db():
    client = MongoClient(monogo_db_uri)
    db = client[db_name]
    return client, db

def generate_unique_id():
 
    epoch_time_ms = str(int(time.time() * 1000))
   
    hash_object = hashlib.sha256(epoch_time_ms.encode())
    hex_dig = hash_object.hexdigest()
    
   
    unique_id = hex_dig[:16]
    
    return unique_id

app = Flask(__name__)
CORS(app)
 
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
     
    if 'file' not in request.files:
        return jsonify({'Error': 'No file provided'}) 
    elif 'userMail' not in request.form:
        return jsonify({"Error":"userMail invalid"})
    
    userMail = request.form['userMail']
    pdf_file = request.files['file']
    filename = pdf_file.filename
    
    file_path = os.path.join('rag','data', filename)   
    pdf_file.save(file_path)
   
    try :
      client, db = get_db()
 
      insertData = {
         "userMail": userMail,
         "reportId":f'R{generate_unique_id()}',
         "reportStatus":"INPROGRESS",
         "fileName":filename,
         "createdDate":datetime.now()
      }
      userResult = list(db[user_collection].find({"userMail":userMail}))
      
      if len(userResult) > 0: 
       reportResult = db[report_collection].insert_one(insertData) 
       client.close()
       if reportResult.acknowledged ==True:
        return jsonify({'Success':"Entry Added!"})
       else:
        return jsonify({"Error":"Could not added a data"})
      else:
        return jsonify({"Error":"user not Exist"})
    except: 
     return jsonify({'Error': "Could not upload a pdf"})
         
@app.route('/registerUser', methods=['POST'])
def registerUser():    
  data = request.get_json()
  if "userType" not in data :
    return jsonify({"Error":"User Type Invalid 1"})
  elif "userName" not in data :
    return jsonify({"Error":"User Name Invalid"})
  elif "userPassword" not in data :
    return jsonify({"Error":"User password Invalid"})
  elif "userMail" not in data :
    return jsonify({"Error":"User mail Invalid"})
  
  Type = data.get('userType')
  name = data.get('userName')
  password = int(data.get('userPassword'))
  mail = data.get('userMail')
  
  print(Type,"This Type")
  
  print(len(Type) <3 ,"This sss" )
  print(  Type not in ["ADMIN", "USER"],"This ")
 
  if len(Type) <3 or Type not in ["ADMIN", "USER"]  :
    return jsonify({"Error":"User Type Invalid 2"})
  elif len(name) <3 or isinstance(name, str) ==False:
    return jsonify({"Error":"User name Invalid"})
  elif len(str(password)) !=6 or isinstance(password, int) ==False:
    return jsonify({"Error":"User password Invalid"})
  elif len(mail) <3 or isinstance(mail, str) ==False:
    return jsonify({"Error":"User mail Invalid"})
  
  try :
      client, db = get_db() 
      result = list(db[user_collection].find({"userMail":mail}))
      
      if len(result) == 0: 
        newUserData={
            "userType" :Type,  
            "userName": name ,
            "userPassword": password ,
            "userMail": mail  
        }
        userResult = db[user_collection].insert_one(newUserData)
        if userResult.acknowledged ==True:
         return jsonify({'Success':"Account Created!"})
        else:
         return jsonify({"Error":"Could not create a account!"})
      else:
        client.close()  
        return jsonify({"Error":"User already exist!"})
  except: 
     return jsonify({'Error': "Could not upload a pdf"})
   
@app.route('/loginUser', methods=['POST'])
def loginUser():
  data = request.get_json()
 
  if "userMail" not in data :
    return jsonify({"Error":"User mail Invalid"})
  elif "userPassword" not in data :
    return jsonify({"Error":"User password Invalid 1"})
  elif "userType" not in data :
    return jsonify({"Error":"User Type Invalid 1"})

  mail = data.get('userMail')
  password = data.get('userPassword')
  userType = data.get('userType')
  
  if len(mail) <3 or isinstance(mail, str) ==False:
    return jsonify({"Error":"User name Invalid"})
  elif len(str(password)) !=6 or isinstance(int(password), int) ==False:
    return jsonify({"Error":"User password Invalid 2"})
  elif len(userType) <3 or isinstance(userType, str) ==False:
    return jsonify({"Error":"User Type Invalid"})
  
  try :
      client, db = get_db() 
      loginResult = list(db[user_collection].find({"userMail":mail,"userType":userType},{"_id":0}))
      client.close()  
     
      if len(loginResult) > 0:   
         if loginResult[0]["userPassword"] == int(password):
          return jsonify({'Success':loginResult}) 
         else:
          return jsonify({"Error":"Passowrd not match"})
      else:
        return jsonify({"Error":"Could not get user "})
  except Exception as e: 
    
     return jsonify({'Error': "Could not get user "})

@app.route('/getDouments', methods=['POST'])
def getDouments():
 try :
  data = request.get_json()
  page = int(data.get('page', 1))  
  per_page = int(data.get('perPage', 10)) 
  queryType = data.get("type") 
  skip = (page - 1) * per_page

  if queryType == "allList": 
    userMail = data.get("userMail")
    
    if userMail is None : return jsonify({"Error":"User E-mail invalid"})

    query ={"userMail":userMail}
    projection ={"_id":0}
  elif queryType ==  "nameList":
    query ={}
    projection ={"_id":0}
  else :
    return jsonify({"Error":"Invalid Type"})  
  
  try :
      client, db = get_db() 
      docuemtnResult = list(db[document_collection].find(query,projection).skip(skip).limit(per_page))
      
      client.close()  
     
      if len(docuemtnResult) > 0:    
          return jsonify({"Success":docuemtnResult})
      else:
        return jsonify({"Error":"Could not get Document "})
  except Exception as e:  
     return jsonify({'Error': "Could not get Document "})
 except Exception as e:
     return jsonify({"Error": str(e)}), 500

@app.route('/getReportByMail', methods=['POST'])
def getReportByMail():
 try :
  data = request.get_json()
  page = int(data.get('page', 1))  
  per_page = int(data.get('perPage', 10)) 
  skip = (page - 1) * per_page
  userMail= data.get('userMail')

  if  userMail is None :
    return {"Error":"user mail invlaid"}
  
  query ={"userMail":userMail}
  projection ={"_id":0}
  
  try :
      client, db = get_db() 
      docuemtnResult = list(db[report_collection].find(query,projection).skip(skip).limit(per_page))
      
      client.close()  
      
      if len(docuemtnResult) > 0:    
          return jsonify({"Success":docuemtnResult})
      else:
        return jsonify({"Error":"Could not get data "})
  except Exception as e:  
     return jsonify({'Error': "Could not get data "})
 except Exception as e:
     return jsonify({"Error": str(e)}), 500

 
@app.route('/chatQueryByCategory', methods=['POST'])
async def chatQueryByCategory():
 try :  
  data = request.get_json()

  if "category" not in data :
    return jsonify({"Error":"Category invalid"})
  elif "query" not in data:
    return jsonify({"Error":"Query Invalid"})
  elif "userMail" not in data:
    return jsonify({"Error":"Uer Mail invalid"})
  elif "roomType" not in data:
    return jsonify({"Error":"Room Type invalid"})
   
  category = data.get("category")
  query= data.get("query")
  userMail = data.get("userMail")
  roomType = data.get("roomType")
  

  if category is None :
    return jsonify({"Error":"Category invalid"})
  elif query is None:
    return jsonify({"Error":"Query Invalid"})
  elif userMail is None:
    return jsonify({"Error":"Uer Mail invalid"})
  elif roomType is None:
    return jsonify({"Error":"Room Type invalid"})

  if roomType == "NewChat":
      if "roomName" not in data:
        return jsonify({"Error":"Room Id invalid"})
      roomName =  data.get("roomName") 
      roomId = f'RO{generate_unique_id()}'
      insertData1 ={ 
                      "chatId":f'C{generate_unique_id()}',
                      "chatType":"bot",
                      "msg":f"Hello, I'm Privec. You can now ask me anything about this {category} document!",
                      "createdDate":datetime.now()
                   }
      newData={
                "roomId" :roomId,
                "roomName":roomName,
                "category":category,
                "userMail":userMail,
                "chat":[insertData1]
              }
      client, db = get_db()
      chatResult = db[chat_collection].insert_one(newData)
      if chatResult.acknowledged ==True: 
        return jsonify({"Success":insertData1})        
      else:
        return jsonify({"Error":"Could not added a data"})
  elif roomType == "NewQuery":
      if "roomName" not in data:
        return jsonify({"Error":"Room  Name invalid"})
      roomName =  data.get("roomName")  
      roomId = f'RO{generate_unique_id()}'
      insertData = { 
        "chatId":f'C{generate_unique_id()}',
        "chatType":"user",
        "msg":query, 
        "createdDate":datetime.now()
      }
      userAnswer = getQuery(query,category)
      if "Error" in userAnswer:
        return jsonify(userAnswer)
      userAnswer = userAnswer['Success']
      insertData2 ={ 
                      "chatId":f'C{generate_unique_id()}',
                      "chatType":"bot",
                      "msg":userAnswer,
                      "createdDate":datetime.now()
                   }
      newData={
                "roomId" :roomId,
                "roomName":roomName,
                "category":category,
                "userMail":userMail,
                "chat":[insertData,insertData2]
              }
      client, db = get_db()
      chatResult = db[chat_collection].insert_one(newData)
      if chatResult.acknowledged ==True:
        # insertData2["_id"] = str(insertData2["_id"])
        return jsonify({"Success":insertData2})        
      else:
        return jsonify({"Error":"Could not added a data"})      
  elif roomType == "ExistingQuery":    
      if "roomId" not in data:
        return jsonify({"Error":"Room Id invalid"})
      roomId = data.get("roomId")
      insertData = { 
        "chatId":f'C{generate_unique_id()}',
        "chatType":"user",
        "msg":query, 
        "createdDate":datetime.now()
      }
      userAnswer = getQuery(query,category)
      if "Error" in userAnswer:
        return jsonify(userAnswer)
      userAnswer = userAnswer['Success']
      
      insertData2 = {
        "chatId":f'C{generate_unique_id()}',
        "chatType":"bot",
        "msg":userAnswer,
        "createdDate":datetime.now()
      }
      FinalChatData =  [insertData,insertData2]
      client, db = get_db() 
      chatResult = db[chat_collection].update_one({
        "userMail":userMail,
        "roomId":roomId,
        "category":category
      },{"$push": {"chat": {"$each":  FinalChatData}}}) 
      client.close()
      if chatResult.modified_count > 0:
        # insertData2["_id"] = str(insertData2["_id"])
        return jsonify({"Success":insertData2})        
      else:
        return jsonify({"Error":"Could not added a data"})
  else:
    return jsonify({"Error":"Room Type invalid"})
 except Exception as e:
  return jsonify({"Error": str(e)}) 

@app.route('/getChatRoomByMail', methods=['POST'])
async def getChatRoomByMail():
  try :
      data = request.get_json()
      userMail = data.get("userMail")
      category = data.get("category")
      
      try :
        client, db = get_db() 
        query ={"category":category,"userMail":userMail}
        projection ={"_id":0,"chat":0}
        docuemtnResult = list(db[chat_collection].find(query,projection))
        client.close() 
        if len(docuemtnResult) > 0:    
          return jsonify({"Success":docuemtnResult})
        else:
          return jsonify({"Error":"Could not get Document "})
      except Exception as e:
        return jsonify({"Error": str(e)}), 500
  except Exception as e:
      return jsonify({"Error": str(e)}), 500

@app.route('/getChatQueryByMail', methods=['POST'])
def getChatQueryByMail():
 try :
      data = request.get_json()
      userMail = data.get("userMail")
      category = data.get("category")
      page_number = data.get("page")  # Example: second page
      roomId = data.get("roomId")
      items_per_page = 10
      skip_value = (page_number - 1) * items_per_page
      try :
        client, db = get_db() 
        
        
        pipeline = [
            { 
                "$match": {
                   "roomId":roomId,
                   "userMail":userMail,
                   "category":category
                }
            },
            { 
                "$project": {
                    "chat": { "$slice": ["$chat", skip_value, items_per_page] },
                    "_id":0
                }
            }
        ]
        docuemtnResult = list(db[chat_collection].aggregate(pipeline))
        client.close() 
        if len(docuemtnResult) > 0:    
          return jsonify({"Success":docuemtnResult})
        else:
          return jsonify({"Error":"Could not get Document "})
      except Exception as e:
        return jsonify({"Error": str(e)}), 500
 except Exception as e:
      return jsonify({"Error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=6969)
   