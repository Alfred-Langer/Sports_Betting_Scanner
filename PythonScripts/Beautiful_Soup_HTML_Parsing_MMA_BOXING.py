import os
from pymongo.database import Database
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PythonScripts.Matchup_Class import Matchup
from discord import SyncWebhook
import traceback
import time
from bs4 import BeautifulSoup

def databaseTeamNameCheck(nameOne:str,nameTwo:str,tableName:str,mongoDatabase:Database):

        parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
        collection = mongoDatabase[tableName]
        result = collection.find_one({"keyTeamName":nameOne})
        if result is None:
            parsingErrorWebhook.send(content=traceback.format_exc())
            parsingErrorWebhook.send(content="We are most likely missing a team in a table in the database.\nTableName: " + tableName + "\nTeamNameOne: " + nameOne)
            teamOne = None
        else:
            teamOne = result["valueTeamName"]

        result = collection.find_one({"keyTeamName":nameTwo})
        if result is None:
            parsingErrorWebhook.send(content=traceback.format_exc())
            parsingErrorWebhook.send(content="We are most likely missing a team in a table in the database.\nTableName: " + tableName + "\nTeamNameTwo: " + nameTwo)
            teamTwo = None
        else:
            teamTwo = result["valueTeamName"]
    
        
        return teamOne,teamTwo


def firstWebsiteSimpleParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    try:
        with open(os.getcwd() + "/localHTMLFiles/firstWebsiteOrigin.html",'rb') as fp:
            soup = BeautifulSoup(fp,"html.parser")

        
            teamNames = soup.find_all("div",class_="outcome-name")
            odds = soup.find_all("div",class_="outcome-odds")
            for index in range(0,len(teamNames),2):
                extractedTeamOne = teamNames[index].text.upper()
                extractedTeamTwo = teamNames[index+1].text.upper()
                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                if teamOne is None or teamTwo is None:
                    continue   
                moneyLineOddOne = odds[index+0].text.replace("\n","").replace("\r","").replace("","")
                moneyLineOddTwo = odds[index+1].text.replace("\n","").replace("\r","").replace("","")
                currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)
                currentMatchup.addMoneyLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)       
                
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")


def secondWebsiteSimpleParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    if linkToBettingSite == "a":
        return
    try:
        with open(os.getcwd() + "/localHTMLFiles/secondWebsiteOrigin.html",'rb') as fp:
            soup = BeautifulSoup(fp,"html.parser")
            teamNames = soup.find_all("span",class_="teamNameFirstPart")
            odds = soup.find_all("div",class_="oddsDisplay")
            for index in range(0,len(teamNames),2):
                extractedTeamOne = teamNames[index].text.upper()
                extractedTeamTwo = teamNames[index+1].text.upper()
                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                moneyLineOddOne = odds[index+0].text
                moneyLineOddTwo = odds[index+1].text
                currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                if currentMatchup == None: 
                        currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
                currentMatchup.addMoneyLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)  

    
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")

def thirdWebsiteSimpleParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        with open(os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html",'rb') as fp:
            soup = BeautifulSoup(fp, "html.parser")
            teamNames = soup.select('span[class*="' + os.getenv('THIRD_WEBSITE_TEAM_ELEMENT_CLASS_NAME')+'"]')
            htmlElementsThatHaveOddsForEvents = soup.select('button[class*="' + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME')+'"]')
            skipElements = soup.select('span[class*="' + os.getenv('THIRD_WEBSITE_SKIP_ELEMENT_CLASS_NAME')+'"]')

            for index in range(len(skipElements)):
                teamNames.pop(0)
                if sport == "MMA":
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                elif sport == "BOXING":
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)
                    htmlElementsThatHaveOddsForEvents.pop(0)

            interval = 6 if sport=="MMA" else 4
            intervalDenominator = 3 if sport=="MMA" else 2

            for index in range(0,len(htmlElementsThatHaveOddsForEvents),interval):

                teamNameIndex = index // intervalDenominator
                extractedTeamOne = teamNames[teamNameIndex].text.upper()
                extractedTeamTwo = teamNames[teamNameIndex + 1].text.upper()

                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                if teamOne is None or teamTwo is None:
                    continue
                
                
                currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                if currentMatchup == None: 
                    currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  



                moneyLineOddOne = htmlElementsThatHaveOddsForEvents[index].text.replace("Odds Decreased", "").replace("Odds Increased", "")
                moneyLineOddTwo = htmlElementsThatHaveOddsForEvents[index+1].text.replace("Odds Decreased", "").replace("Odds Increased", "")
            
                currentMatchup.addMoneyLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

                
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")



def fourthWebsiteSimpleParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        with open(os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html",'rb') as fp:
            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(fp, "html.parser")

            # Find all div elements with class name "participant"
            teamNames = soup.find_all("div", class_='rcl-ParticipantFixtureDetailsTeam_TeamName')
            teamNames = [team for team in teamNames if team.text != "UFC"]
            odds = soup.find_all("span", class_='sgl-ParticipantOddsOnly80_Odds')
            halfOfOddsLength = len(odds) // 2

            oddIndex = 0
            for index in range(0,len(teamNames),2):
                extractedTeamOne = teamNames[index].text.upper()
                extractedTeamTwo = teamNames[index+1].text.upper()
                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                moneyLineOddOne = odds[oddIndex].text
                moneyLineOddTwo = odds[oddIndex+halfOfOddsLength].text
                currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                if currentMatchup == None: 
                        currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
                currentMatchup.addMoneyLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)  
                oddIndex += 1
            
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc() + "\n==========================================================================")