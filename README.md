# Scroll Rack
A Magic: The Gathering deck-building application that suggests cheaper alternatives for cards.
- Find inexpensive versions of format staples! (Can't afford Fierce Guardianship? Unwind is a much cheaper option! Don't have the money for Demonic Tutor? Consider Diabolic Intent! Want to play Time Warp but light on cash? Karn's Temporal Sundering has you covered.)
- Find similar cards to those already in your decklist! (For example, if you're playing a white keywords matter deck and already have Baneslayer Angel, Scroll Rack will suggest Zetalpa, Primal Dawn, Akroma, Angel of Wrath, and Sire of Seven Deaths - all creatures around the same mana cost that have similar keywords and color identities. As another example, say you're playing an UB theft deck and have included Thief of Sanity - Scroll Rack would suggest Hostage Taker and Gonti, Lord of Luxury.) 
- Discover obscure MTG cards! (Seriously, this program spits out strange stuff sometimes.)
## Screenshots
<img src="/screenshots/fierce_guardianship_search.png?raw=true" width="45%" height="45%"> <img src="/screenshots/baneslayer_angel_search.png?raw=true" width="45%" height="45%">
## Requirements (only if building from source)
- Python 3.13 or later
- Pip
## Installation
If you're using a Windows computer, you can download one of the standalone executables from the Releases tab of the repository. If not, follow these instructions to compile the application from its source code.
1. Open a terminal on your machine
2. `git clone` the repository
3. `cd scroll-rack`
4. `pip install requests`
5. `pip install pillow`
6. `pip install FreeSimpleGUI`
7. `python scrollrack.py`
## Usage
1. Type in the name of a card and click 'Search for Card'. Spelling doesn't have to be exact! (ex. 'aust com' finds 'Austere Command') If a matching card exists, Scroll Rack will display it in the top-right corner of the application window.
2. Click 'Run Scroll Rack.' Scroll Rack will run its algorithm and find alternate cards for you!
## Application Design
I've been an avid fan of Magic: The Gathering since I was a kid (my first set was Khans of Tarkir) and I started playing regularly with the release of Strixhaven in 2020. My favorite part of Magic are the intricate and bizzare mechanical interactions you can build decks around, and I love combing through Scryfall to find infrequently-played cards with niche uses. I wrote Scroll Rack both to make my own search process easier and as a useful tool for my combo deck-loving friends.

Scroll Rack works by retrieving an input card from Scryfall, storing it as a custom object, analyzing it for certain properties, and crafting an custom search request that it sends to the Scryfall API to retrieve alternatives. It stores card face images in memory temporarily instead of on disk, which makes the application lightweight. Card ingestion and analysis works as follows:

1. Card Ingestion: all cards are stored in a custom data structure that extracts critical information about the card (name, price, mana cost, oracle text, etc.) from its Scryfall JSON file. JSON data is extracted according to the card's 'layout' property: single-faced cards use the basic data structure, while multi-faced cards utilize two or more CardFace objects to separate each face's characteristics.  

    1a. Description Parsing: The core functionality of a card is almost always found in its Oracle Text, so Scroll Rack performs a number of text parsing functions on card descriptions to get better search results. The program removes special characters (•, (, ), —, and :) commonly used in Oracle Text, splits descriptions on newlines and periods, and replaces instances of a card's name with ~ (which Scryfall interprets as a placeholder for any card name). It also removes instances of evergreen keywords (ie. Trample, Lifelink, etc.) from a card's Oracle Text to prevent redundant search conditions (since Scroll Rack stores a card's keywords in a separate variable). These functions break down Oracle Text into smaller sections that are common to many cards, drastically improving search results when combined with other conditions.

2. Card Analysis: After ingesting an input card, Scroll Rack runs an analysis algorithm that outputs a custom Scryfall API search string based on certain qualities of the input card. The algorithm can be run in 4 different modes (1 to 4), with mode 1 having the strictest search conditions and mode 4 having the least strict conditions. The mode-based system exists in the event that Scroll Rack cannot find any cards on its first search (which is always mode 1): in this case, the program will adjust the mode of the algorithm and run until it finds a total of 3 alternate cards across all algorithm modes. Cards are anaylzed using the following properties:
   - Oracle Text: alternative cards must have at least one component of the input card's parsed Oracle Text.
   - Types: alternative cards must have at least one type (not subtype) of the input card's types (ex. Enchantment OR creature).
   - Power/Toughness: In stricter modes, alternative cards for an input creature or vehicle must have Power and Toughness greater or equal to the input card's Power and Toughness.
   - Colors: In stricter modes, alternative cards must have at most all of the colors present in the input card.
   - Mana Cost: In stricter modes, alternative cards must have a mana cost equal to the input card's mana cost.
   - Keywords: In stricter modes, alternative cards must have all of the keywords present on the input card. The exceptions to this rule are (most of) the evergreen keywords: Scroll Rack categorizes the evergreen keywords into types based on their purpose and accepts keywords with similar functionality to those present on the input card as a valid substitute. For example, Hexproof is considered a valid alternative to Indestructible, and First Strike is considered a valid alternative to Double Strike.

3. Card Search and Display: As Scroll Rack runs its analysis algorithm, results are ingested and stored until the program has found 3 valid alternative cards. Those cards are then displayed on the bottom half of the application window, sorted by similarity and then price (ie. a more similar card A will appear before a less similar card B that is cheaper than card A).
### Limitations
While the program works very well for most cards, sometimes it returns really weird results! Cards with extremely strange Oracle Text or mechanics either return completely nonsensical results or no results at all, and the less-similar results for cards are often off-color. I see these as fun quirks of the application: I've discovered some really cool cards as a result of these errors. However, I plan to keep adjusting the card analysis parameters to return more consistent results.
## Planned Features
- Allow filtering results by format legality (ie. Standard, Commander, Modern, etc.)
- Description-only search option to catch effects that get printed on a wide variety of card types (ex. Craterhoof Behemoth/Triumph of the Hordes/Garruk's Uprising)
## License
Copyright (c) 2025 Jacob Casper  
This project is under the MIT License. More details can be found in the LICENSE file.
