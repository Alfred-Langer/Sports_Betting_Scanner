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


def firstWebsiteSPORTParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))

    try:
        numberOfLocalHTMLFiles = len(os.listdir(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles"))
        for index in range(1,numberOfLocalHTMLFiles):
            with open(os.getcwd() + "/localHTMLFiles/firstWebsiteHTMLFiles/page" + str(index) + ".html",'rb') as fp:
                soup = BeautifulSoup(fp, "html.parser")
                oddBlocks = soup.find_all("div",class_=os.getenv("FIRST_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME"))
                valuableOddBlocks = [value for value in oddBlocks if (len(value.text.split()) > 1) and ("." in value.text) and ((value.text.split()[0] == "Match" and value.text.split()[1] == "Winner") or (value.text.split()[0] == "Handicap") or (value.text.split()[0] == "Total" and value.text.split()[1] == "Points" and value.text.split()[2]=="Over/Under") or (value.text.split()[0] == "Total" and value.text.split()[1] == "Runs" and value.text.split()[2]=="Over/Under"))]
                
                teamOne = None
                teamTwo = None
                for block in valuableOddBlocks:
                    if "Match Winner" in block.text:
                        wholeMatchWinnerBlock = [value for value in block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME")) if "(incl. " in value.text]
                        if wholeMatchWinnerBlock == []:
                            continue
                        else:
                            wholeMatchWinnerBlock = wholeMatchWinnerBlock[0]
                        extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in wholeMatchWinnerBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                        moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in wholeMatchWinnerBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                        
                        teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                        if teamOne is None or teamTwo is None:
                            break         
                        currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)
                        currentMatchup.addMoneyLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)
                    elif "Handicap" in block.text:
                        handicapBlocks = block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME"))
                        for handicapBlock in handicapBlocks:
                            handicapOne,handicapTwo = [teamNameElement.text.upper().split("@\xa0")[1] for teamNameElement in handicapBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                            handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in handicapBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                            currentMatchup.addHandicapLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+"@"+handicapOne,teamTwo+"@"+handicapTwo)
                    elif "Over/Under" in block.text:
                        totalBlocks = block.find_all("div",class_=os.getenv("FIRST_WEBSITE_DATA_ROW_ELEMENT_CLASS_NAME"))
                        for totalBlock in totalBlocks:
                            totalBoundaryOne,totalBoundaryTwo = [teamNameElement.text.upper() for teamNameElement in totalBlock.find_all("div",class_=os.getenv('FIRST_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                            totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in totalBlock.find_all("span",class_=os.getenv("FIRST_WEBSITE_ODD_ELEMENT_CLASS_NAME"))]
                            currentMatchup.addTotalLineOdds(os.getenv('FIRST_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
            
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content=str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")


def secondWebsiteSPORTParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
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
                    if "Money Line" in panel.text:
                        extractedTeamOne,extractedTeamTwo = [teamNameElement.text.upper() for teamNameElement in panel.find_all(class_=os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME'))]
                        moneyLineOddOne,moneyLineOddTwo = [oddElement.text for oddElement in panel.find_all(class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                            
                        teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                        if teamOne is None or teamTwo is None:
                            break
                        
                        currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                        if currentMatchup == None: 
                            currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  
                        currentMatchup.addMoneyLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

                    elif "Point Spread" in panel.text or "Run Line" in panel.text:
                        
                        handicaps = []
                        [handicaps.append(teamNameElement.text.upper()) for teamNameElement in panel.find_all("span",class_=os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME')) if teamNameElement.text.upper() not in handicaps and ("+" in teamNameElement.text or "-" in teamNameElement.text)]
                        handicapElements = panel.find_all("span",class_=os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME'))
                        if(len(handicapElements) == 3):
                            handicapOne = handicaps[1].text
                            handicapTwo = handicaps[2].text
                            handicapLineOddOne,handicapLineOddTwo = [oddElement.text for oddElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                            currentMatchup.addHandicapLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,teamOne+"@"+handicapOne,teamTwo+"@"+handicapTwo)

                    elif ("Total Points" in panel.text and "-" not in panel.text) or ("Total Runs" in panel.text and panel.text[0] == "T"):
                        totalBoundaryValue = panel.find("span", class_=os.getenv('SECOND_WEBSITE_HANDICAP_TOTAL_ELEMENT_CLASS_NAME'))
                        totalBoundaries = []
                        [totalBoundaries.append(teamNameElement.text.upper() + " " +totalBoundaryValue.text)  for teamNameElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_TEAM_ELEMENT_CLASS_NAME')) if teamNameElement.text.upper() not in totalBoundaries]
                        totalBoundaryOne,totalBoundaryTwo = totalBoundaries
                        totalLineOddOne,totalLineOddTwo = [oddElement.text for oddElement in panel.find_all("div",class_=os.getenv('SECOND_WEBSITE_ODD_ELEMENT_CLASS_NAME'))]
                        currentMatchup.addTotalLineOdds(os.getenv('SECOND_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
    
    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")


def thirdWebsiteSPORTParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
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

                teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
                if teamOne is None or teamTwo is None:
                    continue
                
                
                currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
                if currentMatchup == None: 
                    currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  



                moneyLineOddOne = htmlElementsThatHaveOddsForEvents[index].text.replace("Odds Decreased", "").replace("Odds Increased", "")
                moneyLineOddTwo = htmlElementsThatHaveOddsForEvents[index+1].text.replace("Odds Decreased", "").replace("Odds Increased", "")
                

                currentMatchup.addMoneyLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)

                if len(htmlElementsThatHaveOddsForEvents[index+2].text.split(".5",1)) > 1:
                    elementOne = htmlElementsThatHaveOddsForEvents[index+2].text.replace("Odds Decreased", "").replace("Odds Increased", "")
                    elementTwo = htmlElementsThatHaveOddsForEvents[index+3].text.replace("Odds Decreased", "").replace("Odds Increased", "")

                    handicapOne, handicapLineOddOne = elementOne.split(".5",1)
                    handicapTwo, handicapLineOddTwo = elementTwo.split(".5",1)
                    handicapOne = teamOne + "@" + handicapOne + ".5"
                    handicapTwo = teamTwo + "@" + handicapTwo + ".5"
                    currentMatchup.addHandicapLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)

                if htmlElementsThatHaveOddsForEvents[index+4].text != "" and htmlElementsThatHaveOddsForEvents[index+5].text != "":
                    elementOne = htmlElementsThatHaveOddsForEvents[index+4].text.replace("Odds Decreased", "").replace("Odds Increased", "")
                    elementTwo = htmlElementsThatHaveOddsForEvents[index+5].text.replace("Odds Decreased", "").replace("Odds Increased", "")

                    totalBoundaryOne = htmlElementsThatHaveOddsForEvents[index+4].select('span[class*="style_label__"]')[0].text
                    totalBoundaryTwo = htmlElementsThatHaveOddsForEvents[index+5].select('span[class*="style_label__"]')[0].text

                    totalLineOddOne = htmlElementsThatHaveOddsForEvents[index+4].select('span[class*="style_price__"]')[0].text
                    totalLineOddTwo = htmlElementsThatHaveOddsForEvents[index+5].select('span[class*="style_price__"]')[0].text


                    totalBoundaryOne = "OVER " + totalBoundaryOne 
                    totalBoundaryTwo = "UNDER " + totalBoundaryTwo 
                    currentMatchup.addTotalLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

    #Not entirely sure what exceptions can occur during this process, so until I know I'm going to catch every type of exception and send the message to the discord.
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")

    

def fourthWebsiteSPORTParserBeautifulSoup(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))
    
    try:
        with open(os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html",'rb') as fp:
            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(fp, "html.parser")

            # Find all div elements with class name "participant"
            team_divs = soup.find_all("div", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_BOTH_TEAMS_ELEMENT_CLASS_NAME_SPORT') in value)
            team_names = []

            # Loop through each participant div
            for team_div in team_divs:
                # Find all div elements with class name "teamName" inside the current participant div
                team_name_divs = team_div.find_all("div", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_SINGLE_TEAM_ELEMENT_CLASS_NAME_SPORT') in value)

                # Print out the text content of each team name div
                for team_name_div in team_name_divs:
                    team = team_name_div.text.upper()
                    if any(char.isdigit() for char in team):
                        for char_index in range(0,len(team)):
                            currentChar = team[char_index]
                            if currentChar.isdigit():
                                team_names.append(team[0:char_index])
                                break
                    else:
                        team_names.append(team)

            # Find all div elements with class name "participant"
            odd_columns = soup.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_COLUMN_ELEMENT_CLASS_NAME'))
            
            skipElements = len(soup.find_all("div", class_=os.getenv('FOURTH_WEBSITE_SKIP_ELEMENT_CLASS_NAME')))

            moneyLineColumn = []
            handicapLineOdds = []
            handicapLineBoundaries = []
            totalLineBoundaries = []
            totalLineOdds = []

            for column in odd_columns:

                if "Spread" in column.text or "Match Handicap" in column.text or "Run Line" in column.text:
                    handicapLineColumn = [value for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

                    for oddElement in handicapLineColumn:
                        handicapBoundary = oddElement.find("span", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME_SPORT') in value)
                        if handicapBoundary == [] or handicapBoundary == [""] or handicapBoundary is None:
                            handicapLineBoundaries.append("")
                        else:
                            handicapLineBoundaries.append(handicapBoundary.text)
                        
                        handicapOdd = oddElement.find("span", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_NON_MONEYLINE_ELEMENT_CLASS_NAME_SPORT') in value)
                        if handicapOdd == [] or handicapBoundary == [""] or handicapBoundary is None:
                            handicapLineOdds.append("")
                        else:
                            handicapLineOdds.append(handicapOdd.text)
                elif "Total" in column.text:
                    totalLineOddColumn = [value for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]
                    
                    for oddElement in totalLineOddColumn:
                        totalBoundary = oddElement.find("span", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME_SPORT') in value)
                        if totalBoundary == [] or totalBoundary is None or totalBoundary is None:
                            totalLineBoundaries.append("")
                        else:
                            totalLineBoundaries.append(totalBoundary.text)
                        
                        totalOdd = oddElement.find("span", class_=lambda value: value and os.getenv('FOURTH_WEBSITE_NON_MONEYLINE_ELEMENT_CLASS_NAME_SPORT') in value)
                        if totalOdd == [] or totalBoundary is None or totalBoundary is None:
                            totalLineOdds.append("")
                        else:
                            totalLineOdds.append(totalOdd.text)
                elif "Money Line" in column.text or "To Win" in column.text:
                    moneyLineColumn = [value.text if value.text != "OTB" else "" for value in column.find_all("div", class_=os.getenv('FOURTH_WEBSITE_ODD_BLOCK_ELEMENT_CLASS_NAME'))]

        for index in range(0,len(moneyLineColumn),2):
            if skipElements != 0:
                    skipElements = skipElements - 1
                    print("SKIP ELEMENT")
                    continue
            extractedTeamOne = team_names[index]
            extractedTeamTwo = team_names[index+1]
            teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
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
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc() + "\n==========================================================================")


def thirdWebsiteParserSelenium(sport:str,sportLeague:str,linkToBettingSite:str,tableName:str,mongoDatabase:Database,allMatchups:dict):
    parsingErrorWebhook = SyncWebhook.from_url(os.getenv('PARSING_ERROR_NOTIF'))

    # Set Firefox options
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    firefox_options.set_capability("pageLoadStrategy", "none")
    service = Service(executable_path="./geckodriver")
    driver = webdriver.Firefox(options=firefox_options, service=service)  

    # Load the webpage
    driver.get(linkToBettingSite)

    # Define the element you want to wait for
    element_locator = (By.CSS_SELECTOR, "div[class*='" + os.getenv('THIRD_WEBSITE_DATE_ELEMENT_CLASS_NAME') + "']")
    wait = WebDriverWait(driver, 30)

    # Wait until the element is present
    try:
        loadElement = wait.until(EC.presence_of_element_located(element_locator))
        driver.execute_script("window.stop();")
    except TimeoutError as inst:
        return None
    except Exception as inst:
        parsingErrorWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc()+ "\n==========================================================================")
        return None
    
    matchupRowElements = driver.find_elements(By.CSS_SELECTOR,"div[class*='" + os.getenv('THIRD_WEBSITE_ODD_ROW_ELEMENT_CLASS_NAME') + "']")
    matchupRowElements = [x for x in matchupRowElements if (x.find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_SKIP_ELEMENT_CLASS_NAME') + "']") == [] and x.find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']") != [])]


    for iterationElement in matchupRowElements:
        teamNames = iterationElement.find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_TEAM_ELEMENT_CLASS_NAME') + "']")

        extractedTeamOne = teamNames[0].text.upper().replace(" (MATCH)","")
        extractedTeamTwo = teamNames[1].text.upper().replace(" (MATCH)","")
        teamOne,teamTwo = databaseTeamNameCheck(extractedTeamOne,extractedTeamTwo,tableName,mongoDatabase)
        if teamOne is None or teamTwo is None:
            continue

        currentMatchup = Matchup.matchupExists(teamOne,teamTwo,allMatchups)
        if currentMatchup == None: 
            currentMatchup = Matchup(sport,sportLeague,teamOne,teamTwo,allMatchups)  

        allOddPairs= iterationElement.find_elements(By.CSS_SELECTOR,"div[class*='" + os.getenv('THIRD_WEBSITE_ODD_PAIR_ELEMENT_CLASS_NAME') + "']")
        parsedOddElements = []

        #The first step is to see if there are any alternate odds present. If there is, we are going to look at those odd markets first and add them to our parsed elements list.
        #An alternate odd is when there is an alternate button present. These buttons only appear for total and handicap odds. If either Handicap and Total Odds have the button we will parse those odds first
        alternateButtons = iterationElement.find_elements(By.CSS_SELECTOR,"div[class*='" + os.getenv('THIRD_WEBSITE_ALTERNATE_ODDS_ELEMENT_CLASS_NAME') + "']")
        for alternateButton in alternateButtons:
            alternateButton.click()
            time.sleep(1)
            handicapAndTotalOddPairs= alternateButton.find_elements(By.CSS_SELECTOR,"div[class*='" + os.getenv('THIRD_WEBSITE_ODD_PAIR_ELEMENT_CLASS_NAME') + "']")
            for oddPairs in handicapAndTotalOddPairs:
                if "+" in oddPairs.text or "-" in oddPairs.text:
                    oddButtons = oddPairs.find_elements(By.CSS_SELECTOR,"button[class*='" + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME') + "']")
                    handicapOne = teamOne + "@" + oddButtons[0].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                    handicapLineOddOne = oddButtons[0].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                    handicapTwo = teamTwo + "@" + oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                    handicapLineOddTwo = oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                    parsedOddElements.append(oddPairs.text)
                    currentMatchup.addHandicapLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)
                else:
                    oddButtons = oddPairs.find_elements(By.CSS_SELECTOR,"button[class*='" + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME') + "']")
                    totalBoundaryOneElement = oddButtons[0].find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']")
                    totalLineOddOneElement = oddButtons[0].find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']")
                    if totalBoundaryOneElement != [] and totalLineOddOneElement != []:
                        totalBoundaryOne= "OVER " + totalBoundaryOneElement[0].text
                        totalLineOddOne = totalLineOddOneElement[0].text
                        totalBoundaryTwo = "UNDER " + oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                        totalLineOddTwo = oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                        parsedOddElements.append(oddPairs.text)
                        currentMatchup.addTotalLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)

        #The next step is to look at the remaining odd elements that are present in the current row
        #The odds that are parsed here would be a Handicap or Total Odd line that doesn't have an alternate button and our Moneyline oddline becuase there is never an alternate button for the Moneyline
        for oddPairs in allOddPairs:
            if oddPairs.text in parsedOddElements:
                continue

            #Only handicap odds have a + or - in their odds so we can be sure that it's a handicap odd if either character is in the text
            if "+" in oddPairs.text or "-" in oddPairs.text:
                oddButtons = oddPairs.find_elements(By.CSS_SELECTOR,"button[class*='" + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME') + "']")
                handicapOne = teamOne + "@" + oddButtons[0].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                handicapLineOddOne = oddButtons[0].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                handicapTwo = teamTwo + "@" + oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                handicapLineOddTwo = oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                parsedOddElements.append(oddPairs.text)
                currentMatchup.addHandicapLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,handicapLineOddOne,handicapLineOddTwo,handicapOne,handicapTwo)
            
            #If we reach here then we know that we are dealing with a Total line or Money line
            else:
                #If there are no total boundaries present, then we know that we are dealing with a moneyline, otherwise it's a totaline.
                totalBoundaries = oddPairs.find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']")
                if totalBoundaries == [] and oddPairs.text != "":
                    moneyLineOddOne,moneyLineOddTwo = oddPairs.text.split("\n")
                    currentMatchup.addMoneyLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,teamOne,moneyLineOddOne,moneyLineOddTwo)
                    parsedOddElements.append(oddPairs.text)
                else:
                    oddButtons = oddPairs.find_elements(By.CSS_SELECTOR,"button[class*='" + os.getenv('THIRD_WEBSITE_ODD_ELEMENT_CLASS_NAME') + "']")
                    totalBoundaryOneElement = oddButtons[0].find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']")
                    totalLineOddOneElement = oddButtons[0].find_elements(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']")
                    if totalBoundaryOneElement != [] and totalLineOddOneElement != []:
                        totalBoundaryOne= "OVER " + totalBoundaryOneElement[0].text
                        totalLineOddOne = totalLineOddOneElement[0].text
                        totalBoundaryTwo = "UNDER " + oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_BOUNDARY_ELEMENT_CLASS_NAME') + "']").text
                        totalLineOddTwo = oddButtons[1].find_element(By.CSS_SELECTOR,"span[class*='" + os.getenv('THIRD_WEBSITE_ODDS_PRESENT_ELEMENT_CLASS_NAME') + "']").text
                        parsedOddElements.append(oddPairs.text)
                        currentMatchup.addTotalLineOdds(os.getenv('THIRD_WEBSITE'),linkToBettingSite,totalLineOddOne,totalLineOddTwo,totalBoundaryOne,totalBoundaryTwo)
        print('done')

    # Close the browser
    driver.quit()