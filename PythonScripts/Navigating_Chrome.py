import pyautogui
import time
import pyperclip
import re
import os
from discord import SyncWebhook
from bs4 import BeautifulSoup
import subprocess
from threading import Thread

def openFirefox(link):
    subprocess.call([os.getcwd() + "/bashScript/openUpBrowser.sh", link])

def findImageOnScreen(image:str, timeoutDuration:int, scrollFlag:bool = False, confidenceValue:float = 0.9, grayscaleFlag:bool = False, regionBox:tuple = (0,0,1920,1080),returnNothing = False):
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
            pyautogui.click(1911,202,button='left',clicks=20)
            time.sleep(1)
    if returnNothing:
        return None

    else:
        raise ImageNotFoundOnScreenError(image)

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
    x,y = findImageOnScreen("bookMarkIcons.png",timeoutDuration = 5, regionBox=(960,0,960,540),grayscaleFlag=True)
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
    x,y = findImageOnScreen(htmlIcon,timeoutDuration = 20,scrollFlag = scrollFlagInput, grayscaleFlag=True, regionBox=(1425,195,170,65), confidenceValue=0.90)
    pyautogui.rightClick(x,y)
    x,y = findImageOnScreen("copyOption.png",timeoutDuration = 5, regionBox=(1475,330,1590,85), grayscaleFlag=True)
    pyautogui.moveTo(x,y)
    x,y = findImageOnScreen("copyOuterHtmlOptionButton.png",timeoutDuration = 5, regionBox=(1710,360,165,90),grayscaleFlag=True)
    pyautogui.moveTo(x,y)
    time.sleep(0.25)
    pyautogui.click(x,y)

    #Close Inspect Element
    inspectElement()

def copyFireFoxHTML(htmlIcon:str,webhook,scrollFlagInput:bool = False):
    #Open Inspect Element
    
    inspectElement()
    time.sleep(3)
    #Locate HTML tags in inspect Element and copy the HTML content to the clipboard
    
    x,y = findImageOnScreen(htmlIcon,timeoutDuration = 20,scrollFlag = scrollFlagInput, grayscaleFlag=True, regionBox=(70,880,65,40), confidenceValue=0.90)
    pyautogui.rightClick(x,y)
    x,y = findImageOnScreen("copyOptionFirefox.png",timeoutDuration = 5, regionBox=(95,790,130,40), grayscaleFlag=True)
    pyautogui.moveTo(x,y)
    x,y = findImageOnScreen("copyOuterHtmlOptionButtonFirefox.png",timeoutDuration = 5, regionBox=(350,815,160,40),grayscaleFlag=True)
    pyautogui.moveTo(x,y)
    time.sleep(1)
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

def firstWebsiteGetAllOddLinks(htmlFileName:str,divContainerClassName:str,aLinkClassName:str,wrongDivContainerClassName:str = "INCORRECT",incorrectPageFlag:str = "NONE"):
    #This function is used when the odds for each matchup are displayed on their own individual HTML pages.
    time.sleep(2)

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
        raise LocalHTMLFileNotPresent(htmlFileName, "First Website")
    
    soup = BeautifulSoup(page.read(),'html.parser',from_encoding='utf-8')
    divContainers = soup.select('div.'+divContainerClassName+':not(.'+ wrongDivContainerClassName +')')
    anchorTags = []
    for container in divContainers:
        link = container.find("a",class_=aLinkClassName)
        if link is not None:
            anchorTags.append(link)

    incorrectPageElements = soup.find_all("div",class_=incorrectPageFlag)
    if anchorTags == []:
        raise NoAnchorTagsPresentInLocalHTMLFileError(htmlFileName)
    elif incorrectPageElements != []:
        return []

    #Lastly we iterate through all the anchor tags and extract the href attribute, AKA the URL to the HTML page that displays the odds for each individual matchup.
    matchUrlList = []
    for match in anchorTags:
        matchUrlList.append(match['href'])

    return matchUrlList

def secondWebsiteGetAllOddLinks(htmlFileName:str,divContainerClassName:str,invalidDivContainerClassName:str, aLinkClassName:str, retry=False):
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
        raise LocalHTMLFileNotPresent(htmlFileName, "Second Website")
    
    soup = BeautifulSoup(page.read(),'html.parser',from_encoding='utf-8')
    div_containers = soup.find_all("div", class_=divContainerClassName, recursive=True)
    div_containers_with_valid_odds = []
    for event in div_containers:
        skipFlag = event.find("div",class_=invalidDivContainerClassName)
        if ((event.find("div", class_="odds")) and (skipFlag is None)):
            div_containers_with_valid_odds.append(event)

    anchorTags = []
    for container in div_containers_with_valid_odds:
        link = container.find("a",class_=aLinkClassName)
        if link is not None:
            anchorTags.append(link)

    if anchorTags == []:
        if retry:
            raise NoAnchorTagsPresentInLocalHTMLFileError(htmlFileName)
        else:
            return "Retry"


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
            findImageOnScreen("websiteImages/firstWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,regionBox=(615,505,100,575)) #This website needs some extra time to load. This HTML icon indicates that all the HTML has been loaded and can be extracted.
            copyHTML("htmlIcon.png") 
            matchUpLinks = firstWebsiteGetAllOddLinks(os.getcwd()  + "/localHTMLFiles/firstWebsiteOrigin.html",aLinkClassName=os.getenv('FIRST_WEBSITE_LINK_ELEMENT_CLASS'),incorrectPageFlag='text-2x1',divContainerClassName=os.getenv('FIRST_WEBSITE_DIV_ELEMENT_CLASS'),wrongDivContainerClassName=os.getenv("FIRST_WEBSITE_WRONG_DIV_ELEMENT_CLASS"))
        
        for index in range(len(matchUpLinks)):
            link = matchUpLinks[index]
            goToWebsite(os.getenv('FIRST_WEBSITE_URL_PREFACE')+link)
            time.sleep(1)
            counter = 0
            noOddsLoadedFlag = None
            while counter < 30 and noOddsLoadedFlag is None:
                allOddsOptionIconLocation=findImageOnScreen("websiteImages/allOddsOption.png",timeoutDuration=1,grayscaleFlag=True, confidenceValue=0.90, returnNothing=True)
                if allOddsOptionIconLocation is None:
                    continue
                pyautogui.leftClick(allOddsOptionIconLocation)
                pyautogui.moveTo(allOddsOptionIconLocation.x + 70,allOddsOptionIconLocation.y)
                noOddsLoadedFlag = findImageOnScreen("websiteImages/firstWebsiteOddsLoadedIcon.png",timeoutDuration=1,grayscaleFlag=True, confidenceValue=0.85, returnNothing=True)
                counter +=1
            if counter >= 30:
                raise FirstWebsiteNoOddsLoadedError()
            copyHTML("htmlIcon.png")
            createLocalHTMLFile(os.getcwd()  + "/localHTMLFiles/firstWebsiteHTMLFiles/page" + str(index + 1) + ".html")
    
    #This is how I'm currently handling errors for website parsing

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================") 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=inst)
        if inst.imageFile == "websiteImages/firstWebsiteLoadIcon.png":
            htmlFetchingErrorWebhook.send("It also might be possible that the link for this website's event is invalid so double check the environment file.\n\n==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except FirstWebsiteNoOddsLoadedError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    

def secondWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        if link =="a":
            return
        goToWebsite(link)
        locationFlag = findImageOnScreen("websiteImages/secondWebsiteOkayButton.png",timeoutDuration = 12,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True,regionBox=(745,555,505,135))
        if locationFlag is not None:
            pyautogui.leftClick(locationFlag)
            locationPopup = findImageOnScreen("websiteImages/secondWebsitePopup.png",timeoutDuration = 15,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True)
            if locationPopup is not None:
                pyautogui.leftClick(locationPopup.x+100,locationPopup.y+35)
        
        findImageOnScreen("websiteImages/secondWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.95,regionBox=(1400,345,170,85))
        
        skipFlag = findImageOnScreen("websiteImages/secondWebsiteSkipElement.png",timeoutDuration = 3,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True)
        if skipFlag is not None:
            raise InvalidWebsiteLinkError(os.getenv('SECOND_WEBSITE'),link)
        copyHTML("htmlIcon.png")

        matchUpLinks = secondWebsiteGetAllOddLinks(htmlFileName = os.getcwd() + "/localHTMLFiles/secondWebsiteOrigin.html",divContainerClassName=os.getenv('SECOND_WEBSITE_DIV_ELEMENT_CLASS'),invalidDivContainerClassName=os.getenv("SECOND_WEBSITE_INVALID_DIV_ELEMENT_CLASS"),aLinkClassName=os.getenv('SECOND_WEBSITE_LINK_ELEMENT_CLASS'))
        if matchUpLinks == "Retry":
            matchUpLinks = secondWebsiteGetAllOddLinks(htmlFileName = os.getcwd() + "/localHTMLFiles/secondWebsiteOrigin.html",divContainerClassName=os.getenv('SECOND_WEBSITE_DIV_ELEMENT_CLASS'),invalidDivContainerClassName=os.getenv("SECOND_WEBSITE_INVALID_DIV_ELEMENT_CLASS"),aLinkClassName=os.getenv('SECOND_WEBSITE_LINK_ELEMENT_CLASS'),retry=True)
        for index in range(len(matchUpLinks)):
            link = matchUpLinks[index]
            goToWebsite(link)
            try: #I have an inner try and catch loop here because if we can't find the oddsLoadedIcon on just one of the pages, I don't want the program to skip all the other pages because the icon might be there. If I just had one try and catch in the collector function, then I would skip all the odds pages as soon as I can't find the icon.
                matchWinnerIconLocation=findImageOnScreen("websiteImages/secondWebsiteOddsLoadedIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.99)
            except ImageNotFoundOnScreenError as inst:
                htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
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
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except InvalidWebsiteLinkError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")


def thirdWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        findImageOnScreen("websiteImages/thirdWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True)
        copyHTML("htmlIcon.png",scrollFlagInput=True)
        createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html",bodyFilter=False) 

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================") 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=inst)
        if inst.imageFile == "websiteImages/thirdWebsiteLoadIcon.png":
            htmlFetchingErrorWebhook.send("It also might be possible that the link for this website's event is invalid so double check the environment file.\n\n==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")

def fourthWebsiteHTMLCollector(link:str):
    htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
    try:
        p = Thread(target=openFirefox,args=(link,))
        p.start()
        findImageOnScreen("websiteImages/fourthWebsiteLoadIcon.png", timeoutDuration = 20, confidenceValue=0.90, grayscaleFlag=True)
        copyFireFoxHTML("firefoxHtmlIcon.png",htmlFetchingErrorWebhook)
        createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/fourthWebsiteHTMLFiles/page.html",bodyFilter=False) 
        time.sleep(1)
        closeFirefox()
        p.join()
    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
        if inst.imageFile == "websiteImages/fourthWebsiteLoadIcon.png":
            htmlFetchingErrorWebhook.send("It also might be possible that the link for this website's event is invalid so double check the environment file.\n\n==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")

def firstSimpleWebsiteHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        matchUpLinks = "undefined"
        while matchUpLinks == "undefined":
            findImageOnScreen("websiteImages/firstWebsiteSimpleLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,regionBox=(615,505,100,575)) #This website needs some extra time to load. This HTML icon indicates that all the HTML has been loaded and can be extracted.
            copyHTML("htmlIcon.png")
            createLocalHTMLFile(os.getcwd()  + "/localHTMLFiles/firstWebsiteOrigin.html") 

    
    #This is how I'm currently handling errors for website parsing

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================") 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=inst)
        if inst.imageFile == "websiteImages/firstWebsiteLoadIcon.png":
            htmlFetchingErrorWebhook.send("It also might be possible that the link for this website's event is invalid so double check the environment file.\n\n==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except FirstWebsiteNoOddsLoadedError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")

def secondWebsiteSimpleHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        if link =="a":
            return
        goToWebsite(link)
        locationFlag = findImageOnScreen("websiteImages/secondWebsiteOkayButton.png",timeoutDuration = 12,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True,regionBox=(745,555,505,135))
        if locationFlag is not None:
            pyautogui.leftClick(locationFlag)
            locationPopup = findImageOnScreen("websiteImages/secondWebsitePopup.png",timeoutDuration = 15,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True)
            if locationPopup is not None:
                pyautogui.leftClick(locationPopup.x+100,locationPopup.y+35)
        
        findImageOnScreen("websiteImages/secondWebsiteLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True,confidenceValue=0.95,regionBox=(1400,345,170,85))
        
        skipFlag = findImageOnScreen("websiteImages/secondWebsiteSkipElement.png",timeoutDuration = 3,grayscaleFlag=True,confidenceValue=0.95,returnNothing=True)
        if skipFlag is not None:
            raise InvalidWebsiteLinkError(os.getenv('SECOND_WEBSITE'),link)
        copyHTML("htmlIcon.png")
        createLocalHTMLFile(os.getcwd()  + "/localHTMLFiles/secondWebsiteOrigin.html") 


    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except InvalidWebsiteLinkError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")


def thirdWebsiteSimpleHTMLCollector(link:str):
    try:
        htmlFetchingErrorWebhook = SyncWebhook.from_url(os.getenv('HTML_FETCHING_ERROR_NOTIF'))
        goToWebsite(link)
        findImageOnScreen("websiteImages/thirdWebsiteSimpleLoadIcon.png",timeoutDuration = 20,grayscaleFlag=True)
        copyHTML("htmlIcon.png",scrollFlagInput=True)
        createLocalHTMLFile(os.getcwd() + "/localHTMLFiles/thirdWebsiteHTMLFiles/page.html",bodyFilter=False) 

    except LocalHTMLFileNotPresent as inst: #Inst refers to the actual instance of the error/exception
        #Here I'm sending the text of the exception to our Discord Server through our webhook
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")
    except ImageFileNotFoundError as inst: 
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================") 
    except ImageNotFoundOnScreenError as inst:
        htmlFetchingErrorWebhook.send(content=inst)
        if inst.imageFile == "websiteImages/thirdWebsiteSimpleLoadIcon.png":
            htmlFetchingErrorWebhook.send("It also might be possible that the link for this website's event is invalid so double check the environment file.\n\n==========================================================================")
    except NoAnchorTagsPresentInLocalHTMLFileError as inst:
        htmlFetchingErrorWebhook.send(content=str(inst)+"==========================================================================")

#Custom Exceptions
class ImageNotFoundOnScreenError(Exception):
    def __init__(self,imageFile:str):
        self.imageFile = imageFile
        super().__init__("\n**ImageNotFoundOnScreenError:**\n\nPyautogui could not find " + self.imageFile + " on the screen.\n\n")


class LocalHTMLFileNotPresent(Exception):
    def __init__(self,localHTMLFile:str,website:str):
        self.localHTMLFile = localHTMLFile
        self.website = website
        super().__init__("\n**LocalHTMLFileNotPresent:**\n\nBeautiful Soup could not find the local HTML file: " + self.localHTMLFile + ". This is for website: " + self.website + "\n\n")


class ImageFileNotFoundError(Exception):
    def __init__(self,imagePath:str,imageFile:str):
        self.imageFile = imageFile
        self.imagePath = imagePath
        super().__init__("\n**ImageFileNotFoundError:**\n\nPython could not find the PNG file " + self.imageFile + " at the path: " + self.imagePath + "\n\n")

class NoAnchorTagsPresentInLocalHTMLFileError(Exception):
    def __init__(self,localHTMLFile:str):
        self.localHTMLFile = localHTMLFile
        super().__init__("\n**NoAnchorTagsPresentInLocalHTMLFileError:**\n\nBeautiful Soup could not find any anchor tags present in the local HTML file: " + self.localHTMLFile + " check to see if the HTML File actually has HTML inside of it, if so, then the anchor tag class name for the Matchup links has probably changed.\n\n")

class FirstWebsiteNoOddsLoadedError(Exception):
    def __init__(self):
        super().__init__("\n**FirstWebsiteNoOddsLoadedError:**\n\nPyautogui could not find the icons on the screen that signal the program that the odds have been loaded. \nThis is for the First Website.\n\n")

class InvalidWebsiteLinkError(Exception):
    def __init__(self,website:str, link:str):
        self.website = website
        self.link = link
        super().__init__("\n**InvalidWebsiteLinkError:**\n\nThe current link " + self.link + " for the website: " + self.website + ", is invalid. Update the environment file.\n\n")

def resetChrome():
    chromeSettingsIcon = findImageOnScreen("chromeSettingsIcon.png",timeoutDuration = 20,grayscaleFlag=True)
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
    chromeIcon = findImageOnScreen("chromeIcon.png",timeoutDuration = 20, regionBox=(0,50,80,400),grayscaleFlag=True)
    pyautogui.leftClick(chromeIcon)

    chromeWindowsIcon = findImageOnScreen("chromeWindowIcon.png",timeoutDuration = 20,grayscaleFlag=True)
    while(chromeWindowsIcon == None):
        chromeWindowsIcon = findImageOnScreen("chromeWindowIcon.png",timeoutDuration = 20,grayscaleFlag=True)

def closeFirefox():
    fireFoxIcons = "Something"
    while fireFoxIcons is not None:
        fireFoxIcons = findImageOnScreen("firefoxCloseButtonIcons.png",timeoutDuration=2,grayscaleFlag=True,returnNothing=True)
        if fireFoxIcons is not None:
            pyautogui.leftClick(fireFoxIcons.x + 68,fireFoxIcons.y - 20)
    print('complete')
    
def removeOldHTMLFiles():
    if os.path.exists("localHTMLFiles/firstWebsiteOrigin.html"):
        os.remove("localHTMLFiles/firstWebsiteOrigin.html")

    if os.path.exists("localHTMLFiles/secondWebsiteOrigin.html"):
        os.remove("localHTMLFiles/secondWebsiteOrigin.html")

    if os.path.exists("localHTMLFiles/fourthWebsiteHTMLFiles/page.html"):
        os.remove("localHTMLFiles/fourthWebsiteHTMLFiles/page.html")

    if os.path.exists("localHTMLFiles/thirdWebsiteHTMLFiles/page.html"):
        os.remove("localHTMLFiles/thirdWebsiteHTMLFiles/page.html")

    for x in range(1,len(os.listdir("localHTMLFiles/firstWebsiteHTMLFiles"))):
        if os.path.exists("localHTMLFiles/firstWebsiteHTMLFiles/page" + str(x) + ".html"):
            os.remove("localHTMLFiles/firstWebsiteHTMLFiles/page" + str(x) + ".html")

    for x in range(1,len(os.listdir("localHTMLFiles/secondWebsiteHTMLFiles"))):
        if os.path.exists("localHTMLFiles/secondWebsiteHTMLFiles/page" + str(x) + ".html"):
            os.remove("localHTMLFiles/secondWebsiteHTMLFiles/page" + str(x) + ".html")


def teamViewerClosePopup():
    teamViewerFlag = findImageOnScreen("teamViewerPopup.png",timeoutDuration=15,grayscaleFlag=True,returnNothing=True)
    if teamViewerFlag is not None:
        okayButton = findImageOnScreen("teamViewerOkayButton.png",timeoutDuration=5,grayscaleFlag=True)
        pyautogui.leftClick(okayButton)

