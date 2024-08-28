from bs4 import BeautifulSoup
import requests
import re
import time
import pandas
import os

class FightEntry:   
    def __init__(self, id=None, name=None, team=None, oppName=None, outcome=None, method=None, weightDiv=None, year=None) -> None:
        self.id = id
        self.name = name
        self.team = team
        self.oppName = oppName
        self.outcome = outcome
        self.method = method
        self.weightDiv = weightDiv
        self.year = year

    def __str__(self):
        return str(self.__dict__)

id = 0

def extractDataForOneFigher(url):
    global id
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    #print(soup.prettify())

    #find name
    # pattern = re.compile(r'Full Name')
    elem = soup.find("h1", itemprop="name")

    if not elem:
        return None

    #find "Full Name" which is inside <strong/> and then we need to get the <p/> so that's why we use .parent twice
    name = elem.getText()
    # name = elem.parent.parent.text[len("Full Name: "):]  
    print(name)

    # find weight division -> not necessary bc each fight might have different weight divisions. and I am not going to compare stats for different weights in absolute divs
    # pattern = re.compile(r'Weight Division')
    # elem = soup.find(string=pattern)
    # weightDiv = elem.parent.parent.text[len("Weight Division: "):]  

    #find school
    pattern = re.compile(r'(Team/Association:)|(Team/Affiliation:)')
    elem = soup.find("strong", string=pattern)
    if elem is not None:
        team = elem.parent.text[len("Team/Association: "):]  #i am lucky that words association and affiliation have the same number of letters - 11 
    else:
        team = "N/A" #freaking Abmar Barbosa - index 3 has messed up text on the page - fix that manually - his team is Abmar Barbosa Jiu Jitsu (formerly Drysdale Jiu Jitsu)

    fightEntriesList = []

    #*****individual fight info*******
    table = soup.find("table", class_="table table-striped sort_table")

    if table is not None:
        for row in table.tbody.contents:
            fightEntry = FightEntry()
            tds = row.find_all("td")
            # inside td: 1=name; 2=outcome; 3=method; 5=weightDiv; 7=year

            fightEntry.id = id
            fightEntry.name = name
            fightEntry.team = team
            fightEntry.oppName = tds[1].span.get_text()
            fightEntry.outcome = tds[2].get_text()
            fightEntry.method = tds[3].get_text()
            fightEntry.weightDiv = tds[5].get_text()
            fightEntry.year = tds[7].get_text()

            fightEntriesList.append(fightEntry)
            id += 1

    return fightEntriesList

def main():
    startTime = time.time()
    rootUrl = "https://www.bjjheroes.com"

    #extract all figher urls
    allFightersUrl = "https://www.bjjheroes.com/a-z-bjj-fighters-list"
    response = requests.get(allFightersUrl)
    soup = BeautifulSoup(response.text, "lxml")
    listOfNames = soup.find_all("td", {"class": "column-1"})

    listOfFights = []

    for name in listOfNames:       
        subUrl = name.a.get('href')
        urlOfFigher = rootUrl+subUrl
        singleFighterData = extractDataForOneFigher(urlOfFigher)
        if singleFighterData:
            for fight in singleFighterData:
                listOfFights.append(fight.__dict__)

    #****for testing****
    # for i in range(2):       
    #     subUrl = listOfNames[i].a.get('href')
    #     urlOfFigher = rootUrl+subUrl
    #     singleFighterData = extractDataForOneFigher(urlOfFigher)
    #     if singleFighterData:
    #         for fight in singleFighterData:
    #             listOfFights.append(fight.__dict__)

    print(len(listOfFights))
    print("***********")
    # for fight in listOfFights:
    #     print(fight)
    
    #print(listOfFights[0].keys())
    df = pandas.DataFrame(listOfFights)
    df.to_csv("bjj-heroes.csv")

    endTime = time.time()
    print(os.getcwd())
    print("Time elapsed: ", round(endTime-startTime, 2), " seconds")


#***********************************
main()



#todo
#id isn't technically necessary bc each row # is a unique identifier
#str bs