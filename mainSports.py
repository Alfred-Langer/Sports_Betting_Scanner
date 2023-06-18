if True:
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
    from PythonScripts.Navigating_Chrome_Sports import firstWebsiteHTMLCollector,secondWebsiteHTMLCollector,thirdWebsiteHTMLCollector,fourthWebsiteHTMLCollector,firstSimpleWebsiteHTMLCollector, secondSimpleWebsiteHTMLCollector, thirdSimpleWebsiteHTMLCollector, fourthSimpleWebsiteHTMLCollector, openChrome,resetChrome,removeOldHTMLFiles, teamViewerClosePopup
    from PythonScripts.Beautiful_Soup_HTML_Parsing import firstWebsiteParserBeautifulSoup,secondWebsiteParserBeautifulSoup,thirdWebsiteParserBeautifulSoup,fourthWebsiteParserBeautifulSoup,firstWebsiteSimpleParserBeautifulSoup,secondWebsiteSimpleParserBeautifulSoup,thirdWebsiteSimpleParserBeautifulSoup,fourthWebsiteSimpleParserBeautifulSoup,firstWebsiteSPORTParserBeautifulSoup,secondWebsiteSPORTParserBeautifulSoup,fourthWebsiteSPORTParserBeautifulSoup
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


            currentFilePrefix = ""
            time.sleep(1)
            openChrome()
            #resetChrome()
            Matchup.arbitrageWebhook.send(content="Starting Iteration")
            try:
                print(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])
                for index in range(0,len(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])):
                
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

                    htmlCollectionT1 = Thread(target=firstWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],))
                    htmlCollectionT1.start()
                    htmlCollectionT1.join()

                    #htmlCollectionT2 = Thread(target=secondWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],))
                    #htmlCollectionT2.start()
                    parsingT1 = Thread(target=firstWebsiteSPORTParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                    parsingT1.start()
                    parsingT1.join()
                    #htmlCollectionT2.join()

                    htmlCollectionT3 = Thread(target=thirdWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],))
                    htmlCollectionT3.start()
                    #parsingT2 = Thread(target=secondWebsiteSPORTParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                    #parsingT2.start()
                    #parsingT2.join()
                    #htmlCollectionT3.join()

                    
                    htmlCollectionT4 = Thread(target=fourthWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],))
                    htmlCollectionT4.start()
                    parsingT3 = Thread(target=thirdWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                    parsingT3.start()
                    parsingT3.join()
                    htmlCollectionT4.join()

                    time.sleep(1)
                    parsingT4 = Thread(target=fourthWebsiteSPORTParserBeautifulSoup,args =(ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv(currentFilePrefix+'SPORT_BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Table Name'],mongoDB,allMatchups))
                    parsingT4.start()
                    parsingT4.join()

                    for hash, matchup in allMatchups.items():
                        matchup.arbitrageCheck(dataframeInformation)
                        matchup.handicapArbitrageCheck(dataframeInformation)
                        matchup.totalArbitrageCheck(dataframeInformation)

                    bettingOpportunities = pd.DataFrame(dataframeInformation)
                    fileName = ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['Sport'] + ast.literal_eval(os.getenv(currentFilePrefix+'SPORTS_LEAGUES'))[index]['League'] + ".csv"
                    bettingOpportunities.to_csv(fileName, mode='w', index=False)
                    os.system("pkill chrome")

            except Exception as inst:
                generalErroWebhook.send(content = str(inst)+ " - " +str(type(inst)) + "\n\n" + traceback.format_exc() + "\n==========================================================================")
            