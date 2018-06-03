# Scrapeum toppinn á Wikipedia
	# og mynd líka?

	
import sqlite3
import wikipedia

dbURL = "C:/Users/Valdi/Desktop/Ferdasja sumar/database.db"
con = sqlite3.connect(dbURL)
cur = con.cursor()

query  = cur.execute("SELECT city FROM Prices")
res = cur.fetchall()
cities = [x[0] for x in res]

correctedNames = []

for city in cities: 
	print(wikipedia.summary(city, sentences = 4))