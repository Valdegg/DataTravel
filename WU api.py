# skröpum upp borgirnar af Weather Underground



import requests
import json 
import pandas as pd 
import datetime
import time 
import sqlite3
import pickle 
import pycountry
from bs4 import BeautifulSoup



# use: list = getHTMLTabless(url)   # list of many? hverju skilar soup.find.find_all? lista af html lokuðum tag svigum 
# before: the url contains HTML tables
# after: df is a list of dataframes with data from tables from url, with column names as keys from tables from url
def getHTMLTables(url):
	res = []
	
	r = requests.get(url)
	
	soup = BeautifulSoup(r.text, 'lxml') # spurning með 'lxml', fer eftir töflunni
	
	tables = soup.find_all('table')
	#print(tables[2])
	print(len(tables))
	nrOfTables = 0
	for table in tables:
		# first nrOfTables tables have been added to res as data frames 
	
		
		headers = table.find_all('tr')[0].find_all('th')
		nrOfColumns = len( headers ) # number of column names 
	
		columns = [[] for _ in headers]
		
	
		if len(columns) > 0:
			# data is only loaded into the tables with keys 
		
			# data is stored in the columns
			nrOfRows = 0 
			# how many rows have been traversed
			for row in table.find_all('tr')[1:]:
				# first nrOfRows rows have been added to c[0..nrOfRows] where c are in columns
				rowData = row.find_all('td')
				nrOfRows += 1 
				if len(rowData) >0:
					for columnNr in range(nrOfColumns):
						
						if len(rowData[columnNr].contents) > 1:
							# some html stuff in this column 
							
							# í tilfellinu þar sem þetta er 'range':
							# tek það sem er á milli <span class="barTextLeft"> og </span>
							# og <span class="barTextRight"> og </span>
							# og greini á milli með "-"
							
							
							lowest = rowData[columnNr].contents[1].string
							highest = rowData[columnNr].contents[-1].string
							
							if(lowest is not None and highest is not None):
								# we can take substring og lowest 
								lowest = rowData[columnNr].contents[1].string[1:]								
								columns[columnNr].append(lowest + "-" + highest)
							else: 								
								columns[columnNr].append("")
							
							
						else: 
							columns[columnNr].append( str(rowData[columnNr].string) )
							
						
						
			
			# data in table has been loaded into columns 
			keys = []
			for header in headers:
				keys.append(header.string)
			
			res.append(pd.DataFrame(dict(zip(keys, columns))))
			# data frame with data from table with keys as key has been added to res
			nrOfTables += 1

	return res
	
def beforeComma(string):
	return string.split(",")[0]

def afterComma(string):	
	if string is not None:
		if len(string.split(",")) > 1:
			return string.split(",")[1][1:] 
	

	#### Skilgreini dict á milli countries og WU codes 


country_to_iso = getHTMLTables("https://www.wunderground.com/weather/api/d/docs?d=resources/country-to-iso-matching&MR=1")
iso_codes = pd.concat(country_to_iso)


iso = iso_codes.to_dict()["ISO Code"]
print(len(iso_codes))
print(len(iso_codes["ISO Code"]))

# iso breytir tölu í iso code 
osi = {v: k for k, v in iso.items()}
# öfug vörpun 
wu = iso_codes.to_dict()["Wunderground Code"]
# wu[osi[ iso_code ] gefur wu code fyrir iso code 

with open("cityFix.txt", 'rb') as f:
	cityFix = pickle.load(f)
	
cityFix["Bolzano-Bozen"] = "00000.20.16020"
cityFix["The Hague (Den Haag)"] = "00000.12.06200"
cityFix["Zaragoza (Saragossa)"] = "00000.142.08160"
cityFix["Krakow (Cracow)"] = "00000.1004.12566"
# cityFix er dict sem úthlutar borg sem hafði sama nafn og aðrar borgir í planner apanum zmw kóða sem gerir kleift að finna veðrið í borginni 



	

# borg: strengur með landheiti og borg (fylki ef í US)
# dateFrom og dateTo:  strengur MMDD,   mest 30 dagar á milli
# output: weather predictions in borg on the era between dateFrom and dateTo. dictionary containing the information about weather , not weekday_short and all that craps.  it's a list [city, weatherData]
def weatherInCity(borg, dateFrom, dateTo):

	timabil = dateFrom + dateTo 
	base = "http://api.wunderground.com/api/e0d9599c3d3d3e3b/planner_"
	city = beforeComma(borg) 	
	#land = 	pycountry.countries.get(name= afterComma(borg))
	#wucode = wu[osi[ land.alpha_2 ] ]
	
	fyrirspurn = base + timabil + "/q/" + afterComma(borg) + "/" + city + ".json"
	print(fyrirspurn + "\n")
	
	response = requests.get(fyrirspurn)
	data = response.json()
	if len(data) > 1:
		# það eru 2 lyklar, 'response' og 'trip' í succesful fyrirspurnum 
		weatherData = data["trip"]
	
		# sleppum trip[period_of_record] en geymum rest 
		del weatherData["period_of_record"] 	

		return [borg, weatherData]
	else: 
		# g.r.f. að borgin sé ein af þeim sem búið er að skrifa í cityFix.txt
		zmw = cityFix[beforeComma(city)]
		fyrirspurn = base + timabil + "/q/" + "zmw:" + zmw + ".json"
		response = requests.get(fyrirspurn)	
		data = response.json()
		weatherData = data["trip"]
		# sleppum trip[period_of_record] en geymum rest 
		del weatherData["period_of_record"] 	

		return [borg, weatherData]
	

with open("citiesEurope.txt", 'rb') as f:
	cities = pickle.load(f)


dbURL = "C:/Users/Valdi/Desktop/Ferdasja sumar/database.db"
con = sqlite3.connect(dbURL)
cur = con.cursor()

wAttributes = list(map(lambda x: x[0] , cur.execute('select * from WeatherEurope').description) )
cAttributes= list(map(lambda x: x[0] ,cur.execute('select * from WeatherChancesEurope').description))	

### weatherAllWeeks úr API WU test.py virkar ekki, eftirfarandi er því úr API WU fikt.py 

# notkun: dfs = weatherAllWeeks(city)
# before: city er borgarnafn sem virkar í WU apann (gæti þurft að snyrta til áður en kallað er á)
# after: dfs is a list with 2 dataframes (weather and chances)  with 52 rows with the weather from WU for all weeks of the year for the city 
def weatherAllWeeks(city):
	
	dfWeather = pd.DataFrame(columns = wAttributes)
	dfChances = pd.DataFrame(columns = cAttributes)
	
	# dataframes with space for 52 weeks has been created 
	
	# get búið til dataframeið upprunalega mþa gera from_dict(weatherInWeek)
	
	dateOfVacation = datetime.date(2018,1,1)
	
	print(dateOfVacation.strftime("%m%d"))
	oneWeek = datetime.timedelta(weeks=1)
	
	# weatherInWeek = weatherInCity(city, dateOfVacation.strftime("%m%d"), (dateOfVacation+oneWeek).strftime("%m%d"))	
	# # is a dict 
	
	# dataframe = pd.from_dict(weatherInWeek)
	# dateOfVacation += oneWeek 
	
	numberOfWeeks = 0
	while( numberOfWeeks < 1 ):   # prófum fyrst <1 í prufukeyrslu
		# weather data for the first numberOfWeeks weeks has been added to dfWeather and dfChances
		# at least numberOfWeeks*7 seconds have passed 
		
		weatherInWeek = weatherInCity(city, dateOfVacation.strftime("%m%d"), (dateOfVacation+oneWeek).strftime("%m%d"))
		
		print(weatherInWeek)
		print(weatherInWeek[1]["chance_of"])
		addWeatherToDFrame(dfChances, weatherInWeek[1]["chance_of"])
		del weatherInWeek["chance_of"]
		addWeatherToDFrame(dfWeather, weatherInWeek)
		
		print(dfWeather)
		# prófa prófa prófa 
		
		dateOfVacation += oneWeek 
		numberOfWeeks += 1 		
		time.sleep(7)
	
	return [dfWeather, dfChances]
	
	
# get bara endurskrifað weatherAllWeeks þannig að það tekur gögnin úr dictionaryinu fyrir gefna borg í gefinni viku 
# og skellir því sem röð inn í WeatherEurope og WeatherChancesEurope
	
#print(cities[95:99])	  vantar frá 95 
	
	
# data = []
# for city in cities[5:7	]: 
	# # city inniheldur nafn borgar og lands, í data er veðrið fyrir borgirnar í cities[.. city]
	# # nema það hafi verið fails þá er bara nafnið á borginni í data 

	# data.append(weatherAllWeeks(city))
	# time.sleep(2)
	# # # geta verið margar borgir með sama nafn í sama landi !!! þá get ég úthlutað hverri fail-borg fylkinu sem hún er í. 
	
# # print(data)


oneWeek = datetime.timedelta(weeks=1)
# city = "Reykjavik, Iceland"
city = cities[97]


# Gögnin um Reykjavík eru öðruvísi núna þegar ég sæki þau en þau eru í gagnagrunninnum ??? Virðast nær raunveruleikanum í gagnagrunninnum.


city = cities[95]#for city in cities[95] : #cities[95:100]:
# vantar info um Berlin 
	# In the meantime, searching for the nearest larger town or city should find a result.
# Leipzig í staðinn fyrir Berlin 


									# vantar info um Venice !!!
# og den Haag er ekki með rétt nafn 

# Lausanne vantar 

# tvö entry fyrir Dublin í WeatherEurope, þurfum mögulega að eyða öllum duplicates í gagnagrunninnum

# höfum líka cityfails.txt 
with open("cityFails.txt", 'rb') as f:
	cityFails = pickle.load(f)
	


#citiesMissing = ["Lausanne, Switzerland", "Exeter, United Kingdom", "Reading, United Kingdom", "Venice, Italy", "Palermo, Italy"]
citiesMissing = []

with open("citiesMissing.txt", 'rb') as f:
	citiesMissing = pickle.load(f)


startingWeekOffset = 0
# ef við viljum byrja á 15. viku þá er offsettið 14, venjulega 0 til að byrja í 1. viku 
	# offsettið er þá aftasta talan sem er komin 

numberOfWeeks = 52
	
weeksOffset = datetime.timedelta(weeks = startingWeekOffset)

startIndex = len(cities)

print(cities[90:100])
				
for city in cities[startIndex:len(cities)]:
		
		# if city == cities[startIndex]:
			# with con: 
				# cur.execute("SELECT week from WeatherEurope where city = '" + city + "'")
				# rows = cur.fetchall()
				# print(rows)
		dateOfVacation = datetime.date(2018,1,1) + weeksOffset
		
		for week in range(1 + startingWeekOffset ,numberOfWeeks+1):
			# búum til tuple með sitt hvorri röðinni og skellum inn í gagnagrunninn 
				# questionMarks = ("?,"*len(weatherRowW))[:-1]
				# cur.execute("INSERT into WeatherEurope VALUES(" + questionMarks + ")", tuple(weatherRowW))
			if city not in citiesMissing:	
				weatherEurope = weatherInCity(city, dateOfVacation.strftime("%m%d"), (dateOfVacation+oneWeek).strftime("%m%d"))[1]
						
				if(weatherEurope["airport_code"]==""):
					citiesMissing.append(city)
					
				else:

					
					# print("\n")
					# print(weatherEurope)
					# print("\n")

					weatherChances = weatherEurope["chance_of"]

					del weatherEurope["chance_of"]

					# print(weatherEurope)	
					# print("\n")
					# print(weatherChances)
						
					europeTuple = [city, week]
			# þurfum að hafa attributein í sömu röð og í gagnagrunninum 
				# city, week, temp_low temp_high, precip, dewpoint_high, dewpoint_low, cloud_cover
				# avg, min, max 
				
					europeKeys = ["temp_low", "temp_high","precip", "dewpoint_high", "dewpoint_low"]
					# europeKeys er með lyklana á hæsta leveli úr weatherEurope, fyrir utan cloud_cover
					subKeys = ["avg", "min", "max"]
					# subkeys er með lyklana í levelinu fyrir neðan 

					subsubDict = []
					for key in europeKeys: 
						
						subDict = weatherEurope[key]
						subsubDict.extend([subDict[x] for x in subKeys])


					# print(subsubDict)

					europeTuple.extend( [x['C'] for x in subsubDict[0:6] ] )
					europeTuple.extend( [x['cm'] for x in subsubDict[6:9] ] )
					europeTuple.extend( [x['C'] for x in subsubDict[9:] ] )
					europeTuple.append( weatherEurope["cloud_cover"]["cond"] )
					# print(europeTuple)
						
					questionMarks = ("?,"*len(europeTuple))[:-1]
					# print(questionMarks)
					
					with con:
						cur.execute("INSERT into WeatherEurope VALUES(" + questionMarks + ")", tuple(europeTuple))
					
					dateOfVacation += oneWeek 		
					time.sleep(6)		
					
					
					
				
print(set(citiesMissing))
				
# búið var að ákvarða að Berlin eigi heima í citiesMissing áður en dump kóðinn var skrifaður:

with open("citiesMissing.txt", "wb") as f:
	pickle.dump(citiesMissing,f)
	
	
	
	
	
	
	
### WeatherChancesEurope

startingWeekOffset = 0
# ef við viljum byrja á 15. viku þá er offsettið 14, venjulega 0 til að byrja í 1. viku 
	# offsettið er þá aftasta talan sem er komin 

numberOfWeeks = 52
	
weeksOffset = datetime.timedelta(weeks = startingWeekOffset)

startIndex = cities.index('Sibiu, Romania')

print(startIndex)
				
for city in cities[startIndex:startIndex+1]:
		
		# if city == cities[startIndex]:
			# with con: 
				# cur.execute("SELECT week from WeatherEurope where city = '" + city + "'")
				# rows = cur.fetchall()
				# print(rows)
		dateOfVacation = datetime.date(2018,1,1) + weeksOffset
		
		for week in range(1 + startingWeekOffset ,numberOfWeeks+1):
			# búum til tuple með sitt hvorri röðinni og skellum inn í gagnagrunninn 
				# questionMarks = ("?,"*len(weatherRowW))[:-1]
				# cur.execute("INSERT into WeatherEurope VALUES(" + questionMarks + ")", tuple(weatherRowW))
			if city not in citiesMissing:	
				weatherEurope = weatherInCity(city, dateOfVacation.strftime("%m%d"), (dateOfVacation+oneWeek).strftime("%m%d"))[1]
						
				if(weatherEurope["airport_code"]==""):
					citiesMissing.append(city)
					
				else:

					
					# print("\n")
					# print(weatherEurope)
					# print("\n")

					weatherChances = weatherEurope["chance_of"]

					del weatherEurope["chance_of"]

					# print(weatherEurope)	
					# print("\n")
					# print(weatherChances)
						
					europeChancesTuple = [city, week]
			# þurfum að hafa attributein í sömu röð og í gagnagrunninum 
				# city, week, temp_low temp_high, precip, dewpoint_high, dewpoint_low, cloud_cover
				# avg, min, max 
				
					europeChancesKeys = ['tempoversixty', 'tempoverninety', 'tempbelowfreezing', 'tempoverfreezing', 'windy', 'partlycloudy', 'sunnycloudy', 'cloudy', 'humid', 'fog', 'precipitation', 'rain', 'snow', 'snowonground', 'sultry', 'thunder', 'tornado', 'hail']
					europeChances2realkeys = {'windy': 'chanceofwind'}
					
					
					keysThatWork = []
					for key in europeChancesKeys: 
						if key in weatherChances.keys():
							subDict = weatherChances[key]
						else:
							key2 = "chanceof" + key 
							if key2 in weatherChances.keys():
								subDict = weatherChances[key2]
								key = key2
							else:
							
								key3 = key2 + "day"
								if key3 in weatherChances.keys():
									subDict = weatherChances[key3]
									key = key3
								else:
							
									if key == "precipitation":
										key4 = "chanceofprecip"
										subDict = weatherChances[key4]
							
						europeChancesTuple.append(subDict['percentage'] )
						keysThatWork.append(key)
						
					# print(subsubDict)
					# print(keysThatWork)
					# print(weatherChances.keys())
					# # print(subsubDict)
					for key in keysThatWork:
						check = key in weatherChances.keys()
						#print(check)
						if(not check):
							print(key)
							
					print(weatherChances)
					print(keysThatWork)
					print(europeChancesTuple)
					# þurfum rétta röð 

						
						
					questionMarks = ("?,"*len(europeChancesTuple))[:-1]
					# print(questionMarks)
					
					# with con:
						# cur.execute("INSERT into WeatherChancesEurope VALUES(" + questionMarks + ")", tuple(europeChancesTuple))
					
					dateOfVacation += oneWeek 		
					time.sleep(6)		
	
	
	



















	
	
	
	
	
	
	
