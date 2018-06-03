import matplotlib.pyplot as plt
import sqlite3 
import pandas as pd 
import mpld3
import numpy as np
import math
import random 
from matplotlib.font_manager import FontProperties


# væri cool að hafa piechartið eins og Distribution of expenses using our statistical model af numbeo
	# gæti fengist úr töflunni hér https://www.numbeo.com/cost-of-living/city-basket-analysis/in/Berlin 
	
# og fleiri upplýsingar um borgina 
	# wikipedia headerinn
	
# valið tímabil (sem er á forsíðunni) er default, annars má velja viku

# teiknum veðrið, hvernig?

# teiknum prices (sem histogram?) og costindeces (sem piechart ?)
# 	viljum hafa double histogram til að bera saman 2 ?
# bubblechart þar sem hver bubbla er mæld í dölum ?

# getum ekki teiknað saman dýra og ódýra á histogram 
	# sleppum bara dýru hlutunum þeir eru irrelevant 

# update Prices set 'mortgage' = replace('mortgage', ',', '')

# þyrfti að teikna bar með mismunandi einingum (°C, precipitation) í mismunandi litum 

# teiknum

def beforeComma(string):
	return string.split(",")[0]

	
dbURL = "C:/Users/Valdi/Desktop/Ferdasja sumar/database.db"
con = sqlite3.connect(dbURL)
cur = con.cursor()


def bubblePrices(city):

	irrelevantAttributes = ["City", "Monthly Pass", "Volkswagen Golf", "Toyota Corolla", "Basic Utilities", "Internet", "Fitness Club", "Tennis Court Rent", "Preschool Month", "Primary School Year", "Rent 1 Bedroom Center","Rent 1 Bedroom Outside Center","Rent 3 Bedrooms Center","Rent 3 Bedrooms Outside Center", "Price m2 Center","Price m2 Outside Center","Average Monthly Salary After Tax","Mortgage Interest Rate"]
	fyrirspurn = "SELECT * FROM Prices where City = " + '"' + beforeComma(city) + '"'
	print(fyrirspurn)
	query  = cur.execute(fyrirspurn)
	
	cols = [column[0] for column in query.description]
	
	results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
	results.drop(columns = irrelevantAttributes, inplace=True)
	print(results.columns.values)
	
	
	values = list(results.loc[0,:])[0:]
	names = []
	
	j = 0 
	for i in cols:
		if i not in irrelevantAttributes:
			names.append(i)
			
			j = j+1	
	
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize = (9,7))
	
	fyrirspurn = "SELECT * FROM Prices where city = " + '"' + beforeComma(city) + '"'
	print(fyrirspurn)
	query  = cur.execute(fyrirspurn)
	
	cols = [column[0] for column in query.description]
	
	
	results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
	results.drop(columns = irrelevantAttributes, inplace=True)
	
	
	
	values = list(results.loc[0,:])[0:]
	names = []
	
	j = 0 
	for i in cols:
		if i not in irrelevantAttributes:
			names.append(i)
			
			j = j+1	
	
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize = (9,7))
	
	

	
	
	N = len(values)
	col = np.random.rand(N)
	print(col)
	end = math.ceil(math.sqrt(N))
	# þurfum að gera samsvörun 
	step = end/N
	x = np.arange(0,end,step)
	hnitx = []
	for i in range(3,end+2):
		for j in range(end):
			if(len(hnitx) == N):
				break
			hnitx.append(i)
			
	hnity = []
	for i in range(N):
		hnity.append(i % end)
	
	#plt.figure(figsize=(9,9))
	
	hnitx = [x + random.random()/4 for x in hnitx]
	hnity = [y + random.random()/4 for y in hnity]	
	mynd = ax.scatter(hnitx, hnity, c = col, alpha = 0.5, s = [x*20 for x in values])
	plt.xlim((0.8,end+2))

	plt.xticks([], [])
	plt.yticks([], [])

	fig.patch.set_visible(False)
	ax.axis('off')

	font0 = FontProperties()
	font1 = font0.copy()
	font1.set_size('large')
	font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 13,
        }
	
	for label, x, y in zip(names, hnitx, hnity):
		r = random.random()*2
		plt.text(x+0.22, y+0.25, label,ha = 'right', va = 'bottom', fontdict=font)
		plt.plot([x+0.22,x], [y+0.25,y], 'k-', linewidth = 0.5)
	# þarf að sjá 

	font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 18,
        }	
	ax.set_title("Bubble chart of prices of goods in " + city + " (area = €)",fontdict=font)
	# vantar að staðfesta að röðin sé eins?
	

	tooltip = mpld3.plugins.PointLabelTooltip(mynd, labels=[str(x) + "€" for x in values])
	
	mpld3.plugins.connect(fig, tooltip)
	
	mpld3.show()
	
	

def doubleBubblePrices(city1,city2):

	irrelevantAttributes = ["City", "Monthly Pass", "Volkswagen Golf", "Toyota Corolla", "Basic Utilities", "Internet", "Fitness Club", "Tennis Court Rent", "Preschool Month", "Primary School Year", "Rent 1 Bedroom Center","Rent 1 Bedroom Outside Center","Rent 3 Bedrooms Center","Rent 3 Bedrooms Outside Center", "Price m2 Center","Price m2 Outside Center","Average Monthly Salary After Tax","Mortgage Interest Rate"]
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize = (9,7))
		
	plt.hold(True)
	
	k = 0 
	bothValues = []
	bothNames = []
	for city in [city1, city2]:
		fyrirspurn = "SELECT * FROM Prices where City = " + '"' + beforeComma(city) + '"'
		query  = cur.execute(fyrirspurn)
		
		cols = [column[0] for column in query.description]
		
		results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
		results.drop(columns = irrelevantAttributes, inplace=True)
		
		
		
		values = list(results.loc[0,:])[0:]
		names = []
		
		j = 0 
		for i in cols:
			if i not in irrelevantAttributes:
				names.append(i)
				
				j = j+1	
		bothValues.append(values)
		bothNames.append(names)
		
		
		
		if(k == 0):
			col = 'red'
			N = len(values)
			
			end = math.ceil(math.sqrt(N))
			# þurfum að gera samsvörun 
			step = end/N
			x = np.arange(0,end,step)
			hnitx = []
			for i in range(3,end+2):
				for j in range(end):
					if(len(hnitx) == N):
						break
					hnitx.append(i)
					
			hnity = []
			for i in range(N):
				hnity.append(i % end)
			
			#plt.figure(figsize=(9,9))
			
			hnitx = [x + random.random()/4 for x in hnitx]
			hnity = [y + random.random()/4 for y in hnity]	
		else:
			col = 'blue'
		k = k +1 
		
		
		
		mynd = ax.scatter(hnitx, hnity, c = col, alpha = 0.3, s = [x*20 for x in values])
		plt.xlim((0.8,end+2))

		plt.xticks([], [])
		plt.yticks([], [])

		

	font0 = FontProperties()
	font1 = font0.copy()
	font1.set_size('large')
	font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 10,
        }
	
	for label, x, y in zip(names, hnitx, hnity):
		r = random.randint(-1, 1)
		plt.text(x+0.22, y+r*0.25, label,ha = 'right', va = 'bottom', fontdict=font)
		plt.plot([x+0.22,x], [y+r*0.25,y], 'k-', linewidth = 0.5)
	# þarf að sjá 

	font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 18,
        }	
	ax.set_title("Bubble chart of prices of goods in " + city1 + " and " + city2 + " (area = €)",fontdict=font)
	# vantar að staðfesta að röðin sé eins?
	
	labels = [str(x) for x in bothValues[0]]
	print(labels)
	print("\n")
	print([str(x) + "," +  "€" for x in bothValues[1]])
	tooltip = mpld3.plugins.PointLabelTooltip(mynd, labels=[str(x) + " , " + str(y) +  " €" for x,y in zip(bothValues[0],bothValues[1])])
	
	mpld3.plugins.connect(fig, tooltip)
	
	mpld3.show()
	

	
	# relevantAttributes = list( set(cols) - set(irrelevantAttributes) )
	


	
bubblePrices("Reykjavik, Iceland")
	
	
	
	

def bubbleIndices(cost, city):
	if(cost):
		fyrirspurn = "SELECT * FROM CostOfLivingIndex where city = " + '"' + city + '"'
	else: 
		fyrirspurn = "SELECT * FROM QualityOfLifeIndex where city = " + '"' + city + '"'

	irrelevantAttributes = ["City", "Rank", "index"]		
	
	
	
	
	### allt fyrir neðan er sama og í Prices dæminu 
	print(fyrirspurn)
	query  = cur.execute(fyrirspurn)
	
	cols = [column[0] for column in query.description]
	

	results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
	results.drop(columns = irrelevantAttributes, inplace=True)
	
	
	
	values = list(results.loc[0,:])[0:]
	names = []
	
	j = 0 
	for i in cols:
		if i not in irrelevantAttributes:
			names.append(i)
			
			j = j+1	
	
	print(len(values))
	print(len(names))
	fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize = (9,7))
	
	N = len(values)

	#col = np.arange(0.1,0.99,0.98/N)
	col = np.random.random_integers(0,N-1)
	print(col)
	#print(len(col))
	colors = ['yellow', 'red', 'green', 'blue', 'black', 'purple', 'brown', 'pink']

	end = math.ceil(math.sqrt(N))
	# þurfum að gera samsvörun 
	step = end/N
	x = np.arange(0,end,step)
	hnitx = []
	for i in range(1,end+1):
		for j in range(end):
			if(len(hnitx) == N):
				break
			hnitx.append(i)
			
	hnity = []
	for i in range(N):
		hnity.append(i % end)
	
	#plt.figure(figsize=(9,9))
	
	# hnitx = [x + random.random()/4 for x in hnitx]
	# hnity = [y + random.random()/4 for y in hnity]	
	print(hnitx)
	print(hnity)
	mynd = ax.scatter(hnitx, hnity, c = colors, alpha = 0.5, s = [x*20 for x in values])
	plt.xlim((0,end))
	plt.ylim((-1,end))
	
	plt.xticks([], [])
	plt.yticks([], [])

	fig.patch.set_visible(False)
	ax.axis('off')


	
	font0 = FontProperties()
	font1 = font0.copy()
	font1.set_size('large')
	fonts = []
	for i in range(N):
	
		fonts.append(  {'family': 'serif',
			'color':  colors[i],
			'weight': 'normal',
			'size': 10,
			})
		
	j = 0 
	for label, x, y in zip(names, hnitx, hnity):
		
		plt.text(x+0.22, y+0.25, label,ha = 'right', va = 'bottom', fontdict=fonts[j])
		j = j+1
		#plt.plot([x+0.22,x], [y+0.25,y], 'k-', linewidth = 0.5)
	# þarf að sjá 

	font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 18,
        }	
	ax.set_title("Bubble chart of prices of goods in " + city + " (area = €)",fontdict=font)
	# vantar að staðfesta að röðin sé eins?
	

	tooltip = mpld3.plugins.PointLabelTooltip(mynd, labels=values)
	
	mpld3.plugins.connect(fig, tooltip)
	
	mpld3.show()
		

def bubblWeather():
	print("")




bubblePrices("venice, Italy")
# doubleBubblePrices("Reykjavik, Iceland", "Copenhagen, Denmark")
# doubleBubblePrices("Belgrade, Serbia", "Lisbon, Portugal")