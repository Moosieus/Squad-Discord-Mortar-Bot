# Squad-Discord-Mortar-Bot
This is a Discord Bot I made for Squad. It was created on Python 3.6.2, using these 3rd party packages:

fuzzywuzzy 0.15.1: https://pypi.python.org/pypi/fuzzywuzzy

discord.py: https://github.com/Rapptz/discord.py

The available commands are listed below. Mortar Bot uses fuzzywuzzy to parse the commands to allow for typographical errors or shorthands (I.e "mort" instead of "mortar" or "targ" instead of "target")

@[botname] - Initializes the bot

mortar [grid] - Sets a mortar location

target [grid] - Prints out the elevation and azimuth for every mortar to hit that target

adjust [distance] [bearing] - Adjusts the last target by said distance and direction

sleep - Wipes the session data and puts the bot to sleep

remove [grid] - Removes a mortar at the exact specified grid

