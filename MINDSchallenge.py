# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:08:58 2020

@author: aneri
"""

import requests
import pandas as pd
import bs4
from tldextract import extract
from datetime import datetime


#initializing variables
dict = {}
daysOfMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
start = 4

for (monthNum,monthDays) in enumerate(daysOfMonths):
    for i in range(1, monthDays+1):
        if i<10:
            date = '0' + str(i)
        else:
            date = str(i)
        if monthNum<9:
            month = '0'+ str(monthNum+1)
        else:
            month = str(monthNum+1)
        formattedDate = datetime.strptime(date + " " + month + " 2019", "%d %m %Y")
        isoFormattedDate = formattedDate.isoformat() + "+00:00"
        dict[isoFormattedDate] = 0
#request the page source code
res = requests.get("https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches")
soup = bs4.BeautifulSoup(res.text,'lxml')

#Select all the tables in the html source code of the page
table = soup.select('.wikitable')

#Select the first table from the list of tables - the orbital launches table
myTable = table[0]

#Get all rows in the table
allRows = myTable.findAll('tr')

#Loop while rows exist
while start<len(allRows):
    
    #skip row with nav box
    if allRows[start].find_all("table", {"class": "navbox"}):
        start = start + 2
        continue
    
    #get the row with date 
    dateRow = allRows[start].find_all('span', attrs={'class':'nowrap'})
    currentDate = str(dateRow[0].text)
    
    #remove references from dates, if they exist
    if(not currentDate.find('[')==-1):
        currentDate = currentDate[0:currentDate.find('[')]
    
    #convert date to ISO format
    formattedDate = datetime.strptime(currentDate.split(' ')[0]+' '+ currentDate.split(' ')[1]+ ' 2019 00:00:00', '%d %B %Y %H:%M:%S')
    isoFormatDate = formattedDate.isoformat() + "+00:00"
    #calculate the number of payloads for a single launch using rowspan
    numberOfLaunches = allRows[start].findAll('td')
    totalLoads = int(numberOfLaunches[0].get("rowspan")) 

    #iterate through each payload 
    for i in range(start+1, start+totalLoads):
        allPayloadRows = allRows[i].findAll('td')
        status = str(allPayloadRows[-1].text)
        status = str(status.lower())

        #add to a dictionary if successful/operations/en route
        if "successful" in status or "operational" in status or "en route" in status:
            if isoFormatDate in list(dict.keys()):
                dict[isoFormatDate]+=1
            else:
                dict[isoFormatDate] = 1
            break
        
    #increment start to the next date
    start = start+totalLoads
    
#dump the data to a csv file
df = pd.DataFrame(list(zip(list(dict.keys()), list(dict.values()))), columns =['Date', 'Value']) 
df.to_csv('output.csv', index = False)
