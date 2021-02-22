# tarkov-randomizer
Randomized Tarkov loadouts that auto update

-----

This application uses Python, NodeJS and MongoDB to periodically retrieve updated information from the official [Escape From Tarkov Wiki](https://escapefromtarkov.gamepedia.com/Escape_from_Tarkov_Wiki).

It parses the data from the wikipages for various items (Weapons, Maps, Headgear, Armor, Rigs, Backpacks) and saves them locally in a MongoDB database.  There is a web frontend that is served via NodeJS's `express` library.  

