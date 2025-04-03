import requests, json, base64
from PIL import Image
from io import BytesIO
import PySimpleGUI as sg

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
    cardRequest += "&format=image&version=normal"
    card = requests.get(cardRequest)
    cardImage = None
    if card.status_code == 200:
        cardImage = Image.open(BytesIO(card.content))
        return cardImage
    return None

# Given a PIL image object, converts the object into a Base64 string readable by PySimple GUI
def convertImageForGUI (cardImageData):
    with BytesIO() as imageBuffer:
        cardImageData.save(imageBuffer, format='PNG')
        imageBuffer.seek(0)
        cardImageDataBase64 = base64.b64encode(imageBuffer.read())
        return cardImageDataBase64
