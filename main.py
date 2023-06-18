if __name__ == "__main__":
    from PythonScripts.Google_Drive_Api_Fetching import getEnvFile,modifyEnvFile
    getEnvFile()
    #modifyEnvFile()
    from PythonScripts.Setup_Environment_Variables import load
    load()
    from PythonScripts.Env_File_ID import esportPrefixes
    import time
    import os
    import ast
    import traceback
    import pandas as pd
    from PythonScripts.Navigating_Chrome import firstWebsiteHTMLCollector,secondWebsiteHTMLCollector,thirdWebsiteHTMLCollector,fourthWebsiteHTMLCollector,firstSimpleWebsiteHTMLCollector, secondSimpleWebsiteHTMLCollector, thirdSimpleWebsiteHTMLCollector, fourthSimpleWebsiteHTMLCollector, openChrome,resetChrome,removeOldHTMLFiles, teamViewerClosePopup
    from PythonScripts.Navigating_Chrome_Sports import firstWebsiteSportHTMLCollector,secondWebsiteSportHTMLCollector, thirdWebsiteSportHTMLCollector, fourthWebsiteSportHTMLCollector
    from PythonScripts.Beautiful_Soup_HTML_Parsing import firstWebsiteParserBeautifulSoup,secondWebsiteParserBeautifulSoup,thirdWebsiteParserBeautifulSoup,fourthWebsiteParserBeautifulSoup,firstWebsiteSPORTParserBeautifulSoup, secondWebsiteSPORTParserBeautifulSoup,thirdWebsiteSPORTParserBeautifulSoup, fourthWebsiteSPORTParserBeautifulSoup, thirdWebsiteParserSelenium
    from PythonScripts.Matchup_Class import Matchup
    from threading import Thread
    from datetime import datetime
    from pymongo import MongoClient
    from discord import SyncWebhook
    #time.sleep(5)
    #teamViewerClosePopup()
    os.system("pkill chrome")
    os.system("pkill firefox")
    cluster= MongoClient(os.getenv('MONGO_DB_CONNECTION_STRING'))
    mongoDB = cluster[os.getenv('MONGO_DB_NAME')]

    generalErroWebhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1107887959157526608/ZIbu0c4VWZKhecFuE8KPMw6GbTIJKkPpTQ4klCjisqn3-X7Gar4kdwxoN1E8ZKJ2jLNf')
    flag = True
    while True: 
        startIndex = 0 if flag else 0
        flag = False
        '''
        for file_index in range(startIndex,len(esportPrefixes)):

            currentFilePrefix = esportPrefixes[file_index]
            time.sleep(1)
            openChrome()
            resetChrome()
            Matchup.arbitrageWebhook.send(content="Starting Iteration")
            try:
                print(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])
                for index in range(0,len(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])):
                
                    removeOldHTMLFiles()
                    allMatchups = {}
                    dataframeInformation = {
                        "Matchup Header":[],
                        "Type of bet":[],
                        "Team 1 Odd":[],
                        "Team 2 Odd":[],
                        "Arb Percentage":[],
                        "Date":datetime.today().strftime("%Y-%m-%d")
                    }
                    openChrome()
                    
                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index] != 'a':
                        htmlCollectionT1 = Thread(target=firstWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],))
                        htmlCollectionT1.start()
                        htmlCollectionT1.join()

                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index] != 'a':
                        htmlCollectionT2 = Thread(target=secondWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],))
                        htmlCollectionT2.start()
                    
                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index] != 'a':
                        parsingT1 = Thread(target=firstWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                        parsingT1.start()
                        parsingT1.join()
                   
                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index] != 'a':
                        if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index] != 'a':
                            parsingT3 = Thread(target=thirdWebsiteParserSelenium, args =(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                            parsingT3.start()
                            parsingT3.join()
                        htmlCollectionT2.join()
                    
                    #if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index] != 'a':
                    #    htmlCollectionT3 = Thread(target=thirdWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],))
                    #    htmlCollectionT3.start()

                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index] != 'a':
                        parsingT2 = Thread(target=secondWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                        parsingT2.start()
                        parsingT2.join()

                    #if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index] != 'a':
                    #    htmlCollectionT3.join()

                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index] != 'a':
                        htmlCollectionT4 = Thread(target=fourthWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],))
                        htmlCollectionT4.start()

                    #if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index] != 'a':
                    #    parsingT3 = Thread(target=thirdWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                    #    parsingT3.start()
                    #    parsingT3.join()


                    if ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index] != 'a':
                        htmlCollectionT4.join()
                        time.sleep(1)
                        parsingT4 = Thread(target=fourthWebsiteParserBeautifulSoup,args =(ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                        parsingT4.start()
                        parsingT4.join()

                    for hash, matchup in allMatchups.items():
                        matchup.arbitrageCheck(dataframeInformation)
                        matchup.handicapArbitrageCheck(dataframeInformation)
                        matchup.totalArbitrageCheck(dataframeInformation)

                    bettingOpportunities = pd.DataFrame(dataframeInformation)
                    fileName = ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['Sport'] + ast.literal_eval(os.getenv(currentFilePrefix+'_ESPORTS_LEAGUES'))[index]['League'] + ".csv"
                    bettingOpportunities.to_csv(fileName, mode='w', index=False)
                    os.system("pkill chrome")

            except Exception as inst:
                generalErroWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc() + "\n==========================================================================")
        '''
        openChrome()
        resetChrome() 
        for index in range(1,len(ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])):    
            #removeOldHTMLFiles()
            allMatchups = {}
            dataframeInformation = {
                "Matchup Header":[],
                "Type of bet":[],
                "Team 1 Odd":[],
                "Team 2 Odd":[],
                "Arb Percentage":[],
                "Date":datetime.today().strftime("%Y-%m-%d")
            }
            openChrome()

            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index] != 'a':
                htmlCollectionT1 = Thread(target=firstWebsiteSportHTMLCollector,args=(ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],))
                htmlCollectionT1.start()
                htmlCollectionT1.join()

            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index] != 'a':
                htmlCollectionT2 = Thread(target=secondWebsiteSportHTMLCollector,args=(ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],))
                htmlCollectionT2.start()
            
            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index] != 'a':
                parsingT1 = Thread(target=firstWebsiteSPORTParserBeautifulSoup, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                parsingT1.start()
                parsingT1.join()
            
            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index] != 'a':
                parsingT3 = Thread(target=thirdWebsiteParserSelenium, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                parsingT3.start()
                parsingT3.join()
                htmlCollectionT2.join()

            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index] != 'a':
                parsingT2 = Thread(target=secondWebsiteSPORTParserBeautifulSoup, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                parsingT2.start()
                parsingT2.join()

            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index] != 'a':
                htmlCollectionT4 = Thread(target=fourthWebsiteSportHTMLCollector,args=(ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],))
                htmlCollectionT4.start()

            if ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index] != 'a':
                htmlCollectionT4.join()
                time.sleep(1)
                parsingT4 = Thread(target=fourthWebsiteSPORTParserBeautifulSoup,args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                parsingT4.start()
                parsingT4.join()

            for hash, matchup in allMatchups.items():
                matchup.arbitrageCheck(dataframeInformation)
                matchup.handicapArbitrageCheck(dataframeInformation)
                matchup.totalArbitrageCheck(dataframeInformation)

            bettingOpportunities = pd.DataFrame(dataframeInformation)
            fileName = ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'] + ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'] + ".csv"
            bettingOpportunities.to_csv(fileName, mode='w', index=False)
            #pd.DataFrame(allMatchups).to_csv("Matchups_"+fileName, mode = 'w', index = False)
            os.system("pkill chrome")
    