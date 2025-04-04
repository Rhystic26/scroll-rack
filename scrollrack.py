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

        if self.layout == 'normal':
            self.typeLine.split(" ")
            for i in self.typeLine:
                if i == "—":
                    break
                self.superTypes.append(i)
            self.colors = jsonData['colors']
            self.oracleText = jsonData['oracle_text']
            if self.isCreature():
                self.power = jsonData['power']
                self.toughness = jsonData['toughness']
            return
        
        elif self.layout == 'prototype' or self.layout == 'mutate':
            pass

        elif self.layout == 'meld':
            pass

        elif self.layout == 'case' or self.layout == 'saga':
            pass

        elif self.layout == 'adventure' or self.layout == 'split' or self.layout == 'modal_dfc':
            pass

        elif self.layout == 'flip' or self.layout == 'transform':
            pass

        elif self.layout == 'class' or self.layout == 'leveler':
            pass

        # self.typeLine = [i for i in self.typeLine if i != "—"]       

    # Checks if a given card is a creature
    def isCreature(self):
        for i in self.superTypes:
            if i == 'creature':
                return True
        return False

# Given a card object, craft a Scryfall search query to find similar cards
def analyzeCard (inputCard, mode):
    searchString = ""
    for i in inputCard.superTypes:
        searchString += ("+t%3A" + i)
    if inputCard.isCreature() and mode <= 1:
        searchString += ("+pow>%3D" + inputCard.power + "+tou>%3D" + inputCard.toughness)
    
    return searchString
    

#evergreen keywords
#evasion: trample, menace, flying
#damage: first strike, double strike, deathtouch
#haste: haste
#defensive: hexproof, indestructible, ward
#combat defensive: vigilance, reach

# ********************Main Program********************

# cd = retrieveCardList("%28oracle%3A%22When+~+enters%2C+look+at+the+top+four+cards+of+target+opponent%E2%80%99s+library%2C+exile+one+of+them+face+down%2C+then+put+the+rest+on+the+bottom+of+that+library+in+a+random+order.%22+OR+oracle%3A%22You+may+cast+that+card+for+as+long+as+it+remains+exiled%2C+and+mana+of+any+type+can+be+spent+to+cast+that+spell.%22%29")

'''t1 = retrieveCardData("baleful eidolon")
t1Card = createCard(t1)
t1Str = analyzeCard(t1Card, 1)
cd1 = retrieveCardList(t1Str)
for i in cd1:
    print(i.name)
'''
# Program variables
searchedCardImage = None
searchedCardPNG = None
searchedCardData = None
searchedCard = None

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

    elif event == 'Run Scroll Rack':
        if searchedCardImage == None:
            programWindow['cardName'].update("No card selected!")
            continue

programWindow.close()