#!/root/clipper/estatisticas/bin/python
# coding: utf-8

import  pymongo, os
import datetime, time
import json, codecs
from sys import argv, exit 

#conexão com o banco de dados
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost')
DATABASE_NAME = os.environ.get('DATABASE_NAME', "twixplorer")
COLLECTION_NAME =  os.environ.get('COLLECTION_NAME', "estatisticas")

estatisticas_collection = None
#conexão com o banco de dados
try:
    client = pymongo.MongoClient(MONGO_URI) #recommended after 2.6
    db = client[DATABASE_NAME]
    estatisticas_collection = db[COLLECTION_NAME] #colection onde será salvo as estatísticas
except Exception as e:
   print(e)


#formato de data padrão, (escolhido pela equipe desenvolvimento labic para os gráficos de linha)
data_format = "%d-%m-%YT%H:%M:%S"

#variaveis globais
data_output = {}	
date_final = 0
date_inicial = 0
period = 0
config_data = {}

"""
função find_count()
query - Pesquisa a ser feita no banco de dados
field_comparator - campo no qual deseja fazer a comparação.
field_time - campo do tempo
collection_name - qual collection será feita tal pesquisa
period - tempo de quanto em quanto tempo será feito a contagem.
timestamp_ms_initial - tempo inicial da busca 
timestamp_ms_finish - tempo final da busca
"""
def find_count(query,field_comparator, field_time,collection_name, period,timestamp_ms_initial, timestamp_ms_finish):
	collection = db[collection_name] #pega a collectin desejada, exemplo: tweets, facebook_comments..	
	timestamp_ms_atual = timestamp_ms_initial ; 	
	result = {}	
	while timestamp_ms_atual < (timestamp_ms_finish):
		#pesquisa no banco de addos
		timestamp_ms_final = timestamp_ms_atual+period
		
		query[field_time] = {"$gte":timestamp_ms_atual,"$lte":timestamp_ms_final}

#		print query

		search = collection.distinct(field_comparator, query)

		#quantidade de elementos encontrados.
		count = len(search) 

		#converte a data para formato desejado
		date = convert_time(int(timestamp_ms_final/1000))
		print(date, count)

		
		#adiciona no dicionario
		result[date] = count	
		#atualiza o tempo	
		timestamp_ms_atual += period			
	#retorna a data
	return result	

"""
função find_categories()
query - Pesquisa a ser feita no banco de dados
field_comparator - campo no qual deseja fazer a comparação.
field_time - campo do tempo
collection_name - qual collection será feita tal pesquisa
timestamp_ms_initial - tempo inicial da busca 
timestamp_ms_finish - tempo final da busca
field_constains - para saber se possui o  nome no valor. 
"""
def find_categories(query, field_comparator, field_time, collection_name, timestamp_ms_initial, timestamp_ms_finish, field_constains):
	collection = db[collection_name] #pega a collectin desejada, exemplo: tweets, facebook_comments..	
	query[field_time] = {"$gte":timestamp_ms_initial,"$lte":timestamp_ms_finish}		#monta a query para restringir o tempo de busca
	
	search = collection.find(query).distinct(key=field_comparator) 
	categorias = []
	for categoria in search:
		if field_constains in categoria:
			categorias.append(categoria)
	return categorias
	

"""
convert_time(timestamp)
timestamp - tempo em segundos de acordo com o padrão de tempo (segundos desde 01/01/1970 até hoje)
retorna a data no padrão "%d-%m-%YT%H:%M:%S"
onde 
%d - dia 10
%m - mes 10
%Y - ano 2016
%H - hora 23
%M - minutos 59
%S - segundos 59
"""
def convert_time(timestamp):
	return datetime.datetime.fromtimestamp(timestamp).strftime(data_format)

"""
sum_series_common(serie_1, serie_2)
Essa função tem como objetivo retornar a soma de duas séries 
"""
def sum_series_common(serie_1, serie_2):
	# pega as informações recebidas 
	label = serie_1["label"] #espera-se que os labels sejam iguais, então tanto faz pegar o label da serie_1 ou da serie_2
	data_1 = serie_1["data"] #data 1 para ser somada
	data_2 = serie_2["data"] #data 2 para ser somada

	#serie de saida
	serie_sum = {}
	data = {}
		
	for key in data_1.keys():
		value_1 = data_1.get(key)
		value_2 = data_2.get(key)
		if value_2:
			value = value_1 + value_2
			data[key] = value

	#atualiza a nova serie
	serie_sum["data"] = data
	serie_sum["label"] = label

	return serie_sum


def ler_configuracao():
	global config_data, data_output 
	label_db = None
	if len(argv)>1:
		label_db = str(argv[1])
	data_output["_id"] = label_db		
	try:
		with codecs.open('config.json','r','utf-8') as data_file:    
			config_data = json.load(data_file)
			return label_db
			pass
	except Exception as e:
		print( e)
		exit(0)

def configura_tempo(label_db):
	global date_final, date_inicial,period, data_output	

	now = datetime.datetime.utcnow()	
	interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)
	unix_time= int((interval - datetime.datetime(1970,1,1)).total_seconds())

	date_final = unix_time*1000;

	period = 1*60*60*1000

	if 'r' in label_db:
		pass
	else:
		if 'h' in label_db:
			horas = int(label_db.split('h')[0])
			if horas <3:
				interval = now - datetime.timedelta(seconds=now.second)
				unix_time= int((interval - datetime.datetime(1970,1,1)).total_seconds())
				period = 15*60*1000
			else:
				period = 1*60*60*1000

			date_inicial = unix_time*1000  - horas*60*60*1000		
			date_final = unix_time*1000;
		else:
			if 'd' in label_db:
				dias = int(label_db.split('d')[0])
				period = 1*60*60*1000			
				date_inicial = unix_time*1000  - dias*24*60*60*1000		
				date_final = unix_time*1000;			
	

	if label_db == 'r8h':
		hora = 8;
		if now.hour>hora:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=now.hour-hora)

		else:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)

		unix_time= int(interval.strftime("%s"))
		
		date_final = unix_time*1000

		date_inicial = date_final - 13*60*60*1000
		

	if label_db == 'r12h':
		hora = 12;
		if now.hour>hora:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=now.hour-hora)
			horas = 5;
		else:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)
			horas =  hora  - now.hour +1
			

		unix_time= int(interval.strftime("%s"))
		date_final = unix_time*1000

		date_inicial = date_final - horas*60*60*1000
		

	if label_db == 'r16h':
		hora = 16;
		horas = 5;
		if now.hour>hora:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=now.hour-hora)

		else:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=2) 
			horas =  hora  - now.hour +1


		unix_time= int(interval.strftime("%s"))
		date_final = unix_time*1000

		date_inicial = date_final - horas*60*60*1000
		

	if label_db == 'r20h':
		hora = 20;
		horas = 5
		if now.hour>hora:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=now.hour-hora)

		else:
			interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)
			horas =  hora  - now.hour +1

		unix_time= int(interval.strftime("%s"))
		date_final = unix_time*1000

		date_inicial = date_final - horas*60*60*1000
				

	if label_db == 'r24h':
		date_final = unix_time*1000
		date_inicial = date_final - 25*60*60*1000
		


	data_output["date_inicial"] = date_inicial/1000
	data_output["date_final"] = date_final/1000
	data_output["period_seconds"] = period/1000

	print(convert_time(date_inicial/1000), convert_time(date_final/1000), period)


def append_serie(series,label,field_comparator,field_time,collection_name,query):
	global period, date_inicial,date_final
	serie = {}	
	data = find_count(query,field_comparator, field_time, collection_name,period, date_inicial,date_final)
	serie["label"] = label
	serie["data"] = data
	series.append(serie)
	print("\t"+label)

########################################Twitter########################################
def twitter_estatisticas():	
	print ("twitter")
	global data_output,config_data
	series_twitter = []	

	config_twitter = config_data.get("config_twitter")	
	collection_name = config_twitter.get("collection_name")
	field_time = config_twitter.get("field_time")

	for serie in config_twitter.get("series"):
		label = serie.get("label")
		field_comparator = serie.get("field_comparator")
		query = serie.get("query")
		append_serie(series_twitter,label,field_comparator,field_time,collection_name,query)		
		pass

	data_output["twitter"] = series_twitter
	

########################################facebook########################################
def facebook_estatisticas():
	print("facebook")
	global data_output,config_data
	series_facebook = []	

	config_faceboook = config_data.get("config_facebook")	
	collection_name = config_faceboook.get("collection_name")
	field_time = config_faceboook.get("field_time")

	for serie in config_faceboook.get("series"):
		label = serie.get("label")
		field_comparator = serie.get("field_comparator")
		query = serie.get("query")
		append_serie(series_facebook,label,field_comparator,field_time,collection_name,query)		
		pass

	data_output["facebook"] = series_facebook
	
	pass

def salvar_banco(label_db):	
	print("escrevendo no banco de dados")
	now = datetime.datetime.utcnow()
	interval = now - datetime.timedelta(seconds=now.second, minutes=now.minute)
	unix_time= int((interval - datetime.datetime(1970,1,1)).total_seconds())

	try:
		data = data_output
		data["_id"] = label_db
		data["date"] = unix_time
		estatisticas_collection.replace_one({"_id":label_db}, data,upsert=True)
		print("dados inseridos")
	except Exception as e:
		print (e)
		try:
			data = data_output
			data["_id"] = label_db
			data["date"] = unix_time
			estatisticas_collection.insert_one(data)
			print("dados inseridos")
			
		except Exception as e:
			print("dados não foram inseridos")
			print (e)


def main(label_db):
	configura_tempo(label_db)
	twitter_estatisticas()
	facebook_estatisticas()
	salvar_banco(label_db)

label_db = ler_configuracao()
if label_db:
	main(label_db)
