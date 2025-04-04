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

# Given a PIL image object, converts the object into a Base64 bytestring
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
        self.colors = jsonData['colors']
        self.keywords = jsonData['keywords']
        self.oracleText = jsonData['oracle_text']
        self.typeLine = jsonData['type_line']
        self.typeLine.split(" ")
        self.superTypes = []
        for i in self.typeLine:
            if i == "—":
                break
            self.superTypes.append(i)        

class Creature (Card):
    def __init__(self, jsonData):
        super().__init__(jsonData)
        self.power = jsonData['power']
        self.toughness = jsonData['toughness']

# Given JSON data for a card, creates a card object using the correct class (creature or non-creature)
def createCard(cardJson):
    typeLine = cardJson['type_line']
    typeLine.split(" ")
    for i in typeLine:
        if i == "creature":
            card = Creature(cardJson)
            return card
    card = Card(cardJson)
    return card

# Given a card object, craft a Scryfall search query to find similar cards
def analyzeCard (inputCard):
    pass

#evergreen keywords
#evasion: trample, menace, flying
#damage: first strike, double strike, deathtouch
#haste: haste
#defensive: hexproof, indestructible, ward
#combat defensive: vigilance, reach

#main loop
programLayout = [[sg.Text("Search for a card here:"), sg.Text(key='cardName')], 
                 [sg.vtop(sg.Input(key='cardInput')), sg.Image(key='displayInputCard', size=(146,204))], 
                 [sg.Text(key='cardNotFound')], 
                 sg.vtop([sg.Button('Search for Card'), sg.Button('Quit')])]

programWindow = sg.Window('Scroll Rack', programLayout)

while True:
    event, values = programWindow.read()

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    if event == 'Search for Card':
        programWindow['cardNotFound'].update("")
        programWindow['displayInputCard'].update()
        programWindow['cardName'].update("")
        print(programWindow['displayInputCard'].Size)
        searchedCardImage = retrieveCardImage(values['cardInput'])
        if searchedCardImage == None:
            programWindow['cardNotFound'].update("Card not found")
            continue
        searchedCardPNG = convertImageForGUI(searchedCardImage)
        searchedCardData = retrieveCardData(values['cardInput'])
        searchedCard = createCard(searchedCardData)
        programWindow['displayInputCard'].update(data=searchedCardPNG)
        programWindow['cardName'].update(searchedCard.name)

programWindow.close()