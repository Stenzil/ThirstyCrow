#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* Team Id: 100
* Author List:Praveen Pandey, Abhishek Goel
* Filename: lund.py
* Theme: Thirsty Crow
* Functions: av,stepcount,move,movethebot,stepcount1,compass,getdirections,savepositions,
            finalmove,run1,extract,clearBuffer,bhago,bhagna,mad,rvrt
* Global Variables: ser,premove,predir,pebble,water,allmoves,start,arena_config,crowid,dests, Robot_start
                    cdi,dii




Understanding the code: 
    
    **AIM:- To perform the complete robot traversal as per the given configuration by E-yantra. **
    
For moving the robot through out the graph, first of all the robot should be told about the graph and
he should be aware of his location (like where he is and in what direction he is facing). So first we need
a map (graph) in the code which can be understood by the robot. 

We've created a virtual graph using the grid matrix (The variable m (line46)). If you think again, 
this matrix is nothing but a representation of data points in a X-Y cordinate. Every node is a data
that is represented as 1 in the 2-D matrix and other points are zero with all nodes at a distance of
one unit from each other. Distane is kept uniform in all the directions . Now the robot knows how many 
nodes are there in the graph and where they are. 

NOW WE KNOW THAT AT SOME LOCATION WE HAVE A NODE. BUT IF WE SEE , WE'VE NOTHING TO DO WITH THE NODES.
ACTUALLY WE'VE TO DEAL WITH THE HEXAGONS. THESE HEXAGONS HAVE SOME FIXED IDs. SO IF WE WISH TO GO TO A
HEXAGON WITH SOME ID , OUR ROBOT DOESN'T KNOWS WHERE IT WILL BE. WHAT SHOULD WE DO ?

SOLUTION :- for this problem we created one more variable named dests(line no:- 62). Dest contains the 
location of all the axes for each hexagon. In anycase we'll have to go to any of the axes only. 
we can't say that we need to go to cell ( hexagon) no -6 , we'll say that cell no. 6 and axes- "2-2".
So basically we should know the location of each axes of all the hexagons/cells.
Dests basically contains the required data and here we end up solving our problem 

NOW OUR ROBOT KNOWS LOCATION OF ALL THE AXES OF EACH HEXAGON. SO NOW THE ROBOT KNOWS ITS OWN POSITION ,
AND WHERE ARE ALL THE POINTS. NOW HE SHOULD BE TOLD WHERE HE HAS TO GO, WHAT PATH IT HAS TO CHOOSE
AND WHAT HE HAS TO DO THERE. WHAT CAN BE DONE ?

SOLUTION: - out of the three problems mentioned above two of them can simply be done by adding few variables
. We can store the value of the location where he has to go and the purpose of going there ( like pick-up)
or drop or buzzer or aanything else. But when it comes to path plannig we need a proper algorithm. 
We've mentioned in task 3 that why we are using A* algorithm and why it is better than others in this 
scenario. 

to implement A* we need to know the actual distance of the destination node from the current node
and for that purpose we have stepcount1 function which gives a list of movements from the input, input 
contains current and destination node location. The logic behind stepcount1() is that the location of 
any node will be a cordinate of X-Y and to find the distance we can use the manhattan distance directly
simply by subtracting them.

Now we've the ability to find the distance between two nodes and it's time to plan the path between the 
nodes and for that lets assume the case where we need to go from (x1,y1) to (x2,y2). 

starting with (x1,y1), we'll check what are the next possible directions(using function av(line-161)) in which the robot can be moved. 
Then we'll check one more thing, amongst all the possible moves available from the current node which one 
will have the least distance from the final destination node. The one with the least distance from the
final node will be added in the path (in the allmoves list). then this process is repeated untill the 
destination is reached.

Now our robot can move to any node or say to any hexagon's any axes.

Now the algorithm of planning the path is done and its time to move the robot. FOr that we need to 
move the robot in the specific directions(because for moving the robot commands are to be sent for motor).
Now in the allmoves(where all nodes between initial and final nodes are stored) we move from one node 
to next node step by step. For one movement we need to find the direction and that can be done simply 
using the 2-D matrix concept that we've used. By simply comparing the X and Y of both the nodes.
Comparing the nodes will give us the correct direction for the next movement which will be done easily
using the WHITE LINE SENSOR. 

Now almost 80% of the work is done. Our robot can move from one node to another node perfectly. 
Perfectly ??. wait NO.

WHAT IF YOU HAVE TO TAKE A U-TURN AND GO DOWN THE GRAPH, THE DIRECTIONS WILL REVERSE AND THE ROBOT WILL 
GO ANYWHERE AND YOUR ALGORITHM WILL FAIL. SO WHAT NOW ? OUR ALL HARDWORK IS WASTE ? 
ALL THE WORK DONE ABOVE IS A WASTE ? IS THERE ANY SOLUTION TO THIS PROBLEM ?

So the answer to this question is YES. YES w've a solution to this . We can make a compass in our code
this compass will keep record of the previous moves and then will compare it with the next move and then 
according it will make the corrected directions. For example : you've taken a U-turn and now the next
move is on your right up , but the robot is facing in opposite direction so for the robot it will be 
left down. So we'll in that case if we don't use compass and send right up it will go wrong.  So using 
function compass will help us solving the issue mentioned above.


So this was the overall traversal process's detailed explanation.

in addition to them we've other function also for some minor movements and other support. 
Like we've function mad(line -663) and rvrt(line - 759) which help us moving the robot to face at axes
after reaching the destination using mad( move at destination) and then bringing it back to the same
position for future movements using function rvrt.


we've finalmove which uses the functions like saveposition to extract the information of the given nodes
by E-yantra. 



"""

premove = []
predir = []
import serial
import time

ser = serial.Serial("COM4", 9600, timeout=0.005)
# ser:- this variable will be used for serial communication with the robot.

crowid = 10  # crowid:- Aruco_id for the robot

allmoves = []  # Globalvariable for moves between any two nodes

arena_config = {
    0: ("Water Pitcher", 6, "2-2"),
    2: ("Pebble", 8, "3-3"),
    4: ("Pebble", 16, "2-2"),
    6: ("Pebble", 19, "1-1"),
}
#  arena_config:- Provided arena config by eyantra
m = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
"""
    This variable is the representatoin of the flex in a matrix. We assumed the flex as a X-Y cordinate 
    and each node as one unit of distance. The flex was symmetrical and hence we made a virtual 
    graph using 2-D matrix that is going to help us through out the traversal.
"""
dests = [
    [1, "1-1", [[8, 10], [5, 10]]],
    [1, "2-2", [[7, 11], [6, 9]]],
    [1, "3-3", [[6, 11], [7, 9]]],
    [2, "1-1", [[10, 9], [7, 9]]],
    [2, "2-2", [[9, 10], [8, 8]]],
    [2, "3-3", [[9, 8], [8, 10]]],
    [3, "1-1", [[8, 8], [5, 8]]],
    [3, "2-2", [[7, 9], [6, 7]]],
    [3, "3-3", [[6, 9], [7, 7]]],
    [4, "1-1", [[3, 9], [6, 9]]],
    [4, "2-2", [[5, 10], [4, 8]]],
    [4, "3-3", [[4, 10], [5, 8]]],
    [5, "1-1", [[9, 8], [12, 8]]],
    [5, "2-2", [[11, 9], [10, 7]]],
    [5, "3-3", [[10, 9], [11, 7]]],
    [6, "1-1", [[7, 7], [10, 7]]],
    [6, "2-2", [[9, 8], [8, 6]]],
    [6, "3-3", [[9, 6], [8, 8]]],
    [7, "1-1", [[5, 6], [8, 6]]],
    [7, "2-2", [[7, 7], [6, 5]]],
    [7, "3-3", [[7, 5], [6, 7]]],
    [8, "1-1", [[6, 7], [3, 7]]],
    [8, "2-2", [[5, 8], [4, 6]]],
    [8, "3-3", [[5, 6], [4, 8]]],
    [9, "1-1", [[1, 8], [4, 8]]],
    [9, "2-2", [[3, 9], [2, 7]]],
    [9, "3-3", [[3, 7], [2, 9]]],
    [10, "1-1", [[9, 6], [12, 6]]],
    [10, "2-2", [[11, 7], [10, 5]]],
    [10, "3-3", [[11, 5], [10, 7]]],
    [11, "1-1", [[7, 5], [10, 5]]],
    [11, "2-2", [[9, 6], [8, 4]]],
    [11, "3-3", [[9, 4], [8, 6]]],
    [12, "1-1", [[5, 4], [8, 4]]],
    [12, "2-2", [[7, 5], [6, 3]]],
    [12, "3-3", [[7, 3], [6, 5]]],
    [13, "1-1", [[6, 5], [3, 5]]],
    [13, "2-2", [[5, 6], [4, 4]]],
    [13, "3-3", [[5, 4], [4, 6]]],
    [14, "1-1", [[1, 6], [4, 6]]],
    [14, "2-2", [[3, 7], [2, 5]]],
    [14, "3-3", [[3, 5], [2, 7]]],
    [15, "1-1", [[9, 4], [12, 4]]],
    [15, "2-2", [[11, 5], [10, 3]]],
    [15, "3-3", [[10, 5], [11, 3]]],
    [16, "1-1", [[10, 3], [7, 3]]],
    [16, "2-2", [[9, 4], [8, 2]]],
    [16, "3-3", [[8, 4], [9, 2]]],
    [17, "1-1", [[5, 2], [8, 2]]],
    [17, "2-2", [[7, 3], [6, 1]]],
    [17, "3-3", [[7, 1], [6, 3]]],
    [18, "1-1", [[3, 3], [6, 3]]],
    [18, "2-2", [[5, 4], [4, 2]]],
    [18, "3-3", [[5, 2], [4, 4]]],
    [19, "1-1", [[1, 4], [4, 4]]],
    [19, "2-2", [[3, 5], [2, 3]]],
    [19, "3-3", [[3, 3], [2, 5]]],
]
""" dests:- this variable keeps record of the positions of the axes of each node according to the 
            variable m.
"""
start = [["START-2", [1, 6]], ["START-1", [12, 6]]]  # two possible starts

Robot_start = "START-1"  # start provided by E-yantra.

allpositions = (
    []
)  # Global variable that will help in extracting the config from the provided details
m[7][5] = 0
"""
Function Name : av()
Input: ci-current positions of x axis,cj-current position of j axis
Output: cord- cordinates of the next possible moves
Purpose: This function tell us about the possible moves from the current node :
    it returns the cordinate of the adjacent nodes.As we've implemented the graph using a 2D matrix
    it simply checks in all the 8 possible directions and then returns the cord i.e the cordinate of 
    next possible moves
"""


def av(ci, cj):
    cord = []
    up = dn = lt = rt = dnlt = dnrt = uplt = uprt = 0
    if m[ci + 1][cj + 1] == 1:
        uplt = 1
        cord.append([ci + 1, cj + 1])
    if m[ci - 1][cj - 1] == 1:
        dnrt = 1
        cord.append([ci - 1, cj - 1])
    if m[ci + 1][cj] == 1:
        up = 1
        cord.append([ci + 1, cj])
    if m[ci][cj + 1] == 1:
        lt = 1
        cord.append([ci, cj + 1])
    if m[ci - 1][cj] == 1:
        dn = 1
        cord.append([ci - 1, cj])
    if m[ci - 1][cj + 1] == 1:
        dnlt = 1
        cord.append([ci - 1, cj + 1])
    if m[ci][cj - 1] == 1:
        rt = 1
        cord.append([ci, cj - 1])
    if m[ci + 1][cj - 1] == 1:
        uprt = 1
        cord.append([ci + 1, cj - 1])
    return cord


"""
Function Name : stepcount()
Input: curri-initial points of x axis,currj-initial points of j axis, dest & destj- final 
       destination points of x and y
Output: A list containing total number of moves in each direction and overall no. of moves.
Purpose:This function is to count the no of steps between two selected nodes :
        it return the no of upward , downward , left ,right movements required to 
        reach the destination and the total no of moves also 
"""


def stepcount(curri, currj, desti, destj):
    steprt = steplt = stepup = stepdn = 0
    if curri - desti < 0:
        stepup = abs(curri - int(desti))
    else:
        stepdn = abs(curri - int(desti))
    if currj - int(destj) < 0:
        steprt = abs(currj - int(destj))
    else:
        steplt = abs(currj - int(destj))
    total = steprt + steplt + stepup + stepdn
    return [steplt, steprt, stepup, stepdn, total]


"""
Function Name : move()
Input: ci-current positions of x axis,cj-current position of j axis,desti & destj- Destination points
Output: None
Purpose:This function take the initial and the final destination and then amongst all the
        possible moves it selects the one from which the destination is nearest and appends that
        node into allmoves . It then recusrsively calls itself by after assigning the new 
        nodes appended into allmoves as the current location and does all the process again
        for the new points as initail points.  
"""


def move(ci, cj, desti, destj):
    minsize = 990
    cord = []
    n = av(ci, cj)
    for points in n:
        k = stepcount(points[0], points[1], desti, destj)
        if k[-1] < minsize:
            minsize = k[-1]
            cord = points
    allmoves.append(cord)
    if minsize == 0:
        return 0
    move(cord[0], cord[1], desti, destj)


"""def savepositions():  
    for points in start:
        if points[0]==Robot_start:
            ci=points[1][0]
            cj=points[1][1]  
    for i in arena_config:
        typ=arena_config[i][0]
        comb=arena_config[i][1]
        pos=arena_config[i][2]
        for data in dests:
            if data[0]==comb and data[1]==pos:
                cord=data[2]
        allpositions.append([typ, cord, i , 2])
    currentposition=[ci,cj]
    return currentposition
"""
"""
Function Name : movethebot()
Input: ci-current positions of x axis,cj-current position of j axis,di & dj- Destination points
Output: None
Purpose: This functions is used to get allmoves between two points using the function move and then 
        getting the directions (exact and corrected(using compass)).

"""


def movethebot(ci, cj, di, dj):
    # if ci!=di and cj!=dj:
    # print(premove)
    # print(allmoves)
    print("csdfwds")
    allmoves.append([ci, cj])
    move(ci, cj, di, dj)
    getdirections()
    run1()


"""
Function Name : move()
Input: curri-current positions of x axis,currj-current position of j axis,desti & destj- Destination points
Output: kk-direction for the next move
Purpose:This functions returns the direction for the next adjacent point which is further corrected by 
        compass() 

"""


def stepcount1(curri, currj, desti, destj):
    kk = 0
    steprt = steplt = stepup = stepdn = 0
    if curri - desti < 0:
        stepup = abs(curri - int(desti))
    else:
        stepdn = abs(curri - int(desti))
    if currj - int(destj) < 0:
        steprt = abs(currj - int(destj))
    else:
        steplt = abs(currj - int(destj))
    total = steprt + steplt + stepup + stepdn
    k = [steplt, steprt, stepup, stepdn, total]
    print(k)
    if k[0] > 0 and k[2] > 0:
        kk = "ltup"
        # print(kk)
    elif k[0] > 0 and k[3] > 0:
        kk = "ltdn"
        # print(kk)
    elif k[1] > 0 and k[2] > 0:
        kk = "rtup"
        # print(kk)
    elif k[1] > 0 and k[3] > 0:
        kk = "rtdn"
        # print(kk)
    elif k[2] > 0:
        kk = "up"
        # print(kk)
    elif k[3] > 0:
        kk = "dn"

    return kk


cdi = []
"""
Function Name : compass()
Input: nm-next move
Output: corrected direction
Purpose: this functions take the next move from the stepcount1 function and then decides the direction
        according to the previous move and the alignment of the robot.
"""


def compass(nm):

    if len(premove) != 0:
        pm = premove[-1]
        if pm == "up":
            if nm == "dn":
                return "rt2up"
            else:
                return nm
        elif pm == "dn":
            if nm == "ltdn":
                return "rtup"
            elif nm == "rtdn":
                return "ltup"
            elif nm == "up":
                return "rt2up"
        elif pm == "ltdn":
            if nm == "ltup":
                return "rtup"
            elif nm == "dn":
                return "ltup"
            elif nm == "rtup":
                return "lt2up"
        elif pm == "rtdn":
            if nm == "dn":
                return "rtup"
            elif nm == "rtup":
                return "ltup"
            elif nm == "ltup":
                return "rt2up"
        elif pm == "rtup":
            if nm == "up":
                return "ltup"
            elif nm == "rtdn":
                return "rtup"
            elif nm == "ltdn":
                return "rt2up"
        elif pm == "ltup":
            if nm == "up":
                return "rtup"
            elif nm == "ltdn":
                return "ltup"
            elif nm == "rtdn":
                return "lt2up"

    else:
        if nm == "ltdn":
            return "ltup"
        elif nm == "rtdp":
            return "rtup"
        else:

            return nm


dii = []
"""
Function Name : getdirections()
Input: None
Output: None
Purpose:After getting the finals nodes of the path , we need to get the directions for movement
    of the robot. This function uses the lsit DII containg all the nodes that will come in 
    the path and it will generate a list which will contain the movement directions 
    according to the areana. It then Uses the function COMPASS to get the directions 
    according to the current configuration of the robot and put them in a list CDI. 
"""


def getdirections():
    for x in range(len(allmoves) - 1):
        dii.append(
            stepcount1(
                allmoves[x][0], allmoves[x][1], allmoves[x + 1][0], allmoves[x + 1][1]
            )
        )
    for y in range(len(dii)):
        cdi.append(compass(dii[y]))
        premove.append(dii[y])


pebble = []
water = []

"""
mapp
we have assumed the arena to be a X-Y cordinate but we have two starts and hence if the starting position changes 
everything everything will change. we've marked the axes from start 2. if the robot has to start from start 1 this will help it.
"""
mapp = {
    1: 17,
    2: 18,
    3: 12,
    4: 16,
    5: 19,
    6: 13,
    7: 7,
    8: 11,
    9: 15,
    10: 14,
    11: 8,
    12: 3,
    13: 6,
    14: 10,
    15: 9,
    16: 4,
    17: 1,
    18: 2,
    19: 5,
}
"""        
Function Name : savepositions1()
Input: None
Output: currentposition- starting position of the bot .
Purpose: this function extracts the features from the given configuration from E-yantra
        and makes it more accesible by preparing a list of pebbles and water. 
        that contains the information about the pickup zone and the pitcher zone.
        
"""


def savepositions1():
    global allpositions
    for points in start:
        if points[0] == Robot_start:
            ci = points[1][0]
            cj = points[1][1]
    for i in arena_config:
        typ = arena_config[i][0]
        comb = arena_config[i][1]
        pos = arena_config[i][2]
        if ci == 12 and cj == 6:
            comb = mapp[comb]
        for data in dests:
            if data[0] == comb and data[1] == pos:
                cord = data[2]
        if typ == "Pebble":
            pebble.append([typ, cord, pos, i, 1])
        elif typ == "Water Pitcher":
            water.append([typ, cord, pos, i, 0])
    if ci == 12 and cj == 6:
        ci = 1
    currentposition = [ci, cj]

    return currentposition


"""
Function Name : finalmove()
Input: start:- currentposition obtained from the saveposition function.
Output: None.
Purpose: this function send command to the robot using the bhagna function that uses run1() and then the
        robot moves. This does all the pick up managment in proper way. find the nearest pickup zone
        and moves to that from the current location. After putting one pebble into pitcher, it again searches
        for the nearest pebble and then goes there to pickup . Along with the complete movement traversal 
        it also does the mad and the rvrt thing along with the buzzer for 5 seconds at last.
        
"""


def finalmove(start):
    global pebble
    nearest = 999
    for lab, points in enumerate(pebble):
        if points[-1] > 0:
            if (
                stepcount(start[0], start[1], points[1][1][0], points[1][1][1])[-1]
                < nearest
                and m[points[1][1][0]][points[1][1][1]] != 0
            ):
                nearest = stepcount(
                    start[0], start[1], points[1][1][0], points[1][1][1]
                )[-1]
                dest = points[1][1]
                minu = lab
            if (
                stepcount(start[0], start[1], points[1][0][0], points[1][0][1])[-1]
                < nearest
                and m[points[1][0][0]][points[1][0][1]] != 0
            ):
                nearest = stepcount(
                    start[0], start[1], points[1][0][0], points[1][0][1]
                )[-1]
                dest = points[1][0]
                minu = lab

    print(pebble)
    # time.sleep(1)
    print(start, dest)
    bhagna(start[0], start[1], dest[0], dest[1])
    pebble[minu][-1] -= 1
    ser.write("m".encode())
    mad(pebble[minu][2], premove)
    rvrt(predir)

    print(pebble)
    i = 0
    while True:
        if i % 2 == 0:
            curr = dest
            if (
                stepcount(curr[0], curr[1], water[0][1][0][0], water[0][1][0][1])[-1]
                < stepcount(curr[0], curr[1], water[0][1][1][0], water[0][1][1][1])[-1]
            ):
                dest = water[0][1][0]
            else:
                dest = water[0][1][1]
            config = water[0][2]
            bhagna(curr[0], curr[1], dest[0], dest[1])
            water[0][-1] += 1
            print("bole")
        else:
            curr = dest
            nearest = 999
            for lab, points in enumerate(pebble):
                if points[-1] > 0:
                    if (
                        stepcount(curr[0], curr[1], points[1][1][0], points[1][1][1])[
                            -1
                        ]
                        < nearest
                        and m[points[1][1][0]][points[1][1][1]] != 0
                    ):
                        nearest = stepcount(
                            curr[0], curr[1], points[1][1][0], points[1][1][1]
                        )[-1]
                        dest = points[1][1]
                        minu = lab
                    if (
                        stepcount(curr[0], curr[1], points[1][0][0], points[1][0][1])[
                            -1
                        ]
                        < nearest
                        and m[points[1][0][0]][points[1][0][1]] != 0
                    ):
                        nearest = stepcount(
                            curr[0], curr[1], points[1][0][0], points[1][0][1]
                        )[-1]
                        dest = points[1][0]
                        minu = lab

            bhagna(curr[0], curr[1], dest[0], dest[1])
            pebble[minu][-1] -= 1
            config = pebble[minu][2]
        # time.sleep(0.5)
        print(curr, dest)
        if i % 2 != 0:
            pass
            ser.write("m".encode())
        mad(config, premove)
        if i % 2 == 0:
            pass
            ser.write("o".encode())

        rvrt(predir)
        print(pebble)
        i += 1
        flag = False
        for points in pebble:
            if points[-1] > 0:
                flag = True

        if flag == False and i % 2 != 0:
            break
        time.sleep(1)
    ser.write("b".encode())
    time.sleep(5)
    ser.write("n".encode())


"""        
Function Name : run1()
Input: None
Output: None
Purpose: Accordint to the directions in the cdi  it sends command to the robot. run1 uses the cdi list 
    that is made after calling movethebot() which get the path from move function and directions using
    get direction function. getdirection function uses the function compass to generate a list cdi
    that is being used here to command the robot using ser variable. The delay given in this function is 
    due to the reading that are to be obtained from the white line sensor. if we don't keep delay the 
    robot will skip that node.
"""


def run1():
    for i in range(len(allmoves) - 1):
        if ser.isOpen():
            if cdi[i] == "ltup":

                ser.write("a".encode())
                # time.sleep(0.25)

                while True:
                    data = ser.read(1)
                    # print(data)
                    if data == b"o":
                        # print(data)
                        break
                time.sleep(0.20)
                ser.write("w".encode())
            elif cdi[i] == "rtup":
                ser.write("d".encode())
                # time.sleep(0.25)
                # print('rtupsdasdaasd')
                while True:
                    data = ser.read(1)
                    # print(data)
                    if data == b"o":
                        # print(data)
                        break
                time.sleep(0.20)
                ser.write("w".encode())
                # time.sleep(0.55)
            elif cdi[i] == "lt2up" or cdi[i] == "rt2up":
                ser.write("a".encode())
                # print('hiiio')
                time.sleep(0.25)
                ser.write("k".encode())
                time.sleep(0.25)
                ser.write("k".encode())
                time.sleep(0.25)
                ser.write("a".encode())
                while True:
                    data = ser.read(1)
                    #    print(data)
                    if data == b"o":
                        #       print(data)
                        break
                time.sleep(0.20)
                ser.write("w".encode())
                time.sleep(0.55)
            elif cdi[i] == "rt2up":
                ser.write("a".encode())
                time.sleep(0.25)
                ser.write("k".encode())
                time.sleep(0.25)
                ser.write("a".encode())

                while True:
                    data = ser.read(1)
                    #  print(data)
                    if data == b"o":
                        # print(data)
                        break
                time.sleep(0.20)
                ser.write("w".encode())
                time.sleep(0.55)
            ser.write("j".encode())
            #  print(allmoves[i], allmoves[i+1])
            time.sleep(1)


"""
Function Name : clearBuffer()
Input: None
Output: None
Purpose: this function clears all the global variable after every move except for the premove
"""


def clearBuffer():
    global dii, cdi, allmoves
    dii = []
    cdi = []
    # premove=[]
    allmoves = []


"""
Function Name : bhagna()
Input: i-current positions of x axis,j-current position of j axis,k & l- Destination points
Output: None
Purpose: This functions call movethebot and then clearBuffer so this functions can be used directly for
        continious nd nonstop movements. we cannot clear premove once the robot has started , and to keep
        that goal this function is used. 
"""


def bhagna(i, j, k, l):
    movethebot(i, j, k, l)
    print("allmoves")
    print(allmoves)
    print("cdi")
    print(cdi)
    # print('dii')
    # print(dii)
    clearBuffer()


"""
Function Name : mad()---- Move at destination 
Input: axes- the axes mentioned in the polygons , pm= premove
Output: None
Purpose: This functions is used to move the bot for picking up the pebble after reaching the destination
            node with the help of previous move. This functions take two arguments axes and pm. In axes one
            needs to mention the axes to which he want to drop or pick the pebble. In the pm it should be 
            given the list of premoves. So now it has the list of previous moves and the axes.It will 
            then see what sequence of moves it should follow to get to the axes based on the pattern 
            of the axes nd the previous moves. Once the moves are done then the id of sequence pattern
            is appended into the predir(this will be used to revert the movements and bring back robot in
            the same position by rvrt function). 
"""


def mad(axes, pm):
    if axes == "1-1":
        if pm[-1] == "up" or pm[-1] == "dn":
            ser.write("f".encode())
            time.sleep(0.15)
            ser.write("j".encode())
            predir.append(1)
        elif pm[-1] == "ltup" or pm[-1] == "rtdn":
            ser.write("a".encode())
            time.sleep(0.25)
            ser.write("y".encode())
            time.sleep(0.4)
            ser.write("j".encode())
            time.sleep(0.1)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(2)
        elif pm[-1] == "ltdn" or pm[-1] == "rtup":
            ser.write("d".encode())
            time.sleep(0.25)
            ser.write("u".encode())
            time.sleep(0.4)
            ser.write("j".encode())
            time.sleep(0.1)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(3)
    elif axes == "2-2":
        if pm[-1] == "up" or pm[-1] == "dn":
            ser.write("a".encode())
            time.sleep(0.25)
            ser.write("y".encode())
            time.sleep(0.4)
            ser.write("j".encode())
            time.sleep(0.1)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(2)
        elif pm[-1] == "ltup" or pm[-1] == "rtdn":
            ser.write("d".encode())
            time.sleep(0.25)
            ser.write("u".encode())
            time.sleep(0.4)
            ser.write("j".encode())
            time.sleep(0.25)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(3)
        elif pm[-1] == "ltdn" or pm[-1] == "rtup":
            ser.write("f".encode())
            time.sleep(0.15)
            ser.write("j".encode())
            predir.append(1)
    elif axes == "3-3":
        if pm[-1] == "up" or pm[-1] == "dn":
            ser.write("d".encode())
            time.sleep(0.25)
            ser.write("u".encode())
            time.sleep(0.4)
            ser.write("j".encode())
            time.sleep(0.25)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(3)
        elif pm[-1] == "ltup" or pm[-1] == "rtdn":
            ser.write("f".encode())
            time.sleep(0.15)
            ser.write("j".encode())
            predir.append(1)
        elif pm[-1] == "ltdn" or pm[-1] == "rtup":
            print("hiii")
            ser.write("a".encode())
            time.sleep(0.25)
            ser.write("y".encode())
            time.sleep(0.4)
            ser.write("f".encode())
            time.sleep(0.1)
            ser.write("j".encode())
            predir.append(2)
    ser.write("j".encode())
    time.sleep(1.25)


"""
Function Name : rvrt() 
Input: pd=predir
Output: None
Purpose: This functions is used to get the robot back in the position after picking up the pebble. 
        basically for alignment. This function takes pd as an argument which is a list of predir.It 
        contains the record of the movements done at mad and then it reverses all the movements and then 
        the robot comes back to its original position. 
"""


def rvrt(pd):
    if pd[-1] == 1:
        ser.write("z".encode())
        time.sleep(0.15)
        ser.write("j".encode())
    if pd[-1] == 2:
        ser.write("z".encode())
        time.sleep(0.15)
        ser.write("j".encode())
        ser.write("d".encode())
        time.sleep(0.15)
        ser.write("u".encode())
        time.sleep(0.5)
        ser.write("j".encode())
    if pd[-1] == 3:
        ser.write("z".encode())
        time.sleep(0.15)
        ser.write("j".encode())
        ser.write("a".encode())
        time.sleep(0.15)
        ser.write("y".encode())
        time.sleep(0.5)
        ser.write("j".encode())
    ser.write("j".encode())
    time.sleep(1.25)
