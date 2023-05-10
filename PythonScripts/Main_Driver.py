if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    import os
    import ast
    import pandas as pd
    from Navigating_Chrome import firstWebsiteHTMLCollector,secondWebsiteHTMLCollector,thirdWebsiteHTMLCollector,fourthWebsiteHTMLCollector,openChrome,resetChrome,closeFirefox,removeOldHTMLFiles
    from Selenium_HTML_Parsing import firstWebsiteParserBeautifulSoup,secondWebsiteParserBeautifulSoup,thirdWebsiteParserBeautifulSoup,fourthWebsiteParserBeautifulSoup
    from threading import Thread
    from selenium import webdriver
    from datetime import datetime



    os.system("pkill chrome")
    os.system("pkill firefox")
    removeOldHTMLFiles()

  
    

    import mysql.connector
    #Database and Cursor Objects
    mydb = mysql.connector.connect(
        host=os.getenv('HOST'),
        user=os.getenv('USER'),
        database=os.getenv('DATABASE')
    )
    mycursor = mydb.cursor(buffered=True)
    
    
    
    while True: 
        removeOldHTMLFiles()
        for index in range(0,len(ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"])):
            
            allMatchups = {}
            dataframeInformation = {
                "Matchup Header":[],
                "Type of bet":[],
                "Team 1 Odd":[],
                "Team 2 Odd":[],
                "Arb Percentage":[],
                "Date":datetime.today().strftime("%Y-%m-%d"),
                "Hash":[]
            }
            openChrome()
            
            htmlCollectionT1 = Thread(target=firstWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],))
            htmlCollectionT1.start()
            htmlCollectionT1.join()

            parsingT1 = Thread(target=firstWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["firstWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mycursor,allMatchups))
            parsingT1.start()
            htmlCollectionT2 = Thread(target=secondWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],))
            htmlCollectionT2.start()
            parsingT1.join()
            htmlCollectionT2.join()

            parsingT2 = Thread(target=secondWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["secondWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mycursor,allMatchups))
            parsingT2.start()
            
            htmlCollectionT3 = Thread(target=thirdWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],))
            htmlCollectionT3.start()
            parsingT2.join()
            htmlCollectionT3.join()

            parsingT3 = Thread(target=thirdWebsiteParserBeautifulSoup, args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["thirdWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mycursor,allMatchups))
            parsingT3.start()

            htmlCollectionT4 = Thread(target=fourthWebsiteHTMLCollector,args=(ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],))
            htmlCollectionT4.start()
            #parsingT3.join()
            htmlCollectionT4.join()

            parsingT4 = Thread(target=fourthWebsiteParserBeautifulSoup,args =(ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'],ast.literal_eval(os.getenv('BETTING_SITE_LINK_DICTIONARY'))["fourthWebsite"][index],ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Table Name'],mycursor,allMatchups))
            parsingT4.start()
            parsingT4.join()

            for hash, matchup in allMatchups.items():
                matchup.arbitrageCheck(dataframeInformation)
                matchup.handicapArbitrageCheck(dataframeInformation)
                matchup.totalArbitrageCheck(dataframeInformation)

            bettingOpportunities = pd.DataFrame(dataframeInformation)
            fileName = ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['Sport'] + ast.literal_eval(os.getenv('SPORTS_LEAGUES'))[index]['League'] + ".csv"
            bettingOpportunities.to_csv(fileName, mode='w', index=False)
            os.system("pkill chrome")


        