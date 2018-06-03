# scrape 
# nær í html töflur frá Numbeo og vistar í gagnagrunn


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re 
import sqlite3 


def toNumeric(df):
	names = df.columns.tolist()
	names.remove("City")
	names.remove("Rank")
	for columnName in names:
		df[columnName] = pd.to_numeric(df[columnName])


		
def replaceEuro(df):
	for x in df.columns.tolist():
		df[x] = df[x].str.replace('€' , '')
# use: s = beforeComma(string)	
# before: string is a string that includes a comma 
# after: s is the part of string that's before the comma 
def beforeComma(string):
	return string.split(",")[0]

	
# use: list = getHTMLTabless(url)   
# before: the url contains HTML tables
# after: df is a list of dataframes with data from tables from url, with column names as headers from tables from url
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
	
	
# use: x = fixNames(cityNames)
# before: cityNames is a list of strings 
# after: x is cityNames with '(' and ')' removed and spaces replaced with '-', for scraping in Numbeo
def fixNames(cityNames):
	res = []
	for name in cityNames:
		res.append(name.replace(" ", "-").replace("(","").replace(")",""))
		
	for n, name in enumerate(res): 
		if name == 'The-Hague-Den-Haag':
			res[n] = 'The-Hague-Den-Haag-Netherlands'
	return res


def afterComma(string):
	
	if string is not None:
		if len(string.split("-")) > 1:
			return string.split("-")[1] 
	
	
#### Numbeo

# náum í verðlagið fyrir allar borgirnar og lífsgæðin fyrir hverja borg 


### Evropa, merkt með E í endann 

# næ fyrst í cost of living index töfluna, fæ þaðan nöfnin (dálkur "city")

costIndexE = getHTMLTables("https://www.numbeo.com/cost-of-living/region_rankings.jsp?title=2018&region=150")[0]
# costIndexE er dataframe með gögnunum úr costofliving fyrir Evrópu
qualityE = getHTMLTables("https://www.numbeo.com/quality-of-life/region_rankings.jsp?title=2018&region=150")[0]
# qualityE er listi af data frames með quality of life indexana af Numbeo fyrir hverja borg í cityNamesE 

cityNamesE = list(map(beforeComma, costIndexE["City"]))
# nöfnin á borgunum í Evrópu af Numbeo eru í cityNamesE


costE = []
# verðlagsgögnin fyrir borgirnar í cityNamesE verða í listanum af data frames costE

index = 0
numberOfCities = len(cityNamesE)
scrapeFailures = [] #  price tables that didn't come through  
for name in fixNames(cityNamesE[0:numberOfCities]):
	# verðlags gögnin fyrir fyrstu index borgirnar í cityNamesE eru í fyrstu index röðunum í costE 
	url = "https://www.numbeo.com/cost-of-living/in/" + name + "?displayCurrency=EUR"
	print(cityNamesE[index])
	costTables = getHTMLTables(url)
	
	if(len(costTables) > 0):
		costTables = costTables[0]
		costTables.columns = ["Goods", "Prices", "Range"]
		costE.append(costTables)
	else: 
		
		scrapeFailures.append(name)
		scrapeFailures.append(costTables)
	## Hreinsa burt töflurnar sem eru óþarfi	?
	
	
	
	index += 1

costEdict = dict(zip(cityNamesE, costE))
# costE is a dictionary with names of cities attached 
	




# # data framein sett upp til að bæt amegi í gagnagrunn. 

nColumns = len(costIndexE.columns)

cNames = costIndexE.columns.tolist()
cNames.remove("City")
cNames.remove("Rank")

for columnName in cNames:
	costIndexE[columnName] = pd.to_numeric(costIndexE[columnName])

toNumeric(qualityE)
	




for df in costE:
	replaceEuro(df)
 # evrutáknin ættu að vera farin úr töflunum í costTables 

 
con = sqlite3.connect("C:/Users/Valdi/Desktop/Ferdasja sumar/database.db")


# # data frameið sett í sqlite gagnagrunn:

# # dfin þurfa að hafa sömu dálkaheiti og töflurnar. 

costIndexE.to_sql("CostOfLivingIndex", con, if_exists="replace")
qualityE.to_sql("QualityOfLifeIndex", con, if_exists="replace")

# # # indexatöflurnar hafa verið settar í sql


	
# Gögnin sett í gagnagrunn: 	

# removes first and last letter of string 
def removeFirst(string):
	return string[1:-1]
	
print(removeFirst("yobo"))



with con: 
	cur = con.cursor() 
	cityNumber = 0
	for city in fixNames(cityNamesE[0:numberOfCities]):
		# cityNumber cities have been added to the db. price and price range 
		
		
		prices = costE[cityNumber]["Prices"].values.tolist()
		
		prices = list(map(removeFirst,prices))
		prices.insert(0,city)
		print(prices)
		range = costE[cityNumber]["Range"]
		
		cityNumber += 1
		
		lowRange = list(map( lambda string: string.split("-")[0], range) )
		highRange = list(map(lambda x:  afterComma(x), range))
		lowRange.insert(0,city)
		lowRange.insert(1,0)
		highRange.insert(0,city)
		highRange.insert(1,1)
		if len(pricesAttributes) + 1 == len(prices):		
			# + 1 útaf city
			questionMarks = "?,"*(len(prices)-1)
			questionMarks += "?"
			values = tuple(prices)
			
			cur.execute("INSERT into Prices VALUES(" + questionMarks + ")", values)
			# verðgögnin komin inn í Prices 
			
			
			if len(lowRange) == len(highRange):
				
				# hendi fyrst út None sem er fyrir average salary því það er ekkert range
				
				# auka dálkur fyrir 'high/low"
				questionMarks += ",?"
				values= tuple(lowRange)
				# eyðum út 
				
				cur.execute("INSERT into PriceRange VALUES(" + questionMarks + ")", values)
				
				
				#highRange = [x for x in highRange if x is not 'None']
				values = tuple(highRange)
				cur.execute("INSERT into PriceRange VALUES(" + questionMarks + ")", values)
			# range gögnin komin inn í PriceRange 
		
		else:
			print("unequal lengths, not all attributes ")

			
			

			
			
			
# # næ hér í altcurrency töfluna 

# newCoins = getHTMLTables("https://coinmarketcap.com/new/")

# aukning = newCoins[0]["% 24h"]
# # er með strengi   -37.06 %, vil fjarlæga aftasta,  fá x[-1]
# aukning = list(map(lambda x: x[:-2],aukning))
# aukning = list(filter(None, aukning))
# #print(aukning)
# aukning = list(map(float,aukning))

# import numpy

# print(numpy.mean(aukning))


# # allCoins = getHTMLTables("https://coinmarketcap.com/historical/20170709/")

# # aukning = allCoins[0]["% 24h"]
# # aukning = list(map(lambda x: x[:-2],aukning))
# # aukning = list(filter(None, aukning))
# # #print(aukning)
# # aukning = list(map(float,aukning))

# # print(numpy.mean(aukning[0:100]))




# allCoins = getHTMLTables("https://coinmarketcap.com")

# aukning = allCoins[0]["% Change (24h)"]
# aukning = list(map(lambda x: x[:-2],aukning))
# aukning = list(filter(None, aukning))
# #print(aukning)
# aukning = list(map(float,aukning))
# print(numpy.argmax(aukning))
# #print(numpy.mean(aukning[0:100]))
