import requests, json
from PIL import Image
from io import BytesIO

# Given a HTTPS request string, retrieves a card's data from scryfall in JSON format
def retrieveCardData(cardRequest):
    card = requests.get(cardRequest)
    cardJson = card.json()
    if (cardJson['object'] == "error"):
        return None
    return cardJson

def retrieveCardImage(cardRequest):
    card = requests.get(cardRequest)
    cardImage = None
    if card.status_code == 200:
        cardImage = Image.open(BytesIO(card.content))
        return cardImage
    return None