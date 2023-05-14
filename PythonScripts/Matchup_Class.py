from discord import SyncWebhook
import os
class Matchup:
    #Static Variable across the Matchup Class.
    #Here I store a dictionary containing every instance of Matchup and its corresponding Hash. (Hash is the Key, Object is the Value)

    #This is the object we use to send messages to the discord server
    arbitrageWebhook = SyncWebhook.from_url(os.getenv('ARBITRAGE_NOTIF'))
    

    def __hash__(self) -> int:
        return hash((self.teamOne,self.teamTwo))

    def __init__(self,sport:str,sportLeague:str,teamOne:str,teamTwo:str,allMatchups:dict) -> None:
        self.sport = sport
        self.sportLeague = sportLeague
        self.teamOne = teamOne
        self.teamTwo = teamTwo
        self.teamOneMoneyLineOdds = dict()
        self.teamTwoMoneyLineOdds = dict()
        self.teamOneHandicapLineOdds = dict()
        self.teamTwoHandicapLineOdds = dict()
        self.overTotalLineOdds = dict()
        self.underTotalLineOdds = dict()
        self.bettingSiteLinks = dict()
        self.highestMoneylineArbPercentage = 1.0
        self.highestHandicapLineArbPercentage = 1.0
        self.highestTotalLineArbPercentage = 1.0
        allMatchups[hash(self)] = self

    def addMoneyLineOdds(self,currentBettingSite:str,currentBettingSiteLink:str,firstTeamCurrentBettingSite:str,firstOdd:str,secondOdd:str) -> bool:
        if(firstTeamCurrentBettingSite == self.teamOne):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            self.teamOneMoneyLineOdds[currentBettingSite] = firstOdd
            self.teamTwoMoneyLineOdds[currentBettingSite] = secondOdd
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink
            return True
        elif(firstTeamCurrentBettingSite == self.teamTwo):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            self.teamOneMoneyLineOdds[currentBettingSite] = secondOdd
            self.teamTwoMoneyLineOdds[currentBettingSite] = firstOdd
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink
            return True
        else:
            return False
    
    def addHandicapLineOdds(self,currentBettingSite:str,currentBettingSiteLink:str,firstOdd:str,secondOdd:str,handicapOne:str,handicapTwo:str) -> bool:
        if(self.teamOne in handicapOne):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            if currentBettingSite not in self.teamOneHandicapLineOdds:
                self.teamOneHandicapLineOdds[currentBettingSite] = [(handicapOne,firstOdd)]
                self.teamTwoHandicapLineOdds[currentBettingSite] = [(handicapTwo,secondOdd)]
            else:
                self.teamOneHandicapLineOdds[currentBettingSite].append((handicapOne,firstOdd))
                self.teamTwoHandicapLineOdds[currentBettingSite].append((handicapTwo,secondOdd))
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink    
            return True
        elif(self.teamOne in handicapTwo):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            if currentBettingSite not in self.teamTwoHandicapLineOdds:
                self.teamOneHandicapLineOdds[currentBettingSite] = [(handicapTwo,secondOdd)]
                self.teamTwoHandicapLineOdds[currentBettingSite] = [(handicapOne,firstOdd)]
            else:
                self.teamOneHandicapLineOdds[currentBettingSite].append((handicapTwo,secondOdd))
                self.teamTwoHandicapLineOdds[currentBettingSite].append((handicapOne,firstOdd))
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink
            return True
        else:
            return False

    def addTotalLineOdds(self,currentBettingSite:str,currentBettingSiteLink:str,firstOdd:str,secondOdd:str,totalBoundaryOne:str,totalBoundaryTwo:str)-> bool:
        if("O" in totalBoundaryOne):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            if currentBettingSite not in self.overTotalLineOdds:
                self.overTotalLineOdds[currentBettingSite] = [(totalBoundaryOne,firstOdd)]
                self.underTotalLineOdds[currentBettingSite] = [(totalBoundaryTwo,secondOdd)]
            else:
                self.overTotalLineOdds[currentBettingSite].append((totalBoundaryOne,firstOdd))
                self.underTotalLineOdds[currentBettingSite].append((totalBoundaryTwo,secondOdd))
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink
            return True
        
        elif("U" in totalBoundaryOne):
            firstOdd,secondOdd = Matchup.convertOddsToDecimal(firstOdd,secondOdd)
            if currentBettingSite not in self.underTotalLineOdds:
                self.overTotalLineOdds[currentBettingSite] = [(totalBoundaryTwo,secondOdd)]
                self.underTotalLineOdds[currentBettingSite] = [(totalBoundaryOne,firstOdd)]
            else:
                self.overTotalLineOdds[currentBettingSite].append((totalBoundaryTwo,secondOdd))
                self.underTotalLineOdds[currentBettingSite].append((totalBoundaryOne,firstOdd))
            self.bettingSiteLinks[currentBettingSite] = currentBettingSiteLink
            return True
        else:
            return False

    def arbitrageCheck(self,dataframeInformation:dict) -> None:
        for firstBettingSiteKey,teamOneOddValue in self.teamOneMoneyLineOdds.items():
            for secondBettingSiteKey,teamTwoOddValue in self.teamTwoMoneyLineOdds.items():
                arbitragePercentage = abs((1 / float(teamOneOddValue)) + (1 / float(teamTwoOddValue)))
                dataframeInformation["Matchup Header"].append(self.teamOne + " @ " + self.teamTwo)
                dataframeInformation["Type of bet"].append("Moneyline")
                dataframeInformation["Team 1 Odd"].append(teamOneOddValue)
                dataframeInformation["Team 2 Odd"].append(teamTwoOddValue)
                dataframeInformation["Arb Percentage"].append(arbitragePercentage)


                if (arbitragePercentage < 1.0):
                    Matchup.arbitrageWebhook.send(content="MONEY LINE Arbitrage Opportunity found:\n" + 
                    firstBettingSiteKey + " : " + self.teamOne + " @ " +  teamOneOddValue + " " + self.bettingSiteLinks[firstBettingSiteKey] + "\n" +
                    secondBettingSiteKey + " : " + self.teamTwo + " @ " + teamTwoOddValue + " " + self.bettingSiteLinks[secondBettingSiteKey] + "\n" +
                    "Arbitrage Percentage: " + str(arbitragePercentage))
                    
                    if arbitragePercentage < self.highestMoneylineArbPercentage:
                        self.highestMoneylineArbPercentage = arbitragePercentage

    def handicapArbitrageCheck(self,dataframeInformation:dict) -> None:
        for firstBettingSiteKey,teamOneHandicapOddInfoList in self.teamOneHandicapLineOdds.items():
            for teamOneHandicapOddInfo in teamOneHandicapOddInfoList:
                for secondBettingSiteKey,teamTwoHandicapOddInfoList in self.teamTwoHandicapLineOdds.items():
                    for teamTwoHandicapOddInfo in teamTwoHandicapOddInfoList:
                        handicapOne,handicapOneOdd = teamOneHandicapOddInfo
                        handicapTwo,handicapTwoOdd = teamTwoHandicapOddInfo

                        extractedTeamOne, handicapOneValue= handicapOne.split("@")
                        extractedTeamTwo, handicapTwoValue= handicapTwo.split("@")
                        if handicapOneValue == "" or handicapTwoValue == "" or handicapOneValue[1:] != handicapTwoValue[1:] or handicapOneValue[0] == handicapTwoValue[0] or extractedTeamOne == extractedTeamTwo:
                            continue
                        arbitragePercentage = abs((1 / float(handicapOneOdd)) + (1 / float(handicapTwoOdd)))
                        dataframeInformation["Matchup Header"].append(self.teamOne + " @ " + self.teamTwo)
                        dataframeInformation["Type of bet"].append("Handicap")
                        dataframeInformation["Team 1 Odd"].append(handicapOneOdd)
                        dataframeInformation["Team 2 Odd"].append(handicapTwoOdd)
                        dataframeInformation["Arb Percentage"].append(arbitragePercentage)



                        if (arbitragePercentage < 1.0):
                            Matchup.arbitrageWebhook.send(content="HANDICAP LINE Arbitrage Opportunity found:\n" + 
                            firstBettingSiteKey + " : " + self.teamOne + " @ " +  handicapOneOdd + " " + self.bettingSiteLinks[firstBettingSiteKey] + "\n" +
                            secondBettingSiteKey + " : " + self.teamTwo + " @ " + handicapTwoOdd + " " + self.bettingSiteLinks[secondBettingSiteKey] + "\n" +
                            "Arbitrage Percentage: " + str(arbitragePercentage))
                            
                            if arbitragePercentage < self.highestHandicapLineArbPercentage:
                                self.highestHandicapLineArbPercentage = arbitragePercentage
                        
    def totalArbitrageCheck(self,dataframeInformation:dict) -> None:
        for firstBettingSiteKey,overTotalOddInfoList in self.overTotalLineOdds.items():
            for overTotalOddInfo in overTotalOddInfoList:
                for secondBettingSiteKey,underTotalOddInfoList in self.underTotalLineOdds.items():
                    for underTotalOddInfo in underTotalOddInfoList:
                        totalTitleOne, totalBoundaryOne,totalOddOne = overTotalOddInfo[0].split(" ") + [overTotalOddInfo[1]]
                        totalTitleTwo,totalBoundaryTwo,totalOddTwo = underTotalOddInfo[0].split(" ") + [underTotalOddInfo[1]]

                        if totalBoundaryOne != totalBoundaryTwo or totalTitleOne == totalTitleTwo:
                            continue
                        arbitragePercentage = abs((1 / float(totalOddOne)) + (1 / float(totalOddTwo)))
                        dataframeInformation["Matchup Header"].append(self.teamOne + " @ " + self.teamTwo)
                        dataframeInformation["Type of bet"].append("Total")
                        dataframeInformation["Team 1 Odd"].append(totalOddOne)
                        dataframeInformation["Team 2 Odd"].append(totalOddTwo)
                        dataframeInformation["Arb Percentage"].append(arbitragePercentage)
                        
                        if (arbitragePercentage < 1.0):
                            Matchup.arbitrageWebhook.send(content="TOTAL LINE Arbitrage Opportunity found:\n" + 
                            firstBettingSiteKey + " : " + self.teamOne + " @ " +  totalOddOne + " " + self.bettingSiteLinks[firstBettingSiteKey] + "\n" +
                            secondBettingSiteKey + " : " + self.teamTwo + " @ " + totalOddTwo + " " + self.bettingSiteLinks[secondBettingSiteKey] + "\n" +
                            "Arbitrage Percentage: " + str(arbitragePercentage))
                            
                            if arbitragePercentage < self.highestTotalLineArbPercentage:
                                self.highestTotalLineArbPercentage = arbitragePercentage            

                    

    #Static Methods
    def matchupExists(teamOne:str,teamTwo:str,allMatchups:dict):
        currentHash = hash((teamOne,teamTwo))
        if currentHash in allMatchups:
            return(allMatchups[currentHash])
        return None
    
    def convertOddsToDecimal(inputOddOne: str, inputOddTwo: str) -> list[str,str]:
        returnList = []

        if inputOddOne == '' and inputOddTwo == '':
            return [1.0,1.0]
        elif (inputOddOne[0] == "+") and ("." not in inputOddOne):
            convertedInputOddOne = str(1 + (int(inputOddOne) / 100))
            returnList.append(convertedInputOddOne)
        elif(inputOddOne[0] == "-") and ("." not in inputOddOne):
            convertedInputOddOne = str(1 - (100 / int(inputOddOne)))
            returnList.append(convertedInputOddOne)
        else:
            returnList.append(inputOddOne)

        
        if (inputOddTwo[0] == "+") and ("." not in inputOddTwo):
            convertedInputOddTwo = str(1 + (int(inputOddTwo) / 100))
            returnList.append(convertedInputOddTwo)
        elif(inputOddTwo[0] == "-") and ("." not in inputOddTwo):
            convertedInputOddTwo = str(1 - (100 / int(inputOddTwo)))
            returnList.append(convertedInputOddTwo)
        else:
            returnList.append(inputOddTwo)
            
        return returnList


