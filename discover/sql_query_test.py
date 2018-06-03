# sql query test fyrir Discover viðmót

import sqlite3

# Föll sem eru notuð: 

# use: s = beforeComma(string)	
# before: string is a string that includes a comma 
# after: s is the part of string that's before the comma 
def beforeComma(string):
	return string.split(",")[0]


# Tenging við gagnagrunninn:
	
dbURL = "C:/Users/Valdi/Desktop/Ferdasja sumar/database.db"
con = sqlite3.connect(dbURL)
cur = con.cursor()

	
### Prices:
# strengir með queries búnir til
selectedProduct = 'Meal Inexpensive'
comparedCity = 'Berlin, Germany'
selectedPercentage = "20"
selectedMaxPrice = "1"

selectedIndex = '"Cost of Living Index"'
selectedIndex = '"Quality of Life Index"'
qualityIndeces = ['"PollutionIndex"', '"Quality of Life Index"']

priceInComparedCity = "SELECT " + selectedProduct + " FROM Prices WHERE City = '" + beforeComma(comparedCity) + "'"
	
indexInComparedCity = "SELECT " + selectedIndex + " FROM CostOfLivingIndex" + " WHERE City = " + '"' + comparedCity + '"'

lessThanMaxPrice = "SELECT City FROM Prices WHERE " + selectedProduct + " < " + selectedMaxPrice

# cities where selectedIndex from the right table (cost of living or quality of life) is selectedPercentage less than selectedIndex in comparedCity
# t.d. 50% ódýrari en Reykjavík 

# ef pollution er valið þá er quality of life taflan valin 

if selectedIndex in qualityIndeces:
	indexInComparedCity = "SELECT " + selectedIndex + " FROM QualityOfLifeIndex" + " WHERE City = " + '"' + comparedCity + '"'



	
cheaperProductCities = "SELECT City FROM Prices WHERE " + selectedProduct + " < " + selectedMaxPrice
# cities where price of selectedProduct is less than selectedMaxPrice



### Weather

selectedWeek = "23"
selectedWeeks = ["23", "24", "25"]

selectedTempLow = 15
selectedTempHigh = 20

selectedClouds = "mostly sunny"
selectedPrecipitation = "30"
selectedWind = "40"
	
tempFits = "SELECT city FROM WeatherEurope WHERE temp_low_avg > " + str(selectedTempLow) + " AND temp_high_avg < " + str(selectedTempHigh)

clouds = ['cloudy', 'mostly cloudy', 'partly cloudy', 'mostly sunny', 'sunny']

i = 0 
while clouds[i] != selectedClouds : 
	i += 1 
# i er indexið á selectedClouds

cloudyOrSunny = "SELECT city FROM WeatherEurope WHERE week = 30 AND cloud_cover = " + '"' + clouds[i] + '"'


for x in clouds[(i+1):]:
	cloudyOrSunny += " OR cloud_cover = " + '"' + x + '"'

#print(cloudyOrSunny)

rainy = "SELECT City From WeatherChancesEurope WHERE week = " + selectedWeek + " AND precipitation < " + selectedPrecipitation

windy = "SELECT City From WeatherChancesEurope WHERE week = " + selectedWeek + " AND windy  < " + selectedWind

with con: 

	# data1 = cur.execute(priceInComparedCity).fetchall()
	
	# data1 = [x[0] for x in data1]
	# # data1 er listi með verðinu á selectedProduct í comparedCity
	
	
	# data2 = cur.execute(indexInComparedCity).fetchall()
	# data2 = [x[0] for x in data2]
	# # data2 er listi með indexinu í comparedCity
	# # print(data2)
	
	# # cheaperCities = "SELECT City FROM CostOfLivingIndex WHERE " + selectedIndex + " < (1-0.01*" + selectedPercentage + ")*" + str(data2[0])	
	
	# # #print(cheaperCities)
	# # data3 = cur.execute(cheaperCities).fetchall()
	# # data3 = [x[0] for x in data3]
	# # # data3 er með borgirnar sem eru ódýrari en comparedCity
	# # #print(data3)
	
	# # print(cheaperProductCities)
	# # data3 = cur.execute(cheaperProductCities).fetchall()
	# # data3 = [x[0] for x in data3]
	# # # data3 is a list of cities where price of selectedProduct is less than selectedMaxPrice

	# # print(lessThanMaxPrice)
	# # data4 = cur.execute(lessThanMaxPrice).fetchall()
	# # data4 = [x[0] for x in data4]
	# # print(data4)
	# # # data4 is list of cities where price of selectedProduct is less than selectedMaxPrice

	# # cheaperThanProductCities = "SELECT City FROM Prices WHERE " + selectedProduct + " < (1-0.01*" + selectedPercentage + ")*" + str(data1[0])
	# # # cities where price of selectedProduct is selectedPricePercent% less than price in comparedCity

	# # data5 = cur.execute(cheaperThanProductCities).fetchall()
	# # data5 = [x[0] for x in data5]
	# # # cities where price of selectedProduct is selectedPricePercent% less than price in comparedCity

	# # betterCities = "SELECT City FROM QualityOfLifeIndex WHERE " + selectedIndex + " < (1-0.01*" + selectedPercentage + ")*" + str(data2[0])
	# # print(betterCities)
	# # data6 = cur.execute(betterCities).fetchall()
	# # data6 = [x[0] for x in data6]
	# # print(data6)

	
	
	# data7 = cur.execute(cloudyOrSunny).fetchall()
	# data7 = [x[0] for x in data7]
	# print(data7)
	
	# data8 = cur.execute(rainy).fetchall()
	# data8 = [x[0] for x in data8]
	# print(data8)	
	
	
	data9 = cur.execute(windy).fetchall()
	data9 = [x[0] for x in data9]
	print(data9)	
	
	
	
	
	
	
	
	
	
	
	