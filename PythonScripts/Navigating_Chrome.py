import pyautogui
import time
import pyperclip
import re
import os
from discord import SyncWebhook
from bs4 import BeautifulSoup
import traceback



def findImageOnScreen(image:str, timeoutDuration:int, scrollFlag:bool = False, confidenceValue:float = 0.9, grayscaleFlag:bool = False, regionBox:tuple = (0,0,1920,1080)):
    timeout = time.time() + timeoutDuration 
    pictureLocation = None

    while  time.time() < timeout:
        try:
            picturePath = os.getcwd() + "/Screenshot_Images/" + image
            pictureLocation = pyautogui.locateCenterOnScreen(picturePath, confidence=confidenceValue, grayscale=grayscaleFlag, region=regionBox)
        except FileNotFoundError:
            raise ImageFileNotFoundError(os.getcwd() + "/Screenshot_Images/" + image, image)
        
        if pictureLocation != None:
            return pictureLocation
        elif scrollFlag:
            #Scroll Flag is specifically for locating the HTML Tags. Somtimes when you Inspect Element, the display shows the middle of the HTML content.
            #This block of code just clicks on the up arrow key of the Inspect Element scroll bar, in order to scroll up.
            pyautogui.click(1911,145,button='left',clicks=10)
        time.sleep(1) #Adding a sleep for 1 second here, apparently helps to reduce CPU Usage for this process.

    raise ImageNotFoundOnScreenError("ImageNotPresentError: Could not find " + image + " on the screen")

def findOneOfTheImagesOnScreen(images:tuple, timeoutDuration:int, scrollFlag:bool = False, confidenceValue:float = 0.9, grayscaleFlag:bool = False, regionBox:tuple = (0,0,1920,1080)):
    timeout = time.time() + timeoutDuration 
    pictureLocation = None

    while  time.time() < timeout:
        try:
            picturePath = os.getcwd() + "/Screenshot_Images/" + images[0]
            pictureLocation = pyautogui.locateCenterOnScreen(picturePath, confidence=confidenceValue, grayscale=grayscaleFlag, region = regionBox)
        except FileNotFoundError:
            raise ImageFileNotFoundError(os.getcwd() + "/Screenshot_Images/" + images[0], images[0])
        
        try:
            picturePath2 = os.getcwd() + "/Screenshot_Images/" + images[1]
            pictureLocation2 = pyautogui.locateCenterOnScreen(picturePath2, confidence=confidenceValue, grayscale=grayscaleFlag, region = regionBox)
        except FileNotFoundError:
            raise ImageFileNotFoundError(os.getcwd() + "/Screenshot_Images/" + images[1], images[1])
        
        if pictureLocation != None:
            return pictureLocation
        elif pictureLocation2 != None:
            return pictureLocation2
        elif scrollFlag:
            #Scroll Flag is specifically for locating the HTML Tags. Somtimes when you Inspect Element, the display shows the middle of the HTML content.
            #This block of code just clicks on the up arrow key of the Inspect Element scroll bar, in order to scroll up.
            pyautogui.click(1911,145,button='left',clicks=10)
        time.sleep(1) #Adding a sleep for 1 second here, apparently helps to reduce CPU Usage for this process.

    raise ImageNotFoundOnScreenError("ImageNotPresentError: Could not find " + images[0] + " or " + images[1] + " on the screen")

def selectAll():
    pyautogui.keyDown("ctrl")
    pyautogui.press("a")
    pyautogui.keyUp("ctrl")

def inspectElement():
    pyautogui.keyDown("ctrl")
    pyautogui.keyDown("shift")
    pyautogui.press("i")
    pyautogui.keyUp("ctrl")
    pyautogui.keyUp("shift")

def goToWebsite(url:str):
    #Click on the Address bar
    x,y = findImageOnScreen("bookmarkIcons.png",timeoutDuration = 5, regionBox=(1801,52,119,50),grayscaleFlag=True)
    pyautogui.click(x - 450,y)

    #Delete all the content currently in the Address bar
    selectAll()
    pyautogui.press("backspace")

    #Print Website URL into the Address bar and hit enter
    pyautogui.write(url)
    pyautogui.press("Enter")

def copyHTML(htmlIcon:str,scrollFlagInput:bool = False):
    #Open Inspect Element
    inspectElement()
    
    #Locate HTML tags in inspect Element and copy the HTML content to the clipboard
    x,y = findImageOnScreen(htmlIcon,timeoutDuration = 20,scrollFlag = scrollFlagInput, regionBox=(1370,140,181,30), grayscaleFlag=True,confidenceValue=0.90)
    pyautogui.rightClick(x,y)
    x,y = findImageOnScreen("copyOption.png",timeoutDuration = 5,regionBox = (450,90,1350,410),grayscaleFlag=True)
    pyautogui.moveTo(x,y)
    x,y = findImageOnScreen("copyOuterHtmlOptionButton.png",timeoutDuration = 5,regionBox = (450,90,1450,410),grayscaleFlag=True)
    pyautogui.click(x,y)

    #Close Inspect Element
    inspectElement()

def createLocalHTMLFile(htmlFileName:str,bodyFilter:bool = True):
    #We paste the HTML content currently in the clipboard and remove all the newline characters from it 
    htmlCode = pyperclip.paste().replace("\n","")
    htmlCode = htmlCode.replace("\r","")
    htmlCode = htmlCode.replace("\t","")

    #Here we use regex to remove everything but the content in the Body tags of the HTML, if bodyFilter is True.
    #Regex search returns a Regex Match object, and the group method just returns the string result of the regex search.
    if bodyFilter:
        htmlCode = re.search("<body.+body>",htmlCode).group()
        htmlCode = re.sub("<script.*?script>","",htmlCode)
        htmlCode = re.sub("<iframe.*?iframe>","",htmlCode)
        htmlCode = re.sub("<svg.*?svg>","",htmlCode)
        htmlCode = re.sub("<img.*?>","",htmlCode)
        
    #Here we create a file using utf8 encoding and put the refined HTML content inside, and save the file.
    file = open(htmlFileName,"w",encoding="utf-8")
    file.write(htmlCode)
    file.close()

def getAllOddLinks(htmlFileName:str,aLinkClassName:str):
    #This function is used when the odds for each matchup are displayed on their own individual HTML pages.
    time.sleep(1)

    #Here we paste the HTML content currently in the clipboard and make a file, similar to createLocalHTMLFile
    htmlCode = pyperclip.paste()
    if htmlCode == "undefined":
       return("undefined")

    file = open(htmlFileName.encode('utf8'),"w",encoding="utf-8")
    file.write(htmlCode)
    file.close()
    
    #Here we use Beautiful Soup, to parse through the HTML file, locate all the anchor tags, and store them in a list.
    try:
        page = open(htmlFileName,"rb")
    except FileNotFoundError:
        raise LocalHTMLFileNotPresent(htmlFileName)
    
    soup = BeautifulSoup(page.read(),'html.parser',from_encoding='utf-8')
    anchorTags = soup.find_all("a",class_=aLinkClassName)
    if anchorTags == []:
        raise NoAnchorTagsPresentInLocalHTMLFileError(htmlFileName)

    #Lastly we iterate through all the anchor tags and extract the href attribute, AKA the URL to the HTML page that displays the odds for each individual matchup.
    matchUrlList = []
    for match in anchorTags:
        matchUrlList.append(match['href'])

    return matchUrlList

def firstWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        matchUpLinks = "undefined"
        while matchUpLinks == "undefined":
            findImageOnScreen("websiteImages/firstWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,regionBox=(595,547,136,533)) #This website needs some extra time to load. This HTML icon indicates that all the HTML has been loaded and can be extracted.
            copyHTML("htmlIcon.png") 
            matchUpLinks = getAllOddLinks(os.getcwd()  + "/localHTMLFiles/firstWebsiteOrigin.html",aLinkClassName=os.getenv('FIRST_WEBSITE_LINK_ELEMENT_CLASS'))
        
        for index in range(len(matchUpLinks)):
            link = matchUpLinks[index]
            goToWebsite(os.getenv('FIRST_WEBSITE_URL_PREFACE')+link)
            time.sleep(1)
            allOddsOptionIconLocation=findImageOnScreen("websiteImages/allOddsOption.png",timeoutDuration=20,confidenceValue=0.90,regionBox=(600,811,1000,853))
            pyautogui.leftClick(allOddsOptionIconLocation)
            pyautogui.moveTo(200,200)
            findOneOfTheImagesOnScreen(["websiteImages/firstWebsiteOddsLoadedIcon.png","websiteImages/firstWebsiteOddsLoadedIcon2.png"],timeoutDuration=20,grayscaleFlag=True, confidenceValue=0.90,regionBox=(600,811,1000,853))
            copyHTML("htmlIcon.png")
            createLocalHTMLFile(os.getcwd()  + "/localHTMLFiles/firstWebsiteHTMLFiles/page" + str(index + 1) + ".html")
    
    #This is how I'm currently handling errors for website parsing

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=traceback.format_exc()) 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())
    

def secondWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        findImageOnScreen("websiteImages/secondWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.95,regionBox=(80,25,35,30))
        copyHTML("htmlIcon.png")
        matchUpLinks = getAllOddLinks(os.getcwd() + "/localHTMLFiles/secondWebsiteOrigin.html",aLinkClassName=os.getenv('SECOND_WEBSITE_LINK_ELEMENT_CLASS'))
        for index in range(len(matchUpLinks)):
            link = matchUpLinks[index]
            goToWebsite(link)
            try:
                matchWinnerIconLocation=findImageOnScreen("websiteImages/secondWebsiteOddsLoadedIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.99,regionBox=(556,606,693,624))
            except ImageNotFoundOnScreenError as inst:
                htmlFetchingErrorWebhook.send(content=traceback.format_exc())
                continue

            pyautogui.moveTo(matchWinnerIconLocation)
            copyHTML("htmlIcon.png")
            #The Match Winner Icon tends to shift downwards once the page fully loads, just in case it does, we'll find its location a second time so we can click on it.
            matchWinnerIconLocation=findImageOnScreen("websiteImages/secondWebsiteOddsLoadedIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.99,regionBox=(556,606,693,624)) 
            pyautogui.leftClick(matchWinnerIconLocation)
            createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/secondWebsiteHTMLFiles/page" + str(index + 1) + ".html")
            pyautogui.moveTo(500,0)


    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())


def thirdWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        findImageOnScreen("websiteImages/thirdWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True)
        copyHTML("htmlIcon.png",scrollFlagInput=True)
        createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html",bodyFilter=False) 

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=traceback.format_exc()) 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())

def fourthWebsiteHTMLCollector(link:str):
    htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
    try:
        goToWebsite(link)
        findImageOnScreen("websiteImages/fourthWebsiteLoadIcon.png", timeoutDuration = 20, grayscaleFlag=True, regionBox=(411,373,76,41))
        copyHTML("htmlIcon.png")
        createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html",bodyFilter=False) 
        time.sleep(1)

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=traceback.format_exc()) 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=traceback.format_exc())

#Custom Exceptions
class ImageNotFoundOnScreenError(Exception):
    def __init__(self,imageFile:str):
        self.imageFile = imageFile
        super().__init__("Pyautogui could not find " + self.imageFile + " on the screen.")


class LocalHTMLFileNotPresent(Exception):
    def __init__(self,localHTMLFile:str):
        self.localHTMLFile = localHTMLFile
        super().__init__("Beautiful Soup could not find the local HTML file: " + localHTMLFile )


class ImageFileNotFoundError(Exception):
    def __init__(self,imagePath:str,imageFile:str):
        self.imageFile = imageFile
        self.imagePath = imagePath
        super().__init__("Python could not find the PNG file " + self.imageFile + " at the path: " + self.imagePath)

class NoAnchorTagsPresentInLocalHTMLFileError(Exception):
    def __init__(self,localHTMLFile:str):
        self.localHTMLFile = localHTMLFile
        super().__init__("Beautiful Soup could not find any anchor tags present in the local HTML file: " + localHTMLFile + " check to see if the HTML File actually has HTML inside of it, if so, then the anchor tag class name for the Matchup links has probably changed")


def resetChrome():
    chromeSettingsIcon = findImageOnScreen("chromeSettingsIcon.png",timeoutDuration = 20,grayscaleFlag=True,regionBox=(1880,55,40,66))
    pyautogui.leftClick(chromeSettingsIcon)
    chromeSettingsText = findImageOnScreen("chromeSettingsText.png",timeoutDuration = 20,grayscaleFlag=True)
    pyautogui.leftClick(chromeSettingsText)
    resetAndCleanUpText = findImageOnScreen("resetAndCleanUpText.png",timeoutDuration = 20,grayscaleFlag=True)
    pyautogui.leftClick(resetAndCleanUpText)
    resetSettingsToDefault = findImageOnScreen("restoreSettingsToDefaultButton.png",timeoutDuration = 20,grayscaleFlag=True)
    pyautogui.leftClick(resetSettingsToDefault)
    resetButton = findImageOnScreen("resetSettingsButton.png",timeoutDuration = 20,grayscaleFlag=True)
    pyautogui.leftClick(resetButton)

    time.sleep(2)

    os.system("pkill chrome")
    time.sleep(2)

def openChrome():
    chromeIcon = findImageOnScreen("chromeIcon.png",timeoutDuration = 20,grayscaleFlag=True)
    pyautogui.leftClick(chromeIcon)

    chromeWindowsIcon = findImageOnScreen("chromeWindowIcon.png",timeoutDuration = 20,grayscaleFlag=True)
    while(chromeWindowsIcon == None):
        chromeWindowsIcon = findImageOnScreen("chromeWindowIcon.png",timeoutDuration = 20,grayscaleFlag=True)



def removeOldHTMLFiles():
    if os.path.exists("/localHTMLFiles/firstWebsiteOrigin.html"):
        os.remove("/localHTMLFiles/firstWebsiteOrigin.html")

    if os.path.exists("/localHTMLFiles/secondWebsiteOrigin.html"):
        os.remove("/localHTMLFiles/secondWebsiteOrigin.html")

    if os.path.exists("/localHTMLFiles/fourthWebsiteHTMLFiles/page.html"):
        os.remove("/localHTMLFiles/fourthWebsiteHTMLFiles/page.html")

    if os.path.exists("/localHTMLFiles/thirdWebsiteHTMLFiles/page.html"):
        os.remove("/localHTMLFiles/thirdWebsiteHTMLFiles/page.html")

    for x in range(1,len(os.listdir("./localHTMLFiles/firstWebsiteHTMLFiles"))):
        os.remove("./localHTMLFiles/firstWebsiteHTMLFiles/page" + str(x) + ".html")

    for x in range(1,len(os.listdir("./localHTMLFiles/secondWebsiteHTMLFiles"))):
        os.remove("./localHTMLFiles/secondWebsiteHTMLFiles/page" + str(x) + ".html")