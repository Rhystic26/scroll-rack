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

class Card:
    def __init__(self, jsonData):
        self.name = jsonData['name']
        self.prices = jsonData['prices']
        self.priceUSD = self.prices['usd']
        self.cmc = jsonData['cmc']
        self.keywords = jsonData['keywords']
        self.layout = jsonData['layout']
        self.typeLine = jsonData['type_line']
        self.superTypes = []
        self.colors = []

        if self.layout == 'normal' or self.layout == 'prototype' or self.layout == 'mutate' or self.layout == 'meld':
            self.oracleText = []
            self.typeLine = self.typeLine.split(" ")
            for i in self.typeLine:
                if i == "—":
                    break
                self.superTypes.append(i)

            self.colors = jsonData['colors']
            
            # Remove special characters from oracle text, split at newlines and periods
            self.tempOracleText = jsonData['oracle_text']
            self.tempOracleText = self.tempOracleText.replace("•", "")
            self.tempOracleText = self.tempOracleText.replace("—", "\n")
            self.tempOracleText = self.tempOracleText.split('\n')
            for b, a in enumerate(self.tempOracleText):
                self.tempOracleText[b] = a.split(".")
                if self.isCreature() and a.count(".") == 0:
                    self.tempOracleText[b] = a.split(",")
            for i in self.tempOracleText:
                for g in i:
                    self.oracleText.append(g)
            self.oracleText = [a for a in self.oracleText if a]

            if self.isCreature():
                self.power = jsonData['power']
                self.toughness = jsonData['toughness']
            

        elif self.layout == 'saga':
            self.oracleText = []
            self.typeLine = self.typeLine.split(" ")
            for i in self.typeLine:
                if i == "—":
                    break
                self.superTypes.append(i)

            self.colors = jsonData['colors']
            
            # Remove special characters from oracle text, split at newlines and periods
            self.tempOracleText = jsonData['oracle_text']
            self.tempOracleText = self.tempOracleText.replace("•", "")
            self.tempOracleText = self.tempOracleText.replace("—", "\n")
            self.tempOracleText = self.tempOracleText.replace("III ", "")
            self.tempOracleText = self.tempOracleText.replace("II ", "")
            self.tempOracleText = self.tempOracleText.replace("I ", "")
            self.tempOracleText = self.tempOracleText.split('\n')
            for b, a in enumerate(self.tempOracleText):
                self.tempOracleText[b] = a.split(".")
            for i in self.tempOracleText:
                for g in i:
                    self.oracleText.append(g)
            print(self.oracleText)
            self.oracleText = [a for a in self.oracleText if a]

            if self.isCreature():
                self.power = jsonData['power']
                self.toughness = jsonData['toughness']

        elif self.layout == 'adventure' or self.layout == 'split' or self.layout == 'modal_dfc':
            self.cardFaces = []


        elif self.layout == 'flip' or self.layout == 'transform':
            self.cardFaces = []
            pass

        elif self.layout == 'class':
            self.oracleText = []
            pass

        elif self.layout == 'case':
            self.oracleText = []
            pass     

    # Checks if a given card is a creature
    def isCreature(self):
        for i in self.superTypes:
            if i == 'Creature':
                return True
        return False

# Given a card object, craft a Scryfall search query to find similar cards
def analyzeCard (inputCard, mode):
    searchString = ""
    '''for i in inputCard.superTypes:
        searchString += ("+t%3A" + i)
    if inputCard.isCreature() and mode <= 1:
        searchString += ("+pow>%3D" + inputCard.power + "+tou>%3D" + inputCard.toughness)'''
    
    return searchString
    

#evergreen keywords
#evasion: trample, menace, flying
#damage: first strike, double strike, deathtouch
#haste: haste
#defensive: hexproof, indestructible, ward
#combat defensive: vigilance, reach

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
        programWindow['cardPrice'].update("Price: $" + searchedCard.priceUSD + " USD")
        print(searchedCard.oracleText)

    elif event == 'Run Scroll Rack':

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
                x = 0
                while len(cardDisplayList) < 3:
                    if 0 <= x < len(suggestedCardList):
                        cardDisplayList.append(suggestedCardList[x])
                    else:
                        break
            if len(cardDisplayList) == 3:
                break
        
        # Display final suggested cards on screen
        if 0 < len(cardDisplayList):
            programWindow['suggestedCard1Name'].update(cardDisplayList[0].name)
            programWindow['suggestedCard1Price'].update(cardDisplayList[0].priceUSD)
            programWindow['displaySuggestedCard1'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[0].name)))

        if 1 < len(cardDisplayList):
            programWindow['suggestedCard2Name'].update(cardDisplayList[1].name)
            programWindow['suggestedCard2Price'].update(cardDisplayList[1].priceUSD)
            programWindow['displaySuggestedCard2'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[1].name)))

        if 2 < len(cardDisplayList):
            programWindow['suggestedCard3Name'].update(cardDisplayList[2].name)
            programWindow['suggestedCard3Price'].update(cardDisplayList[2].priceUSD)
            programWindow['displaySuggestedCard3'].update(convertImageForGUI(retrieveCardImage(cardDisplayList[2].name)))

                

programWindow.close()