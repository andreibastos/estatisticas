# coding: utf-8
import pymongo
import datetime
from sys import argv 
import bottle
from bottle import route, run, response
import json

import os

MONGO_URI = os.environ.get('MONGO_URI', None)
DATABASE_NAME = os.environ.get('DATABASE_NAME', None)
COLLECTION_NAME =  os.environ.get('COLLECTION_NAME', None)
print(MONGO_URI,DATABASE_NAME, COLLECTION_NAME)


estatisticas_collection = None

#conexão com o banco de dados
try:
    client = pymongo.MongoClient(MONGO_URI) #recommended after 2.6
    db = client[DATABASE_NAME]
    estatisticas_collection = db[COLLECTION_NAME] #colection onde será salvo as estatísticas
except Exception as e:
   print(e)


bottle.debug(True)


# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
 
        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)
 
    return _enable_cors



# Route for parsing the requests with the given filter
@route('/estatisticas/<id>')
@enable_cors
def parsed(id):
    print(id) 
    estatistica = {"resposta":False}

    for document in estatisticas_collection.find({"_id":id}):
        if document:
            estatistica = {"resposta":True}
            estatistica["data"] = document
            estatistica["resposta"] = True


    return json.dumps(estatistica, sort_keys=True, ensure_ascii=False)

# Route for parsing the requests with the given filter
@route('/')
@enable_cors
def default():
    return 'estatísticas/r12h'

     

# =======================================================================
if __name__ == "__main__":
    if os.environ.get('APP_LOCATION') == 'heroku':
        run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        run(host='localhost', port=8080, debug=True)