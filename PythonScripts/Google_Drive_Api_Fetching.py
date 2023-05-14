from PythonScripts.Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
from  PythonScripts.Env_File_ID import id
import os 
import io

def getEnvFile():
    CLIENT_SECRET_FILE = os.getcwd() + '/Google_Api_Files/Client_Secret_Arb_App.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)

    file_id = id
    file_name = '.env'

    request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh,request=request)
    done = False
    while not done:
        status, done= downloader.next_chunk()
        print("Download progress {0}".format(status.progress() * 100))

    fh.seek(0)

    with open(os.getcwd()+"/PythonScripts/"+file_name,'wb') as f:
        f.write(fh.read())
        f.close()

def modifyEnvFile():
    print(os.getcwd())
    f = open(os.getcwd()+"/PythonScripts/.env", "r")
    test = f.read()
    firstHalf = test.split("ESPORT_BETTING_SITE_LINK_DICTIONARY")[0]

    secondHalf = "ESPORT_BETTING_SITE_LINK_DICTIONARY" + test.split("ESPORT_BETTING_SITE_LINK_DICTIONARY")[1]
    esportsBettingSiteLinkDictionary = secondHalf.split("ESPORTS_LEAGUES")[0].replace("\n", "")
    
    esportsLeaguesAndBeyond = "ESPORTS_LEAGUES" + secondHalf.split("ESPORTS_LEAGUES")[1]

    esportsLeagues = esportsLeaguesAndBeyond.split("SPORT_BETTING_SITE_LINK_DICTIONARY")[0].replace("\n","")

    sportsBettingSiteLinkDictionaryAndBeyond = "SPORT_BETTING_SITE_LINK_DICTIONARY" + esportsLeaguesAndBeyond.split("SPORT_BETTING_SITE_LINK_DICTIONARY")[1]

    sportsBettingSiteLinkDictionary = sportsBettingSiteLinkDictionaryAndBeyond.split("SPORTS_LEAGUES")[0].replace("\n","")

    sportsLeagues = "SPORTS_LEAGUES" + sportsBettingSiteLinkDictionaryAndBeyond.split("SPORTS_LEAGUES")[1].replace("\n","")

    f.close()
    f2 = open(os.getcwd()+"/PythonScripts/.env",'w')
    f2.write(firstHalf + "\n" + esportsBettingSiteLinkDictionary + "\n" + esportsLeagues + "\n" + sportsBettingSiteLinkDictionary + "\n" + sportsLeagues)
    f2.close()