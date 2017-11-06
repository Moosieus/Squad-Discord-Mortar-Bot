import math as m
import re
import random as rand

''' VARIABLES / GRID MANAGEMENT '''

class OutOfRange(Exception):
    pass

# Major Horizontal Grids
HorGrids = ('A', 'B', 'C',
            'D', 'E', 'F',
            'G', 'H', 'I',
            'J', 'K', 'L',
            'M', 'N', 'O',
            'P', 'Q', 'R',
            'S', 'T', 'U')
# Major Vertical Grids
VerGrids = ('1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21')
# The keypad Multipliers are solid. They don't need to be changed
KeyPad = {'1': (0, 2), '2': (1, 2), '3': (2, 2),
          '4': (0, 1), '5': (1, 1), '6': (2, 1),
          '7': (0, 0), '8': (1, 0), '9': (2, 0)}
# Distance Increments used for linearization
DistRange = [(50, 100), (100, 150), (150, 200),
             (200, 250), (250, 300), (300, 350),
             (350, 400), (400, 450),
             (450, 500), (500, 550), (550, 600),
             (600, 650), (650, 700), (700, 750),
             (750, 800), (800, 850), (850, 900),
             (900, 950), (950, 1000), (1000, 1050),
             (1050, 1100), (1100, 1150), (1150, 1200),
             (1200, 1250)]
# Distance Increments used for linearization
MillInc = [(1579, 1558), (1558, 1538), (1538, 1517),
           (1517, 1496), (1496, 1475), (1475, 1453),
           (1453, 1431), (1431, 1409),(1409, 1387),
           (1387, 1364), (1364, 1341),(1341, 1317),
           (1317, 1292), (1292, 1267),(1267, 1240),
           (1240, 1212), (1212, 1183),(1183, 1152),
           (1152, 1118), (1118, 1081), (1081, 1039),
           (1039, 988), (988, 918), (918, 800)]

''' HELPER METHODS '''

stepOf = lambda x: 300 / (m.pow(3, x))


# Given the GridList, convert to meters from 0,0
def getPos(GridList):
    while len(GridList) > 5:
        GridList.pop(len(GridList) - 1)
    Position = [0.0, 0.0]
    step = 0
    Position[0] += HorGrids.index(GridList.pop(0)) * stepOf(step)
    Position[1] += VerGrids.index(GridList.pop(0)) * stepOf(step) # We just need to pass two digits into this line
    while len(GridList) > 0:
        KeyValue = GridList.pop(0)
        step += 1
        for Dir in range(0, 2):
            Position[Dir] += KeyPad[KeyValue][Dir] * stepOf(step)
    # Assume middle of last grid
    Position[0] += stepOf(step) / 2
    Position[1] += stepOf(step) / 2
    return Position


# Returns the absolute distance between two points.
def getAbsDist(pA, pB):
        dx = pA[0] - pB[0]
        dy = pA[1] - pB[1]
        return m.sqrt(m.pow(m.fabs(dx), 2) + m.pow(m.fabs(dy), 2))


# Returns the range in which to do the linear approximation
def getDistRange(dist):
    try:
        if (dist > 1250.0):
            raise OutOfRange
        elif (dist < 50):
            raise OutOfRange
        else:
            for range in DistRange:
                if (range[0] <= dist and range[1] >= dist):
                    return DistRange.index(range)
    except OutOfRange:
        raise OutOfRange


# Converts distance in meters to milliradians
def getMilRads(dist):
        x = getDistRange(dist)
        try:
            extraDist = dist - DistRange[x][0]
            slope = (MillInc[x][0] - MillInc[x][1]) / 50  # delta Radians / delta Meters(50m)
            # Milliradians to the closest distance + extra distance * slope
            return MillInc[x][0] - slope * extraDist
        except:
            raise OutOfRange


# Returns the Azimuth for which the mcal to fire
def getAzimuth(pB, pA):
    Azimuth = 0.0
    dx = pB[0] - pA[0]
    dy = pB[1] - pA[1]
    dist = getAbsDist(pA, pB)
    if dx >= 0.0 and dy < 0.0:  # (+,-)
        Azimuth += 0
        Azimuth += m.degrees(m.asin(m.fabs(dx) / dist))
    elif dx > 0.0 and dy >= 0.0:  # (+,+)
        Azimuth += 90
        Azimuth += m.degrees(m.asin(m.fabs(dy) / dist))
    elif dx <= 0.0 and dy > 0.0:  # (-,+)
        Azimuth += 180
        Azimuth += m.degrees(m.asin(m.fabs(dx) / dist))
    elif dx < 0.0 and dy <= 0.0:  # (-,-)
        Azimuth += 270
        Azimuth += m.degrees(m.asin(m.fabs(dy) / dist))
    return Azimuth


# Returns a list of the characters
def parse(InputString):
    Input = InputString.upper()
    final = []
    input_list = re.split(r'[\W]', Input)
    if len(input_list) == 1: # If bunched together
        return list(input_list[0])

    #  Filter out non-word characters.
    for string in input_list:
        if re.compile(r'[\w]').match(string):
            final.append(string)

    #  Handle the first object
    if len(final[0]) == 3 or len(final[0]) == 2:
        a = final.pop(0)
        final.insert(0, a[1:])
        final.insert(0, a[0])

    #  If user forgot to split a keypad.
    for c in final[2:]:
        if len(c) > 1:
            i = final[2:].index(c) + 2
            c = final.pop(i)
            l = list(c).__reversed__()
            for x in l:
                final.insert(i, x)
    print(final)
    return final



"""
def parse(InputString):
    InputString = InputString.upper()
    split = re.split(r'[\W]', InputString, 1)  # ['F10','9','4','3','1']
    first = split[0][0]
    second = split[0][1:]
    rest = re.sub(r'[\W]', '', split[1])
    ret = [first,second]
    for c in rest:
        ret.append(c)
#    InputString = re.sub(r'[\W]', '',
#                         InputString)  # Removes all nonword characters, leaving only letters and numbers
    return ret
"""

def getSass(pB, pA):
    dist = getAbsDist(pA, pB)
    tooClose = [
        "You might as well start throwing grenades.",
        "I Hope you have some grenades left.",
        "Get off the mortar.",
        "You know they're practically next to you, right?",
        "You're practically trying to drop the shells on yourself...",
    ]
    tooFar = [
        "Too bad you don't have proper artillery...",
        "Have they added air-strikes yet?",
        "If only you were a *bit* closer.",
        "Sucks to be you."
        "Unlock the extended mortar range powerup, only $3.50"
    ]
    if dist < 50:
        return "Target is too close. " + tooClose[rand.randint(0, len(tooClose) - 1)]
    else:
        return "Target is too far away. " + tooFar[rand.randint(0, len(tooFar) - 1)]

''' CLASS STRUCTURE '''

class mcal():

    def __init__(self):
        self.mortar = ""
        self.target = ""
        self.mortarPos = [0.0, 0.0]
        self.targetPos= [0.0, 0.0]

    # Given a target point, distance, and bearing, modify pA
    def adjust_point(self, adjDist=None, bearing=None):
        print("Debug!")
        if bearing == 0:
            self.targetPos[1] -= adjDist
        elif bearing < 90:  # First Quadrant
            bearing -= 0
            self.targetPos[0] += adjDist * m.sin(m.radians(bearing))
            self.targetPos[1] -= adjDist * m.cos(m.radians(bearing))

        elif bearing == 90:
            self.targetPos[0] += adjDist
        elif bearing < 180:  # Second Quadrant
            bearing -= 90
            self.targetPos[0] += adjDist * m.cos(m.radians(bearing))
            self.targetPos[1] += adjDist * m.sin(m.radians(bearing))

        elif bearing == 180:
            self.targetPos[1] += adjDist
        elif bearing < 270:  # Third Quadrant
            bearing -= 180
            self.targetPos[0] -= adjDist * m.sin(m.radians(bearing))
            self.targetPos[1] += adjDist * m.cos(m.radians(bearing))

        elif bearing == 270:
            self.targetPos[0] -= adjDist
        elif bearing < 360:  # Fourth Quadrant
            bearing -= 270
            self.targetPos[0] -= adjDist * m.cos(m.radians(bearing))
            self.targetPos[1] -= adjDist * m.sin(m.radians(bearing))

        elif bearing == 360:
            self.targetPos[1] -= adjDist
    
    def new_fire_mission(self):
        try:
            self.mortarPos = getPos(parse(self.mortar))
            self.targetPos = getPos(parse(self.target))
            return(
                f"""Azimuth: {round(getAzimuth(self.targetPos,self.mortarPos), 1)}
 Elevation: {round(getMilRads(getAbsDist(self.mortarPos,self.targetPos)), 1)}"""
            )
        except:
            return getSass(self.mortarPos, self.targetPos)

    def current_fire_mission(self):
        try:
            return (
            f"""Azimuth: {round(getAzimuth(self.targetPos,self.mortarPos), 1)}
 Elevation: {round(getMilRads(getAbsDist(self.mortarPos,self.targetPos)), 1)}"""
            )
        except :
            return getSass(self.mortarPos, self.targetPos)