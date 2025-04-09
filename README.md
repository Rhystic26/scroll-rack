# Scroll Rack
A Magic: The Gathering deck-building application that suggests cheaper alternatives for cards.
- Find inexpensive versions of format staples! (Can't afford Fierce Guardianship? Unwind is a much cheaper option! Don't have the money for Demonic Tutor? Consider Diabolic Intent! Want to play Time Warp but light on cash? Karn's Temporal Sundering has you covered.)
- Find similar cards to those already in your decklist! (For example, if you're playing a white keywords matter deck and already have Baneslayer Angel, Scroll Rack will suggest Zetalpa, Primal Dawn, Akroma, Angel of Wrath, and Sire of Seven Deaths - all creatures around the same mana cost that have similar keywords and color identities. As another example, say you're playing an UB theft deck and have included Thief of Sanity - Scroll Rack would suggest Hostage Taker and Gonti, Lord of Luxury.) 
- Discover obscure MTG cards! (Seriously, this program spits out strange stuff sometimes.)
## Screenshots
<img src="/screenshots/fierce_guardianship_search.png?raw=true" width="40%" height="40%"> <img src="/screenshots/baneslayer_angel_search.png?raw=true" width="40%" height="40%">
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
## Application Design and Structure
I've been an avid fan of Magic: The Gathering since I was a kid (my first set was Khans of Tarkir) and 
### Program Flow
Stuff
### Card Analysis Algorithm
Stuff
### Limitations
Finish
### Takeaways
Stuff
## Planned Features
- Allow filtering results by format legality (ie. Standard, Commander, Modern, etc.)
- Description-only search option to catch effects that get printed on a wide variety of card types (ex. Craterhoof Behemoth/Triumph of the Hordes/Garruk's Uprising)
## License
Copyright (c) 2025 Jacob Casper  
This project is under the MIT License. More details can be found in the LICENSE file.
