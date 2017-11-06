import discord as dis
from SquadMortarCalc.mortar import mcal
from fuzzywuzzy import fuzz
from re import sub

# f'adjust {distance}, {bearing}'
async def adjust(self, last_message=None, last_state=None):
    breakdown = str(last_message.content).split(' ')
    dist = int(sub('\D','',breakdown[1]))
    bearing = breakdown[2].lower()
    try: # Try for integer bearing
        bearing = int(bearing)
    except: # Try for cardinal direction
        cardinal_directions = {
            "n": 0,
            "ne": 45,
            "e": 90,
            "se": 135,
            "s": 180,
            "sw": 225,
            "w": 270,
            "nw": 315
        }
        bearing = cardinal_directions[bearing]
    for calc in self.networks[last_message.channel]:
        self.networks[last_message.channel][calc].adjust_point(adjDist=dist,bearing=bearing)
    await print_adjusted_mission(self,last_message=last_message)

# f'remove {location}'
async def remove(self, last_message=None, last_state=None):
    breakdown = str(last_message.content).split(" ", 1)
    ref = breakdown[1]
    self.networks[last_message.channel].pop(ref)

#  f'mortar {location}'
async def mortar(self, last_message=None, last_state=None):
    breakdown = str(last_message.content).split(" ",1)
    ref = breakdown[1]

    self.networks[last_message.channel][ref] = mcal()
    self.networks[last_message.channel][ref].mortar = ref
    """ UNUSED
        @self.client.event
        async def on_message_edit(before,after):
            if str(before.author.id) != self.client.user.id and before.channel == last_message.channel:
                before_breakdown = str(before.content).split(" ", 1)
                before_ref = before_breakdown[1]
                self.networks[last_message.channel].pop(before_ref)
                print(str(after.content))
                await mortar(self,after)
    """

#  f'target {location}'
async def target(self, last_message=None, last_state=None):
    #  last_target = last_message
    breakdown = str(last_message.content).split(" ", 1)
    ref = breakdown[1]
    for calc in self.networks[last_message.channel]:
        self.networks[last_message.channel][calc].target = ref
#        print(self.networks[last_message.channel][calc].target)
    await print_mission(self,last_message=last_message)

#  prints mission from the last coordinates given
async def print_mission(self, last_message=None, last_state=None):
    output = ""
    for calc in self.networks[last_message.channel]:
        print(self.networks[last_message.channel][calc].mortar)
        print(self.networks[last_message.channel][calc].target)
        output += "**Mortar @ " + calc + ":\n**"
        output += self.networks[last_message.channel][calc].new_fire_mission()
        output += '\n\n'
    await self.client.send_message(last_message.channel, output)

#  prints mission + adjustments made to it.
async def print_adjusted_mission(self, last_message=None, last_state=None):
    output = ""
    for calc2 in self.networks[last_message.channel]:
        output += "**Mortar @ " + calc2 + ":\n**"
        output += self.networks[last_message.channel][calc2].current_fire_mission()
        output += '\n\n'
    await self.client.send_message(last_message.channel, output)

#  sleep state for bot.
async def sleep(self, last_message=None, last_state= None):
    try:
        await self.client.send_message(last_message.channel, "Going to sleep...")
    except AttributeError:
        print("No channel to message")
    if last_message is None or len(self.networks) == 1:
        self.networks = {}

        @self.client.event
        async def on_message(message: dis.Message) -> dis.Message:
            #  print(message.content)
            if str(message.content) == f"<@!{self.client.user.id}>" or str(message.content) == f"<@{self.client.user.id}>":
                self.networks[message.channel] = {}
                await self.client.send_message(message.channel, "Mortar Bot Initialized.")
                self.rout = self.routines["root"]
                await self.rout(self, last_message=message)
    elif last_message.channel in self.networks:
        self.networks.pop(last_message.channel)

#  root state of bot, loops back after each routine.
async def root(self, last_message=None, last_state=None):
    @self.client.event
    async def on_message(message):
        print(self.networks)
        if message.author.id != self.client.user.id:
            initialized = False
            for chan in self.networks.keys():
                if message.channel == chan:  # If the message is already in the network keys
                    initialized = True
                    command = str(message.content).split(' ')[0]
                    best_ratio = ("", 0)
                    for rout in self.routines:
                        ratio = fuzz.partial_ratio(command, rout)
                        if ratio > best_ratio[1]:
                            best_ratio = (rout,ratio)
                    if best_ratio[1] > 50:
                        print(f"{best_ratio[0]}, {best_ratio[1]}")
                        await self.routines[best_ratio[0]](self, last_message=message)
                    else:
                        await self.client.send_message(last_message.channel, "Failed to interpret command. (Match < 50)")
            if not initialized: # If the message is already in the network keys
                if str(message.content) == f"<@!{self.client.user.id}>" or str(message.content) == f"<@{self.client.user.id}>":
                    self.networks[message.channel] = {}
                    await self.client.send_message(message.channel, "Mortar Bot Initialized.")
                    self.rout = self.routines["root"]
                    await self.rout(self, last_message=message)


class MortarBot:
    client = dis.Client()  # type: dis.Client
    routines = {
                "sleep": sleep,
                "root": root,
                "mortar": mortar,
                "target": target,
                "remove": remove,
                "adjust": adjust
                }  # type : dict
    networks = {}  # type: dict

    #  Create & Execute the bot.
    def __init__(self):
        @self.client.event
        async def on_ready():
            print("Logged in as: " + self.client.user.name)
            print("Bot User ID: " + self.client.user.id)
            rout = self.routines["sleep"]
            await rout(self)

        self.client.run('your-bot-token-here')  # This command runs the bot.
