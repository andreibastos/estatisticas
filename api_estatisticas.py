# coding: utf-8
import pymongo
import datetime
from sys import argv 
import bottle
from bottle import route, run, response
import json
import estatisticas
import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost')
DATABASE_NAME = os.environ.get('DATABASE_NAME', "twixplorer")
COLLECTION_NAME =  os.environ.get('COLLECTION_NAME', "estatisticas")
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
    estatistica_output = get_estatisticas(id)
    if(estatistica_output["resposta"]):
        data = estatistica_output.get("data")
        date = None
        if data:
            date = data["date"]

        if date:
            now = datetime.datetime.utcnow()
            interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)
            unix_time= int((interval - datetime.datetime(1970,1,1)).total_seconds())

            if (unix_time - date) > 0:
                estatisticas.main(id)
                estatistica_output = get_estatisticas(id)



        return json.dumps(estatistica_output, sort_keys=True, ensure_ascii=False)

    else:        
        estatisticas.main(id)
        estatistica_output = get_estatisticas(id)

    return json.dumps(estatistica_output, sort_keys=True, ensure_ascii=False)

# Route for parsing the requests with the given filter
@route('/')
@enable_cors
def default():
    return 'estatisticas/r12h'


def get_estatisticas(id):

    estatistica_output = {"resposta":False}   
    for document in estatisticas_collection.find({"_id":id }):
        if document:
            estatistica_output["data"] = document
            estatistica_output["resposta"] = True

    return estatistica_output
     

# =======================================================================
if __name__ == "__main__":
    if os.environ.get('APP_LOCATION') == 'heroku':
        run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        run(host='localhost', port=8080, debug=True, reloader=True)