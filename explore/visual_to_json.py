# tekur inn heiti á eigindum (t.d. hitastig,verð á máltíð) og býr til scatterplot json file 

import numpy as np 
import matplotlib.pyplot as plt
import sqlite3
import pickle 
import mpld3

import pandas as pd
from sklearn import preprocessing 
from sklearn.decomposition import PCA



### tenging við gagnagrunn

dbURL = "C:/Users/Valdi/Desktop/Ferdasja sumar/database.db"
con = sqlite3.connect(dbURL)
cur = con.cursor()

#chosenAttributes = cur.execute("SELECT column1, column2 FROM plot_query WHERE id = 1").fetchall()[0]
chosenAttributes = ["Cost of Living Index", "temp_high_avg"]

tofluNofn = ["Prices", "CostOfLivingIndex", "QualityOfLifeIndex", "WeatherEurope", "WeatherChancesEurope"]

eigindiTaflna = []

for tofluNafn in tofluNofn:
	eigindisNafn = list(map(lambda x: x[0] , con.execute('select * from ' + tofluNafn).description) ) 
	eigindiTaflna.append(eigindisNafn)
	
# eigindiTaflna inniheldur lista af nöfnunum á eigindum taflnanna úr tofluNofn 


# Notkun: nafn = taflaEigindis(eigindi)
# Fyrir: eigindi er nafn á eigindi úr dbURL gagnagrunninum 
# Eftir: nafn er nafnið á töflunni sem eigindið er í
def taflaEigindis(eigindi):
	# vil gá hvaða listi í eigindiTaflna inniheldur eigindið 
	i = 0
	for eigindanofn in eigindiTaflna:
		if eigindi in eigindanofn : 
			return tofluNofn[i]
		i += 1 


		
# Notkun: notTuples = removeTuples(listi)
# Fyrir: listi er listi af tuples [(x,""),(y,""), ...]
# Etir: notTuples er listi [x,y,...]
def removeTuples(listi):
	
	res = [x[0] for x in listi] 
	
	return listi

	
	
	
# Notkun: scatt = scatterplot(eigindi1, eigindi2, week) 
# Fyrir:  eigindi1 og eigindi2 eru nöfn á eigindum úr töflum dbURL gagnagrunninnum, week er vika ef verið er að skoða veður.  eigindin mega ekki vera 'city' því það er sama í báðum 
# Eftir:  scatterplot json hlutur hefur verið saveaður í scatterplot.json
def scatterplot(eigindi1, eigindi2, week):

	tafla1 = taflaEigindis(eigindi1) 
	tafla2 = taflaEigindis(eigindi2)
	
	with con:
		if tafla1 in ["WeatherChancesEurope", "WeatherEurope"]:

			data1 = cur.execute("Select city, " + eigindi1 + " from " + tafla1 + " where week = " + week)
			data1 = removeTuples(cur.fetchall())
		else:
			data1 = cur.execute("Select city, " +  '"' + eigindi1 + '"' +  " from " + tafla1)

			data1 = removeTuples(cur.fetchall())
			
		if tafla2 in ["WeatherChancesEurope","WeatherEurope"]:
			data2 = cur.execute("Select city, " + eigindi2 + " from " + tafla2 + " where week = " + week)
			data2 = removeTuples(cur.fetchall())
		else:
			data2 = cur.execute("Select city, " + '"' + eigindi2 + '"' +  " from " + tafla2)
			data2 = removeTuples(cur.fetchall())
		

	
	newdata = []
	newdata2 = []
	
	missingFromWeatherEurope = ["Venice", "Venice, Italy", "Berlin", "Berlin, Germany", "Palermo", "Palermo, Italy"]
	
	for city in data1:
		
		if city[0] not in missingFromWeatherEurope and city not in newdata:
			newdata.append(city)
			
	# gögn fyrra eigindis eru í newdata
	for city in data2:
		if city not in newdata2:
			#print(data2[i])
			newdata2.append(city)
			#print(newdata2)
			
	# gögn seinna eigindis eru í newdata2 
	
	# jöfnum þá lengdirnar, skyldi annar listinn vera stærri  
	if(len(newdata) >= len(newdata2)):
		newdata = newdata[0:len(newdata2)]
	else:
		newdata2 = newdata2[0:len(newdata)]
	
	
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
	cities = [x[0] for x in newdata]
	cities2 = [x[0] for x in newdata2]
	
		
	print(len(newdata))
	print(len(newdata2))
	
	# for i in range(0,len(newdata)-1):
		# print(newdata[i])
		# print(newdata2[i])
		# print("\n")

	newdata = [x[1] for x in newdata]
	newdata2 = [x[1] for x in newdata2]
	missingCities = []
	i = 0
	for data in newdata2: 
		if data == '':
			print(cities2[i])
			# fjarlægjum tómar borgir 
			newdata.pop(i)
			newdata2.pop(i)
			missingCities.append(cities2[i])
			cities2.pop(i)
		i += 1
		

	

	N = len(newdata)
	col = np.random.rand(N)
	area = s=10 * np.random.random(size=N)
	
	mynd = ax.scatter(newdata, newdata2, c = col, alpha = 0.5)
	
	ax.set_xlabel(eigindi1.replace('_',' '), fontsize=15)
	ax.set_ylabel(eigindi2.replace('_',' '), fontsize=15)
	ax.set_title("Comparison of prices and weather in European Cities")	
	
	tooltip = mpld3.plugins.PointLabelTooltip(mynd, labels=cities2)
	mpld3.plugins.connect(fig, tooltip)
	
	mpld3.save_html(fig, "scatterplot.html")
	
	
# Notkun:  xy = PCA(sleppa)
# Fyrir: toflur er listi af töflum, sleppa er listi af listum yfir þau eigindi sem á ekki að beita PCA á (í sömu röð og toflur)
# Eftir: xy er listi af 3 listum x sem er borgirnar og y og z sem eru principal component 1 og component 2 
def PCA2d(sleppa, toflur):

# prófa fyrst að taka bara costoflivingindex og veðrið í viku 30 
# töflurnar geta verið prices, costoflivingindex, qualityoflifeindex, weathereurope og weatherchanceseurope

	pca = PCA(n_components = 2)	
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
	if(len(toflur) == 1):
		if "WeatherEurope" in toflur or "WeatherChancesEurope" in toflur:
			query  = cur.execute("SELECT * FROM " + toflur[0] + " where week = 20")
			cols = [column[0] for column in query.description]
			
			results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
			
			
			cities = results['city'].tolist()

			dropColumns = ['week', 'city']
			if toflur[0] == "WeatherEurope": 
				dropColumns.append('cloud_cover')
			results.drop(columns = dropColumns, inplace=True)
			results = results.apply(pd.to_numeric)
			resultsScaled = preprocessing.StandardScaler().fit_transform(results)
			
			principalComponentsScaled = pca.fit_transform(resultsScaled)
			principalDfScaled = pd.DataFrame(data = principalComponentsScaled, columns = ['principal component 1', 'principal component 2'])
	
			N = len(cities)
			col = np.random.rand(N)
			

			mynd = ax.scatter(principalDfScaled['principal component 1'],principalDfScaled['principal component 2'], c = col, alpha = 0.5)
			ax.set_title("2-dimensional PCA of weather in Europe in late June")	
		
		if "CostOfLivingIndex" in toflur or "QualityOfLifeIndex" in toflur:
			
			query2 = cur.execute("SELECT * from " + toflur[0])
			cols = [column[0] for column in query2.description]
			
			results2 = pd.DataFrame.from_records(data = query2.fetchall(), columns = cols)
			
			cities2 = results2['City'].tolist()

		
			results2.drop(columns = ['City', 'Rank'], inplace=True)
				
			results2 = results2.apply(pd.to_numeric)
			
			results2Scaled = preprocessing.StandardScaler().fit_transform(results2)
			principalComponentsScaled2 = pca.fit_transform(results2Scaled)
			principalDfScaled2 = pd.DataFrame(data = principalComponentsScaled2, columns = ['principal component 1', 'principal component 2'])
			
			col = np.random.rand(len(cities2))
			
			mynd = ax.scatter(principalDfScaled2['principal component 1'],principalDfScaled2['principal component 2'], c = col, alpha = 0.5)
			if("CostOfLivingIndex" in toflur):
				ax.set_title("2-dimensional PCA of cost of living indeces")	
			else:
				ax.set_title("2-dimensional PCA of quality of life indeces")	
		if "Prices" in toflur: 
			query3 = cur.execute("SELECT * from " + toflur[0])
			cols = [column[0] for column in query2.description]
			print(cols)
			results3 = pd.DataFrame.from_records(data = query3.fetchall(), columns = cols)
			
			cities3 = results3['City'].tolist()
			irrelevantAttributes = ["City", "Monthly Pass", "Volkswagen Golf", "Toyota Corolla", "Basic Utilities", "Internet", "Fitness Club", "Tennis Court Rent", "Preschool Month", "Primary School Year", "Rent 1 Bedroom Center""Rent 1 Bedroom Outside Center""Rent 3 Bedrooms Center","Rent 3 Bedrooms Outside Center", "Price m2 Center","Price m2 Outside Center","Average Monthly Salary After Tax","Mortgage Interest Rate"]
		 
			results3.drop(columns = irrelevantAttributes, inplace=True)
				
			results3 = results3.apply(pd.to_numeric)
			
			results3Scaled = preprocessing.StandardScaler().fit_transform(results3)
			principalComponentsScaled3 = pca.fit_transform(results3Scaled)
			principalDfScaled3 = pd.DataFrame(data = principalComponentsScaled3, columns = ['principal component 1', 'principal component 2'])
			
			col = np.random.rand(len(cities3))
			
			mynd = ax.scatter(principalDfScaled3['principal component 1'],principalDfScaled3['principal component 2'], c = col, alpha = 0.5)
			ax.set_title("2-dimensional PCA of prices of goods")	
			
	else: 
		# sameina 
		toflulisti = []
		
		for tafla in toflur: 
				
			if tafla == "WeatherEurope" or tafla == "WeatherChancesEurope" :
				query  = cur.execute("SELECT * FROM " + tafla + " where week = 20")
				cols = [column[0] for column in query.description]
				
				results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
								
				cities = results['city'].tolist()

				
				
				toflulisti.append(results)
				
			if tafla == "CostOfLivingIndex" or tafla == "QualityOfLifeIndex":
				
				query2 = cur.execute("SELECT * from " + tafla)
				cols = [column[0] for column in query2.description]
				
				results2 = pd.DataFrame.from_records(data = query2.fetchall(), columns = cols)
				
				cities = results2['City'].tolist()	
				results2.drop(sleppa[1], axis=1)
				results2.drop("Rank", axis=1, inplace=True)
				results2.rename(index=str, columns={"City": "city"}, inplace= True)
				

				toflulisti.append(results2)
				
			if tafla == "Prices":
				query3 = cur.execute("SELECT * from " + toflur[0])
				cols = [column[0] for column in query2.description]
				
				results3 = pd.DataFrame.from_records(data = query3.fetchall(), columns = cols)
				
				cities3 = results3['City'].tolist()
				irrelevantAttributes = ["City", "Monthly Pass", "Volkswagen Golf", "Toyota Corolla", "Basic Utilities", "Internet", "Fitness Club", "Tennis Court Rent", "Preschool Month", "Primary School Year", "Rent 1 Bedroom Center""Rent 1 Bedroom Outside Center""Rent 3 Bedrooms Center","Rent 3 Bedrooms Outside Center", "Price m2 Center","Price m2 Outside Center","Average Monthly Salary After Tax","Mortgage Interest Rate"]
			 
				results3.drop(columns = irrelevantAttributes, inplace=True)
					
				toflulisti.append(results3)
					

		saman = reduce( (lambda results,results2: pd.merge(results, results2, how='inner', left_on=['city'], right_on=['city'])), toflulisti)
		

		cities = list(saman["city"])
		
		samandrop = ['city', 'week', 'cloud_cover']
		saman.drop(columns = samandrop, inplace = True)
		
		samanScaled = preprocessing.StandardScaler().fit_transform(saman)
	
		principalComponentsScaledSaman = pca.fit_transform(samanScaled)
		principalDfScaledSaman = pd.DataFrame(data = principalComponentsScaledSaman, columns = ['principal component 1', 'principal component 2'])
		col = np.random.rand(len(saman))
		
		mynd = ax.scatter(principalDfScaledSaman['principal component 1'],principalDfScaledSaman['principal component 2'], c= col, alpha = 0.5)
		
		
# frekar en að hafa results, results2 o.s.frv. þá get ég haft lista/dict  results["WeatherEurope"], results["CostOfLivingIndex"]
	# Prices og QualityOfLifeIndex er keimlíkt CostOfLivingIndex
	# WeatherChancesEurope er keimlíkt WeatherEurope
		# nema það þarf að droppa öðrum dálkum 
	
	
	
	
	
	ax.set_xlabel('Principal Component 1', fontsize=15)
	ax.set_ylabel('Principal Component 2', fontsize=15)
	if(len(toflur) > 1):
		title = "2-dimensional PCA of " + toflur[0]
		i = 1
		for tafla in toflur[1:]:
			if i != (len(toflur)-1):
				title = title + ", " + tafla + " " 
			else:
				title = title + " and " + tafla
			i = i+1 
		ax.set_title(title)
	# vantar að staðfesta að röðin sé eins?
	
	tooltip = mpld3.plugins.PointLabelTooltip(mynd, labels=cities)
	mpld3.plugins.connect(fig, tooltip)
	
	mpld3.save_json(fig, "PCA.json")

	
	
print(chosenAttributes)
scatterplot(chosenAttributes[0],chosenAttributes[1], "25")
