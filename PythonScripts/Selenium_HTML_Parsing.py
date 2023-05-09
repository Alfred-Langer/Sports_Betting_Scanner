import os
import mysql.connector
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from Matchup_Class import Matchup
from discord import SyncWebhook
import traceback
from bs4 import BeautifulSoup


def databaseTeamNameCheck(nameOne:str,nameTwo:str,tableName:str,myCursorObject:mysql.connector.cursor.MySQLCursor):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    myCursorObject.execute('SELECT valueTeamName FROM ' + tableName + ' WHERE keyTeamName = "' + nameOne + '"')
    teams = myCursorObject.fetchall()
    teamOne = teams[0]
    myCursorObject.execute('SELECT valueTeamName FROM ' + tableName + ' WHERE keyTeamName = "' + nameTwo + '"')
    teams = myCursorObject.fetchall()
    teamTwo = teams[0]

    if teamOne is None:
        #Discord Message saying that nameOne does not exist in MySQL Database
        parsingErrorWebhook.send(content=nameOne + " Does not exist in MySQL Database. Update whenever possible")
    else:
        teamOne = teamOne[0]
    if teamTwo is None:
        #Discord Message saying that nameTwo does not exist in MySQL Database
        parsingErrorWebhook.send(content=nameTwo + " Does not exist in MySQL Database. Update whenever possible")
    else:
        teamTwo = teamTwo[0]
    
    return teamOne,teamTwo


def firstWebsiteParser(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,driver:WebDriver,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))

    try:
        numberOfLocalHTMLFiles = len(os.listdir(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles"))
        for index in range(1,numberOfLocalHTMLFiles + 1):
            driver.get("file:///" + os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles/page" + str(index) + ".html")

            oddBlocks = driver.find_elements(By.CLASS_NAME, 'match-market-block')
            
            valuableOddBlocks = []
            for block in oddBlocks:
                textSplitUp = block.text.split("\n")
                title = textSplitUp[0]
                if ((len(textSplitUp)> 1) and ("." in block.text) and (title == "Match Winner" or title == "Map Handicap" or title == "Total Maps Played Over/Under")):
                    valuableOddBlocks.append(block)
                    if (len(valuableOddBlocks) == 3):
                        break

            teamOne = None
            teamTwo = None
            
            for block in valuableOddBlocks:
                if "Match Winner" in block.text:
                    wholeMatchWinnerBlock = [value for value in block.find_elements(By.XPATH,".//div[@class='" + os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME") +"']") if "Match Winner" in value.text][0]
                    extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in wholeMatchWinnerBlock.find_elements(By.XPATH,".//div[@class='" + os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME') +"']")]
                    moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in wholeMatchWinnerBlock.find_elements(By.XPATH,".//span[@class='"+os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME")+"']")]
                    
                    teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
                    if teamOne is None or teamTwo is None:
                        break         
                    currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)
                    currentMatchup.addMoneyLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)         
                
                elif "Map Handicap" in block.text:
                    handicapBlock = block.find_element(By.XPATH,".//div[@class='"+os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME")+"']")
                    handicapOne,handicapTwo = [teamNameElement.text.upper().split("@ ")[1] for teamNameElement in handicapBlock.find_elements(By.XPATH,".//div[@class='" + os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME') +"']")]
                    handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in handicapBlock.find_elements(By.XPATH,".//span[@class='"+os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME")+"']")]
                    currentMatchup.addHandicapLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+handicapOne,teamTwo+handicapTwo)
                
                elif "Total Maps Played Over/Under" in block.text:
                    totalBlock = block.find_element(By.XPATH,".//div[@class='"+os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME")+"']")
                    totalBoundaryOne,totalBoundaryTwo = [teamNameElement.text.upper() for teamNameElement in totalBlock.find_elements(By.XPATH,".//div[@class='" + os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME') +"']")]
                    totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in totalBlock.find_elements(By.XPATH,".//span[@class='"+os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME")+"']")]
                    currentMatchup.addTotalLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
    
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=traceback.format_exc())



def secondWebsiteParser(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,driver:WebDriver,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:

        numberOfLocalHTMLFiles = len(os.listdir(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles"))
        for index in range(1,numberOfLocalHTMLFiles + 1):
            driver.get("file:///" + os.getcwd() + "/localHTMLFiles/secondWebsiteHTMLFiles/page" + str(index) + ".html")
            collapsibleOddPanels = driver.find_elements(By.XPATH, "//div[@class='"+os.getenv('SECOND_WEBSITE_PANEL_ELEMENT_CLASS_NAME')+"']")

            teamOne = None
            teamTwo = None
            for panel in collapsibleOddPanels:
                if "Match Winner" in panel.text and "&" not in panel.text:
                    extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in panel.find_elements(By.CLASS_NAME,os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                    moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in panel.find_elements(By.CLASS_NAME,os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                    
                    teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
                    if teamOne is None or teamTwo is None:
                        break
                    
                    currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                    if currentMatchup == None: 
                        currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
                    currentMatchup.addMoneyLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)
                
                elif "Maps Handicap" in panel.text:
                    handicaps = []
                    [handicaps.append(teamNameElement.text.upper()) for teamNameElement in panel.find_elements(By.XPATH,".//span[@class='"+os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME')+"']") if teamNameElement.text.upper() not in handicaps and ("+" in teamNameElement.text or "-" in teamNameElement.text)]
                    handicapOne,handicapTwo = handicaps
                    handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in panel.find_elements(By.XPATH,".//div[@class='"+os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME')+"']")]
                    currentMatchup.addHandicapLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+handicapOne,teamTwo+handicapTwo)

                elif "Maps Total" in panel.text:
                    totalBoundaryValue = panel.find_element(By.XPATH,".//span[@class='"+os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME')+"']")
                    totalBoundaries = []
                    [totalBoundaries.append(teamNameElement.text.upper() + " " +totalBoundaryValue.text)  for teamNameElement in panel.find_elements(By.XPATH,".//div[@class='"+os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME')+"']") if teamNameElement.text.upper() not in totalBoundaries]
                    totalBoundaryOne,totalBoundaryTwo = totalBoundaries
                    totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in panel.find_elements(By.XPATH,".//div[@class='"+os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME')+"']")]
                    currentMatchup.addTotalLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

    
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=traceback.format_exc())

def thirdWebsiteParser(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,driver:WebDriver,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        driver.get("file:///" + os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html")  
        teamNames = driver.find_elements(By.XPATH,"//*[contains(@class, '"+os.getenv('THIRD_WEBSITE_TEAM_ELEMENT_CLASS_NAME')+"')]")
        htmlElementsThatHaveOddsForEvents = driver.find_elements(By.XPATH,"//button[contains(@class, '"+os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME')+"')]")

        skipElements = driver.find_elements(By.XPATH,"//span[contains(@class, '"+os.getenv('THIRD_WEBSITE_SKIP_ELEMENT_CLASS_NAME')+"')]")
        for index in range(len(skipElements)):
            teamNames.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)
            htmlElementsThatHaveOddsForEvents.pop(0)


        for index in range(0,len(htmlElementsThatHaveOddsForEvents),6):

            currentTeamNameElementTextList = teamNames[int(index/6)].text.split("\n")
            extractedTeamOne = currentTeamNameElementTextList[0].upper().replace(" (MATCH)","")
            extractedTeamTwo = currentTeamNameElementTextList[1].upper().replace(" (MATCH)","")

            teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
            if teamOne is None or teamTwo is None:
                continue


            #This should be looked at to see if this can be more efficient. (I don't like addMoneyLineOdds being present in both cases) Normally I would add Money line odds outside and after the if/else statement, but the arbitrage check require the odds to present in the matchup prior. I can't add the odds before the if/else statement because you can't add them to None, if the matchup doesn't exist.
            currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
            if currentMatchup == None: 
                currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
            
            moneyLineOddOne = htmlElementsThatHaveOddsForEvents[index].text
            moneyLineOddTwo = htmlElementsThatHaveOddsForEvents[index+1].text
            currentMatchup.addMoneyLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

            if len(htmlElementsThatHaveOddsForEvents[index+2].text.split(".5",1)) > 1:
                handicapOne, handicapLineOddOne = htmlElementsThatHaveOddsForEvents[index+2].text.split(".5",1)
                handicapTwo, handicapLineOddTwo = htmlElementsThatHaveOddsForEvents[index+3].text.split(".5",1)
                handicapOne = teamOne + handicapOne + ".5"
                handicapTwo = teamTwo + handicapTwo + ".5"
                currentMatchup.addHandicapLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)

            if len(htmlElementsThatHaveOddsForEvents[index+4].text.split(".5",1)) > 1:
                totalBoundaryOne, totalLineOddOne = htmlElementsThatHaveOddsForEvents[index+4].text.split(".5",1)
                totalBoundaryTwo, totalLineOddTwo = htmlElementsThatHaveOddsForEvents[index+5].text.split(".5",1)
                totalBoundaryOne = "OVER " + totalBoundaryOne + ".5"
                totalBoundaryTwo = "UNDER " + totalBoundaryTwo + ".5"
                currentMatchup.addTotalLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)


    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=traceback.format_exc())

def fourthWebsiteParser(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,driver:WebDriver,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
    #for index in range(1):
        driver.get("file:///"+os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html")  
        teamNames = driver.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))
        oddColumns = driver.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_COLUMN_ELEMENT_CLASS_NAME'))
        moneyLineColumn = None
        totalLineColumn = None
        handicapLineColumn = None
        for element in oddColumns:
            if "Spread" in element.text or "Match Handicap" in element.text:
                handicapLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
            elif "Total" in element.text:
                totalLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
            elif "Money Line" in element.text or "To Win" in element.text:
                moneyLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

        for index in range(0,len(moneyLineColumn),2):
            currentTeamNameElementTextList = teamNames[int(index/2)].text.split("\n")
            extractedTeamOne = currentTeamNameElementTextList[1].upper()
            extractedTeamTwo = currentTeamNameElementTextList[2].upper()

            teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
            if teamOne is None or teamTwo is None:
                continue

            currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
            if currentMatchup == None: 
                currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)

            moneyLineOddOne = moneyLineColumn[index]
            moneyLineOddTwo = moneyLineColumn[index+1]
            currentMatchup.addMoneyLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

            if handicapLineColumn != [] and handicapLineColumn[index] != "":
                handicapOne,handicapLineOddOne = handicapLineColumn[index].split("\n")
                handicapTwo,handicapLineOddTwo = handicapLineColumn[index+1].split("\n")
                currentMatchup.addHandicapLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)
            
            if totalLineColumn != [] and totalLineColumn[index] != "":
                totalBoundaryOne,totalLineOddOne = totalLineColumn[index].split("\n")
                totalBoundaryTwo,totalLineOddTwo = totalLineColumn[index+1].split("\n")
                totalBoundaryOne = totalBoundaryOne.replace("O","OVER")
                totalBoundaryTwo = totalBoundaryTwo.replace("U","UNDER")
                currentMatchup.addTotalLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

    except Exception:
        parsingErrorWebhook.send(content=traceback.format_exc())


def firstWebsiteParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))

    try:
        numberOfLocalHTMLFiles = len(os.listdir(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles"))
        for index in range(1,numberOfLocalHTMLFiles):
            with open(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles/page" + str(index) + ".html",'rb') as fp:
                soup = BeautifulSoup(fp, "html.parser")
                oddBlocks = soup.find_all("div",class_=os.getenv("FIRST_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME"))
                valuableOddBlocks = [value for value in oddBlocks if (len(value.text.split()) > 1) and ("." in value.text) and ((value.text.split()[0] == "Match" and value.text.split()[1] == "Winner") or (value.text.split()[0] == "Map" and value.text.split()[1] == "Handicap") or (value.text.split()[0] == "Total" and value.text.split()[1] == "Maps" and value.text.split()[2]=="Played" and value.text.split()[3]=="Over/Under"))]
                
                teamOne = None
                teamTwo = None
                for block in valuableOddBlocks:
                    if "Match Winner" in block.text:
                        wholeMatchWinnerBlock = [value for value in block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME")) if "Match Winner" in value.text][0]
                        extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in wholeMatchWinnerBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                        moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in wholeMatchWinnerBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                        
                        teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
                        if teamOne is None or teamTwo is None:
                            break         
                        currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)
                        currentMatchup.addMoneyLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)
                    elif "Map Handicap" in block.text:
                        handicapBlocks = block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME"))
                        for handicapBlock in handicapBlocks:
                            handicapOne,handicapTwo = [teamNameElement.text.upper().split("@\xa0")[1] for teamNameElement in handicapBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                            handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in handicapBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                            currentMatchup.addHandicapLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+"@"+handicapOne,teamTwo+"@"+handicapTwo)
                    elif "Total Maps Played Over/Under" in block.text:
                        totalBlocks = block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME"))
                        for totalBlock in totalBlocks:
                            totalBoundaryOne,totalBoundaryTwo = [teamNameElement.text.upper() for teamNameElement in totalBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                            totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in totalBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                            currentMatchup.addTotalLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
            
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=str(inst)+ " - " +str(type(inst)))


def secondWebsiteParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:

        numberOfLocalHTMLFiles = len(os.listdir(os.getcwd() + "/localHTMLFiles/secondWebsiteHTMLFiles"))
        for index in range(1,numberOfLocalHTMLFiles):
            with open(os.getcwd() + "/localHTMLFiles/secondWebsiteHTMLFiles/page" + str(index) + ".html",'rb') as fp:
                soup = BeautifulSoup(fp, "html.parser")
                collapsibleOddPanels = soup.find_all("div", class_=os.getenv('SECOND_WEBSITE_PANEL_ELEMENT_CLASS_NAME'))

                teamOne = None
                teamTwo = None

                for panel in collapsibleOddPanels:
                    if "Match Winner" in panel.text and "&" not in panel.text:
                        extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in panel.find_all(class_=os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                        moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in panel.find_all(class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                            
                        teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
                        if teamOne is None or teamTwo is None:
                            continue
                        
                        currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                        if currentMatchup == None: 
                            currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
                        currentMatchup.addMoneyLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

                    elif "Maps Handicap" in panel.text:
                        handicaps = []
                        [handicaps.append(teamNameElement.text.upper()) for teamNameElement in panel.find_all("span",class_=os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME')) if teamNameElement.text.upper() not in handicaps and ("+" in teamNameElement.text or "-" in teamNameElement.text)]
                        handicapOne,handicapTwo = handicaps
                        handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                        currentMatchup.addHandicapLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+"@"+handicapOne,teamTwo+"@"+handicapTwo)

                    elif "Maps Total" in panel.text:
                        totalBoundaryValue = panel.find("span", class_=os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME'))
                        totalBoundaries = []
                        [totalBoundaries.append(teamNameElement.text.upper() + " " +totalBoundaryValue.text)  for teamNameElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME')) if teamNameElement.text.upper() not in totalBoundaries]
                        totalBoundaryOne,totalBoundaryTwo = totalBoundaries
                        totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                        currentMatchup.addTotalLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
    
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=inst)

def thirdWebsiteParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        with open(os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html",'rb') as fp:
            soup = BeautifulSoup(fp, "html.parser")
            teamNames = soup.select('span[class*="' + os.getenv('THIRD_WEBSITE_TEAM_ELEMENT_CLASS_NAME')+'"]')
            htmlElementsThatHaveOddsForEvents = soup.select('button[class*="' + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME')+'"]')
            skipElements = soup.select('span[class*="' + os.getenv('THIRD_WEBSITE_SKIP_ELEMENT_CLASS_NAME')+'"]')

            for index in range(len(skipElements)):
                teamNames.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)
                htmlElementsThatHaveOddsForEvents.pop(0)


            for index in range(0,len(htmlElementsThatHaveOddsForEvents),6):

                teamNameIndex = index // 3
                extractedTeamOne = teamNames[teamNameIndex].text.upper().replace(" (MATCH)","")
                extractedTeamTwo = teamNames[teamNameIndex + 1].text.upper().replace(" (MATCH)","")

                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
                if teamOne is None or teamTwo is None:
                    continue
                
                
                currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                if currentMatchup == None: 
                    currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  

                moneyLineOddOne = htmlElementsThatHaveOddsForEvents[index].text
                moneyLineOddTwo = htmlElementsThatHaveOddsForEvents[index+1].text
                currentMatchup.addMoneyLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

                if len(htmlElementsThatHaveOddsForEvents[index+2].text.split(".5",1)) > 1:
                    handicapOne, handicapLineOddOne = htmlElementsThatHaveOddsForEvents[index+2].text.split(".5",1)
                    handicapTwo, handicapLineOddTwo = htmlElementsThatHaveOddsForEvents[index+3].text.split(".5",1)
                    handicapOne = teamOne + "@" + handicapOne + ".5"
                    handicapTwo = teamTwo + "@" + handicapTwo + ".5"
                    currentMatchup.addHandicapLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)

                if len(htmlElementsThatHaveOddsForEvents[index+4].text.split(".5",1)) > 1:
                    totalBoundaryOne, totalLineOddOne = htmlElementsThatHaveOddsForEvents[index+4].text.split(".5",1)
                    totalBoundaryTwo, totalLineOddTwo = htmlElementsThatHaveOddsForEvents[index+5].text.split(".5",1)
                    totalBoundaryOne = "OVER " + totalBoundaryOne + ".5"
                    totalBoundaryTwo = "UNDER " + totalBoundaryTwo + ".5"
                    currentMatchup.addTotalLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=inst)

def fourthWebsiteParser(sport:str,sportLeague:str,linkToBettingSite:str,driver:WebDriver,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict,dataframeInformation:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        driver.get(os.getcwd() + "\\localHTMLFiles\\fourthWebsiteHTMLFiles\\page.html")  
        teamNames = driver.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))
        oddColumns = driver.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_COLUMN_ELEMENT_CLASS_NAME'))
        moneyLineColumn = None
        totalLineColumn = None
        handicapLineColumn = None
        for element in oddColumns:
            if "Spread" in element.text or "Match Handicap" in element.text:
                handicapLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
            elif "Total" in element.text:
                totalLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
            elif "Money Line" in element.text or "To Win" in element.text:
                moneyLineColumn = [value.text for value in element.find_elements(By.CLASS_NAME,os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

        for index in range(0,len(moneyLineColumn),2):
            currentTeamNameElementTextList = teamNames[int(index/2)].text.split("\n")
            extractedTeamOne = currentTeamNameElementTextList[1].upper()
            extractedTeamTwo = currentTeamNameElementTextList[2].upper()

            teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,myCursorObject)
            if teamOne is None or teamTwo is None:
                continue

            
            currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
            if currentMatchup == None: 
                currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups) 

            moneyLineOddOne = moneyLineColumn[index]
            moneyLineOddTwo = moneyLineColumn[index+1]
            currentMatchup.addMoneyLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

            if handicapLineColumn != [] and handicapLineColumn[index] != "":
                handicapOne,handicapLineOddOne = handicapLineColumn[index].split("\n")
                handicapTwo,handicapLineOddTwo = handicapLineColumn[index+1].split("\n")
                currentMatchup.addHandicapLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)
            
            if totalLineColumn != [] and totalLineColumn[index] != "":
                totalBoundaryOne,totalLineOddOne = totalLineColumn[index].split("\n")
                totalBoundaryTwo,totalLineOddTwo = totalLineColumn[index+1].split("\n")
                totalBoundaryOne = totalBoundaryOne.replace("O","OVER")
                totalBoundaryTwo = totalBoundaryTwo.replace("U","UNDER")
                currentMatchup.addTotalLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

            
            
    except Exception as inst:
        parsingErrorWebhook.send(content=inst)

def fourthWebsiteParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,myCursorObject:mysql.connector.cursor.MySQLCursor,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        with open(os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html",'rb') as fp:
            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(fp, "html.parser")

            # Find all div elements with class name "participant"
            team_divs = soup.find_all("div", class_=os.getenv('FOURTH_WEBSITE_BOTH_TEAMS_ELEMENT_CLASS_NAME'))
            team_names = []

            # Loop through each participant div
            for team_div in team_divs:
                # Find all div elements with class name "teamName" inside the current participant div
                team_name_divs = team_div.find_all("div", class_=os.getenv('FOURTH_WEBSITE_SINGLE_TEAM_ELEMENT_CLASS_NAME'))

                # Print out the text content of each team name div
                for team_name_div in team_name_divs:
                    team_names.append(team_name_div.text.upper())

            # Find all div elements with class name "participant"
            odd_columns = soup.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_COLUMN_ELEMENT_CLASS_NAME'))

            handicapLineOdds = []
            handicapLineBoundaries = []
            totalLineBoundaries = []
            totalLineOdds = []

            for column in odd_columns:
                if "Spread" in column.text or "Match Handicap" in column.text:
                    handicapLineColumn = [value for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

                    for oddElement in handicapLineColumn:
                        handicapBoundary = oddElement.find("span", class_=os.getenv('FOURTH_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME'))
                        if handicapBoundary == []:
                            handicapLineBoundaries.append("")
                        else:
                            handicapLineBoundaries.append(handicapBoundary.text)
                        
                        handicapOdd = oddElement.find("span", class_=os.getenv('FOURTH_WEBSITE_NON_MONEYLINE_ELEMENT_CLASS_NAME'))
                        if handicapOdd == []:
                            handicapLineOdds.append("")
                        else:
                            handicapLineOdds.append(handicapOdd.text)
                elif "Total" in column.text:
                    totalLineOddColumn = [value for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
                    
                    for oddElement in totalLineOddColumn:
                        totalBoundary = oddElement.find("span", class_=os.getenv('FOURTH_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME'))
                        if totalBoundary == []:
                            totalLineBoundaries.append("")
                        else:
                            totalLineBoundaries.append(totalBoundary.text)
                        
                        totalOdd = oddElement.find("span", class_=os.getenv('FOURTH_WEBSITE_NON_MONEYLINE_ELEMENT_CLASS_NAME'))
                        if totalOdd == []:
                            totalLineOdds.append("")
                        else:
                            totalLineOdds.append(totalOdd.text)
                elif "Money Line" in column.text or "To Win" in column.text:
                    moneyLineColumn = [value.text for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

        for index in range(0,len(moneyLineColumn),2):
            extractedTeamOne = team_names[index]
            extractedTeamTwo = team_names[index+1]
            teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,myCursorObject)
            if teamOne is None or teamTwo is None:
                continue

            currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
            if currentMatchup == None: 
                currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups) 

            moneyLineOddOne = moneyLineColumn[index]
            moneyLineOddTwo = moneyLineColumn[index+1]
            currentMatchup.addMoneyLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

            handicapOne = teamOne + "@" + handicapLineBoundaries[index]
            handicapTwo = teamTwo + "@" + handicapLineBoundaries[index+1]
            handicapLineOddOne = handicapLineOdds[index]
            handicapLineOddTwo = handicapLineOdds[index + 1]
            currentMatchup.addHandicapLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)
        
            totalLineOddOne = totalLineOdds[index]
            totalLineOddTwo = totalLineOdds[index+1]
            totalBoundaryOne = totalLineBoundaries[index].replace("O","OVER")
            totalBoundaryTwo = totalLineBoundaries[index+1].replace("U","UNDER")
            currentMatchup.addTotalLineOdds(os.getenv('FOURTH_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
            
            
    except Exception as inst:
        parsingErrorWebhook.send(content=inst)