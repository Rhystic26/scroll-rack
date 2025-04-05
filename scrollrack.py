import requests, json, base64
from PIL import Image
from io import BytesIO
import FreeSimpleGUI as sg

# Given a card name, retrieves a card's data from scryfall in JSON format
def retrieveCardData(cardName):
    wordsInName = cardName.split()
    cardRequest = "https://api.scryfall.com/cards/named?fuzzy="
    for i in wordsInName:
        cardRequest += i + "+"
    card = requests.get(cardRequest)
    cardJson = card.json()
    if (cardJson['object'] == "error"):
        return None
    return cardJson

# Given a card name, retrieves an image of a card from Scryfall
def retrieveCardImage(cardName):
    wordsInName = cardName.split()
    cardRequest = "https://api.scryfall.com/cards/named?fuzzy="
    for i in wordsInName:
        cardRequest += i + "+"
    cardRequest += "&format=image&version=small"
    card = requests.get(cardRequest)
    cardImage = None
    if card.status_code == 200:
        cardImage = Image.open(BytesIO(card.content))
        return cardImage
    return None

# Given a Scryfall search string, retrieves a list of cards from Scryfall in JSON format and parses them into a dictionary
def retrieveCardList(listRequest):
    cardRequest = "https://api.scryfall.com/cards/search?q="
    cardList = requests.get(cardRequest+listRequest)
    cardListJson = cardList.json()
    if cardListJson['object'] == 'error':
        return None
    cardListData = cardListJson['data']
    cardListObjects = []
    for i in cardListData:
        cardListObjects.append(Card(i))
    return cardListObjects

# Given a Pillow image object, converts the object into a Base64 bytestring
def convertImageForGUI (cardImageData):
    with BytesIO() as imageBuffer:
        cardImageData.save(imageBuffer, format='PNG')
        imageBuffer.seek(0)
        cardImageDataBase64 = base64.b64encode(imageBuffer.read())
        return cardImageDataBase64

class CardFace:
    def __init__(self, inputDict):
        self.name = inputDict['name']
        #print(self.name)
        self.typeLine = inputDict['type_line']
        self.oracleText = []
        self.types = []
        self.colors = [] 
        if 'colors' in inputDict:
            self.colors = inputDict['colors']
        self.manaCost = inputDict['mana_cost']

        self.typeLine = self.typeLine.split(" ")
        for i in self.typeLine:
            if i == "—":
                break
            self.types.append(i)
        
        for b, a in enumerate(self.types):
            self.types[b] = a.lower()
        
        # Remove special characters from oracle text, split at newlines and periods
        self.tempOracleText = inputDict['oracle_text']
        self.tempOracleText = self.tempOracleText.replace("•", "")
        self.tempOracleText = self.tempOracleText.replace("(", "")
        self.tempOracleText = self.tempOracleText.replace(")", "")
        self.tempOracleText = self.tempOracleText.replace("—", "\n")
        self.tempOracleText = self.tempOracleText.replace(":", "\n")
        if "Saga" in self.typeLine:
            self.tempOracleText = self.tempOracleText.replace("III ", "")
            self.tempOracleText = self.tempOracleText.replace("II ", "")
            self.tempOracleText = self.tempOracleText.replace("I ", "")
        self.tempOracleText = self.tempOracleText.split('\n')
        for b, a in enumerate(self.tempOracleText):
            self.tempOracleText[b] = a.split(".")
            if (self.isCreature() or self.isVehicle()) and a.count(".") == 0:
                self.tempOracleText[b] = a.split(",")
        for i in self.tempOracleText:
            for g in i:
                self.oracleText.append(g)
        self.oracleText = [a for a in self.oracleText if a]

        tempName = self.name.split(",")
        for b, a in enumerate(self.oracleText):
            self.oracleText[b] = a.replace(self.name, "~")
        for b, a in enumerate(self.oracleText):
            self.oracleText[b] = a.replace(tempName[0], "~")
        
        for b, a in enumerate(self.oracleText):
            self.oracleText[b] = a.lower()
        
        for i in reversed(self.oracleText):
                if len(i) == 1:
                    self.oracleText.remove(i)
        
        for b, a in enumerate(self.oracleText):
            self.oracleText[b] = a.lstrip()

        # Maybe change this section to deal with card face formatting better?
        for i in reversed(self.oracleText):
            if i.startswith('trample') or i.startswith('menace') or i.startswith('lifelink') or i.startswith('flying') or i.startswith('first strike') or i.startswith('double strike') or i.startswith('deathtouch') or i.startswith('haste') or i.startswith('hexproof') or i.startswith('indestructible') or i.startswith('ward') or i.startswith('protection') or i.startswith('vigilance') or i.startswith('reach'):
                self.oracleText.remove(i)

        if (self.isCreature() or self.isVehicle()):
            self.power = inputDict['power']
            self.toughness = inputDict['toughness']

    # Checks if a given card face is a creature
    def isCreature(self):
        for i in self.types:
            if i == 'creature':
                return True
        return False
    
    def isVehicle(self):
        if "vehicle" in self.typeLine:
            return True
        return False

class Card:
    def __init__(self, jsonData):
        self.name = jsonData['name']
        self.prices = jsonData['prices']
        self.priceUSD = self.prices['usd']
        self.cmc = jsonData['cmc']
        self.cmc = int(self.cmc)
        self.cmc = str(self.cmc)
        self.keywords = jsonData['keywords']
        self.layout = jsonData['layout']
        self.typeLine = jsonData['type_line']
        self.types = []
        self.colors = []
        self.cardFaces = None

        for b, a in enumerate(self.keywords):
            self.keywords[b] = a.lower()

        if self.layout == 'normal' or self.layout == 'prototype' or self.layout == 'mutate' or self.layout == 'meld' or self.layout == 'case' or self.layout == 'class':
            self.oracleText = []
            self.typeLine = self.typeLine.split(" ")
            for i in self.typeLine:
                if i == "—":
                    break
                self.types.append(i)
            
            for b, a in enumerate(self.types):
                self.types[b] = a.lower()

            self.colors = jsonData['colors']
            
            # Remove special characters from oracle text, split at newlines and periods
            self.tempOracleText = jsonData['oracle_text']
            self.tempOracleText = self.tempOracleText.replace("•", "")
            self.tempOracleText = self.tempOracleText.replace("(", "")
            self.tempOracleText = self.tempOracleText.replace(")", "")
            self.tempOracleText = self.tempOracleText.replace("—", "\n")
            self.tempOracleText = self.tempOracleText.replace(":", "\n")
            self.tempOracleText = self.tempOracleText.split('\n')
            for b, a in enumerate(self.tempOracleText):
                self.tempOracleText[b] = a.split(".")
                if (self.isCreature() or self.isVehicle()) and a.count(".") == 0:
                    self.tempOracleText[b] = a.split(",")
            for i in self.tempOracleText:
                for g in i:
                    self.oracleText.append(g)
            self.oracleText = [a for a in self.oracleText if a]

            tempName = self.name.split(",")
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.replace(self.name, "~")
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.replace(tempName[0], "~")

            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.lower()
            
            for i in reversed(self.oracleText):
                if len(i) == 1:
                    self.oracleText.remove(i)
            
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.lstrip()

            for i in reversed(self.oracleText):
                if i.startswith('trample') or i.startswith('lifelink') or i.startswith('menace') or i.startswith('flying') or i.startswith('first strike') or i.startswith('double strike') or i.startswith('deathtouch') or i.startswith('haste') or i.startswith('hexproof') or i.startswith('indestructible') or i.startswith('ward') or i.startswith('protection') or i.startswith('vigilance') or i.startswith('reach'):
                    self.oracleText.remove(i)

            if (self.isCreature() or self.isVehicle()):
                self.power = jsonData['power']
                self.toughness = jsonData['toughness']
            #print(self.oracleText)

        elif self.layout == 'saga':
            self.oracleText = []
            self.typeLine = self.typeLine.split(" ")
            for i in self.typeLine:
                if i == "—":
                    break
                self.types.append(i)
           
            for b, a in enumerate(self.types):
                self.types[b] = a.lower()
          
            self.colors = jsonData['colors']
            
            # Remove special characters from oracle text, split at newlines and periods
            self.tempOracleText = jsonData['oracle_text']
            self.tempOracleText = self.tempOracleText.replace("•", "")
            self.tempOracleText = self.tempOracleText.replace("(", "")
            self.tempOracleText = self.tempOracleText.replace(")", "")
            self.tempOracleText = self.tempOracleText.replace("—", "\n")
            self.tempOracleText = self.tempOracleText.replace(":", "\n")
            self.tempOracleText = self.tempOracleText.replace("III ", "")
            self.tempOracleText = self.tempOracleText.replace("II ", "")
            self.tempOracleText = self.tempOracleText.replace("I ", "")
            self.tempOracleText = self.tempOracleText.split('\n')
            for b, a in enumerate(self.tempOracleText):
                self.tempOracleText[b] = a.split(".")
            for i in self.tempOracleText:
                for g in i:
                    self.oracleText.append(g)
            #print(self.oracleText)
            self.oracleText = [a for a in self.oracleText if a]
            
            tempName = self.name.split(",")
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.replace(self.name, "~")
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.replace(tempName[0], "~")
            
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.lower()

            for i in reversed(self.oracleText):
                if len(i) == 1:
                    self.oracleText.remove(i)
            
            for b, a in enumerate(self.oracleText):
                self.oracleText[b] = a.lstrip()

            for i in reversed(self.oracleText):
                if i.startswith('trample') or i.startswith('lifelink') or i.startswith('menace') or i.startswith('flying') or i.startswith('first strike') or i.startswith('double strike') or i.startswith('deathtouch') or i.startswith('haste') or i.startswith('hexproof') or i.startswith('indestructible') or i.startswith('ward') or i.startswith('protection') or i.startswith('vigilance') or i.startswith('reach'):
                    self.oracleText.remove(i)

            if (self.isCreature() or self.isVehicle()):
                self.power = jsonData['power']
                self.toughness = jsonData['toughness']

        elif self.layout == 'flip' or self.layout == 'transform' or self.layout == 'adventure' or self.layout == 'split' or self.layout == 'modal_dfc':
            self.cardFaces = []
            for i in jsonData['card_faces']:
                self.cardFaces.append(CardFace(i))     

    # Checks if a given card is a creature
    def isCreature(self):
        for i in self.types:
            if i == 'creature':
                return True
        return False
    
    def isVehicle(self):
        if "vehicle" in self.typeLine:
            return True
        return False

# Given a card object, craft a Scryfall search query to find similar cards
def analyzeCard (inputCard, mode):
    searchString = "game%3Apaper"

    if inputCard.layout == 'flip' or inputCard.layout == 'transform' or inputCard.layout == 'adventure' or inputCard.layout == 'split' or inputCard.layout == 'modal_dfc':
        pass

    else:
        searchString += "+%28"
        for i in inputCard.oracleText:
            x = i.replace(" ", "+")
            searchString += ('+fulloracle%3A"' + x + '"+OR')
        searchString += "+%29"

        searchString += "+%28"
        if inputCard.isCreature() and 'enchantment' in inputCard.types:
            searchString += ("+t%3Acreature+OR" + "+t%3Aenchantment")
        else:
            for i in inputCard.types:
                if i == 'legendary':
                    continue
                searchString += ("+t%3A" + i + "+OR")
        searchString += "+%29"

        if (inputCard.isCreature() or inputCard.isVehicle()):
            if mode < 2:
                searchString += "+%28"
                searchString += ("+pow>%3D" + inputCard.power)
                searchString += ("+tou>%3D" + inputCard.toughness)
                searchString += "+%29"
        
        if mode < 4:
            colorString = ""
            for i in inputCard.colors:
                colorString += i
            searchString += "+%28"
            searchString += ("+c<%3D" + colorString)
            searchString += "+%29"
        
        if mode < 3:
            searchString += "+%28"
            searchString += ("+mv%3D" + inputCard.cmc)
            searchString += "+%29"
    if mode < 4:
        searchString += "+%28"
        if ('trample' in inputCard.keywords) or ('menace' in inputCard.keywords) or ('flying' in inputCard.keywords):
            searchString += ("+%28" + "+kw%3Atrample+OR" + "+kw%3Amenace+OR" + "+kw%3Aflying" + "+%29")
        if ('first strike' in inputCard.keywords) or ('double strike' in inputCard.keywords) or ('deathtouch' in inputCard.keywords):
            searchString += ("+%28" + "+kw%3Afirststrike+OR" + "+kw%3Adoublestrike+OR" + "+kw%3Adeathtouch" + "+%29")
        if ('haste' in inputCard.keywords):
            searchString += ("+%28" + "+kw%3Ahaste" + "+%29")
        if ('hexproof' in inputCard.keywords) or ('indestructible' in inputCard.keywords) or ('ward' in inputCard.keywords) or ('protection' in inputCard.keywords):
            searchString += ("+%28" + "+kw%3Ahexproof+OR" + "+kw%3Aindestructible+OR" + "+kw%3Award+OR" + "+kw%3Aprotection" + "+%29")
        if ('vigilance' in inputCard.keywords) or ('reach' in inputCard.keywords) or ('lifelink' in inputCard.keywords):
            searchString += ("+%28" + "+kw%3Avigilance+OR" + "+kw%3Areach+OR" + "+kw%3Alifelink" + "+%29")
        for i in inputCard.keywords:
            if i != 'trample' and i != 'menace' and i != 'flying' and i != 'first strike' and i != 'double strike' and i != 'deathtouch' and i != 'haste' and i != 'hexproof' and i != 'indestructible' and i != 'ward' and i != 'protection' and i != 'vigilance' and i != 'reach' and i != 'lifelink':
                searchString += ("+kw%3A" + i)
        searchString += "+%29"

    searchString += "&order=usd&dir=asc"
    return searchString

# ********************Main Program********************

# Global variables
searchedCardImage = None
searchedCardPNG = None
searchedCardData = None
searchedCard = None
analysisString = None
suggestedCardList = None
cardDisplayList = []

# UI setup
col1 = [[sg.vtop(sg.Text("Search for a card here:"))], 
                 [sg.vtop(sg.Input(key='cardInput'))], 
                 sg.vtop([sg.Button('Search for Card'), sg.Button('Run Scroll Rack')])]
col2 = [[sg.Text(key='cardName')], [sg.Text(key='cardPrice')], [sg.Image(key='displayInputCard', filename='magic_card_back.png')]]
col3a = [[sg.Text(key='suggestedCard1Name')], [sg.Text(key='suggestedCard1Price')], [sg.Image(key='displaySuggestedCard1', filename='magic_card_back.png')]]
col3b = [[sg.Text(key='suggestedCard2Name')], [sg.Text(key='suggestedCard2Price')], [sg.Image(key='displaySuggestedCard2', filename='magic_card_back.png')]]
col3c = [[sg.Text(key='suggestedCard3Name')], [sg.Text(key='suggestedCard3Price')], [sg.Image(key='displaySuggestedCard3', filename='magic_card_back.png')]]

programLayout = [[sg.Column(col1), sg.Column(col2)], 
                 [sg.Text(text='Suggested Alternatives:')], 
                 [sg.Column(col3a), sg.Column(col3b), sg.Column(col3c)]]

# Initialize window
programWindow = sg.Window('Scroll Rack', programLayout)

# main loop
while True:

    # Read user input
    event, values = programWindow.read()

    # Check if user quits program
    if event == sg.WINDOW_CLOSED: 
        break

    if event == 'Search for Card':
        programWindow['displayInputCard'].update(filename='magic_card_back.png')
        programWindow['cardName'].update("")
        programWindow['cardPrice'].update("")
        programWindow['suggestedCard1Name'].update("")
        programWindow['suggestedCard1Price'].update("")
        programWindow['displaySuggestedCard1'].update(filename='magic_card_back.png')
        programWindow['suggestedCard2Name'].update("")
        programWindow['suggestedCard2Price'].update("")
        programWindow['displaySuggestedCard2'].update(filename='magic_card_back.png')
        programWindow['suggestedCard3Name'].update("")
        programWindow['suggestedCard3Price'].update("")
        programWindow['displaySuggestedCard3'].update(filename='magic_card_back.png')

        searchedCardImage = retrieveCardImage(values['cardInput'])
        if searchedCardImage == None:
            programWindow['cardName'].update("Card not found")
            continue
        searchedCardPNG = convertImageForGUI(searchedCardImage)
        searchedCardData = retrieveCardData(values['cardInput'])
        searchedCard = Card(searchedCardData)
        programWindow['displayInputCard'].update(data=searchedCardPNG)
        programWindow['cardName'].update(searchedCard.name)
        if searchedCard.priceUSD != None:
            programWindow['cardPrice'].update("Price: $" + searchedCard.priceUSD + " USD")
        
    elif event == 'Run Scroll Rack':
        suggestedCardList = None
        cardDisplayList = []

        # Reset card name elements
        programWindow['suggestedCard1Name'].update("Card not found")
        programWindow['suggestedCard2Name'].update("Card not found")
        programWindow['suggestedCard3Name'].update("Card not found")

        # If no card has been searched, exit function
        if searchedCardImage == None:
            programWindow['cardName'].update("No card selected!")
            continue

        # Run card analysis
        for i in range (1, 5):
            analysisString = analyzeCard(searchedCard, i)
            suggestedCardList = retrieveCardList(analysisString)
            if suggestedCardList == None:
                continue
            else:
                for i in reversed(suggestedCardList):
                    if i.name == searchedCard.name:
                        suggestedCardList.remove(i)
                    for b in cardDisplayList:
                        if i.name == b.name:
                            suggestedCardList.remove(i)
                x = 0
                while len(cardDisplayList) < 3:
                    if 0 <= x < len(suggestedCardList):
                        cardDisplayList.append(suggestedCardList[x])
                        x += 1
                    else:
                        break
            if len(cardDisplayList) == 3:
                break
        
        # Display final suggested cards on screen
        print(analysisString)
        if 0 < len(cardDisplayList):
            programWindow['suggestedCard1Name'].update(cardDisplayList[0].name)
            if cardDisplayList[0].priceUSD != None:
                programWindow['suggestedCard1Price'].update("Price: $" + cardDisplayList[0].priceUSD + " USD")
            programWindow['displaySuggestedCard1'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[0].name)))

        if 1 < len(cardDisplayList):
            programWindow['suggestedCard2Name'].update(cardDisplayList[1].name)
            if cardDisplayList[1].priceUSD != None:
                programWindow['suggestedCard2Price'].update("Price: $" + cardDisplayList[1].priceUSD + " USD")
            programWindow['displaySuggestedCard2'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[1].name)))

        if 2 < len(cardDisplayList):
            programWindow['suggestedCard3Name'].update(cardDisplayList[2].name)
            if cardDisplayList[2].priceUSD != None:
                programWindow['suggestedCard3Price'].update("Price: $" + cardDisplayList[2].priceUSD + " USD")
            programWindow['displaySuggestedCard3'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[2].name)))

                

programWindow.close()