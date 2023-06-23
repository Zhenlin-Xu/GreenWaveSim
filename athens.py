# the size of link and node
LINK_GRIDSIZE = 6
NODE_HEIGHT = 5*LINK_GRIDSIZE
NODE_WIDTH  = LINK_GRIDSIZE
NODE_SIZE   = LINK_GRIDSIZE

OUTER_LINK_LENGTH = 210
LINK_NORMAL = 0
LINK_IN  = 1
LINK_OUT = 2

# car types:
T_Car = 1
T_Bus = 2
T_Taxi = 3
T_Heavy = 4
T_Medium = 5

# Size of the pygame window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT= 600

# Node positions
node_CenterPositions = {
    # node 1
    1 : (SCREEN_WIDTH//2  - 350//7*LINK_GRIDSIZE - NODE_WIDTH,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 2
    2 : (SCREEN_WIDTH//2,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 3
    3 : (SCREEN_WIDTH//2  + 91//7*LINK_GRIDSIZE + NODE_WIDTH,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 4
    4 : (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*2,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 5
    5 : (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*2,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 6
    6 : (SCREEN_WIDTH//2  + 91//7*LINK_GRIDSIZE + NODE_WIDTH,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 7
    7 : (SCREEN_WIDTH//2,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 8
    8 : (SCREEN_WIDTH//2  - 175//7*LINK_GRIDSIZE- NODE_WIDTH,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 9
    9 : (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 11
    11: (SCREEN_WIDTH//2  - 350//7*LINK_GRIDSIZE - NODE_WIDTH,
         SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT- NODE_SIZE//2),
    # node 12
    12: (SCREEN_WIDTH//2,
         SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT- NODE_SIZE//2),
    # node 13
    13: (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*2,
         SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT- NODE_SIZE//2),
    # node 21
    21: (SCREEN_WIDTH//2  + (175+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_WIDTH*3,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 22
    22: (SCREEN_WIDTH//2  + (175+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_WIDTH*3,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
    # node 31
    31: (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*2,
         SCREEN_HEIGHT//2 + (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_HEIGHT+ NODE_SIZE//2),
    # node 32
    32: (SCREEN_WIDTH//2,
         SCREEN_HEIGHT//2 + (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_HEIGHT+ NODE_SIZE//2),   
    # node 33
    33: (SCREEN_WIDTH//2  - 175//7*LINK_GRIDSIZE- NODE_WIDTH,
         SCREEN_HEIGHT//2 + (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_HEIGHT+ NODE_SIZE//2),  
    # node 34
    34: (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH,
         SCREEN_HEIGHT//2 + (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE + NODE_HEIGHT+ NODE_SIZE//2),    
    # node 41
    41: (SCREEN_WIDTH//2  - (350+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_WIDTH*3//2 - NODE_SIZE//2,
         SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT//2),
    # node 42
    42: (SCREEN_WIDTH//2  - (350+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_WIDTH*3//2 - NODE_SIZE//2,
         SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT//2),
}

# trafficLight directions 
tf_Directions = {
    # value: UP_Mainroad, DOWN_mainroad, DOWN_branch, UP_branch
    1: [2,42,11,9],
    2: [3,1,12,7],
    3: [4,2,6,None],
    4: [21,3,13,5],
    5: [6,22,4,31],
    6: [7,5,None,3],
    7: [8,6,2,32],
    8: [9,7,33,None],
    9: [41,8,1,34]
}


# GreenWave phase
tf_Phases = {
    1: (2, [10,5]),
    2: (2, [5,5]),
    3: (1, [5]),
    4: (2, [5,5]),
    5: (2, [10,5]),
    6: (1, [5]),
    7: (2, [5,5]),
    8: (2, [5,5]),
    9: (2, [5,5]),  
}


# Baseline phase
# tf_Phases = {
#     1: (2, [39,39]),
#     2: (2, [39,39]),
#     3: (1, [39]),
#     4: (2, [39,39]),
#     5: (2, [39,39]),
#     6: (1, [39]),
#     7: (2, [39,39]),
#     8: (2, [39,39]),
#     9: (2, [39,39]),  
# }


# Link positions
# Link(linkId, lengthLane, numLanes, originNodeId, destinNodeId, type)
link_Infos = {
    'i2o1': (350, 5, 2, 1, LINK_NORMAL, (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT)),
    'i3o2': ( 91, 5, 3, 2, LINK_NORMAL, (SCREEN_WIDTH//2 + NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT)),
    'i4o3': ( 84, 5, 4, 3, LINK_NORMAL, (SCREEN_WIDTH//2 + 91//7*LINK_GRIDSIZE + NODE_WIDTH*3//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT)),

    'i21o4':(OUTER_LINK_LENGTH, 5, 21,4, LINK_IN, (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*5//2,
                                                SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT)),
    'i1o42':(OUTER_LINK_LENGTH, 5, 1, 42, LINK_OUT, (SCREEN_WIDTH//2  - (350+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                                SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE - NODE_HEIGHT)),

    'i6o5': ( 84, 5, 6, 5, LINK_NORMAL, (SCREEN_WIDTH//2 + 91//7*LINK_GRIDSIZE + NODE_WIDTH*3//2,
                                        SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),
    'i7o6': ( 91, 5, 7, 6, LINK_NORMAL, (SCREEN_WIDTH//2 + NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),
    'i8o7': (175, 5, 8, 7, LINK_NORMAL, (SCREEN_WIDTH//2 - 175//7*LINK_GRIDSIZE - NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),
    'i9o8': (175, 5, 9, 8, LINK_NORMAL, (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                        SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),

    'i5o22':(OUTER_LINK_LENGTH, 5, 5, 22, LINK_OUT, (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*5//2,
                                                SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),
    'i41o9':(OUTER_LINK_LENGTH, 5, 41, 9, LINK_IN, (SCREEN_WIDTH//2  - (350+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                                SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE)),

    'i1o11':(OUTER_LINK_LENGTH, 1, 1, 11, LINK_OUT, (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                                    SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT*2//2)),
    'i9o1' :(140, 1, 9, 1, LINK_NORMAL, (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE)), 
    'i34o9':(OUTER_LINK_LENGTH, 1, 34, 9, LINK_IN, (SCREEN_WIDTH//2 - 350//7*LINK_GRIDSIZE - NODE_WIDTH*3//2,
                                                    SCREEN_HEIGHT//2 + (70)//7*LINK_GRIDSIZE + NODE_HEIGHT)),    
    'i2o12':(OUTER_LINK_LENGTH, 1, 2, 12, LINK_OUT, (SCREEN_WIDTH//2 - NODE_WIDTH//2,
                                                    SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT*2//2)),
    'i7o2' :(140, 1, 7, 2, LINK_NORMAL, (SCREEN_WIDTH//2 - NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE)),
    'i32o7':(OUTER_LINK_LENGTH, 1, 32,7, LINK_IN, (SCREEN_WIDTH//2 - NODE_WIDTH//2,
                                                   SCREEN_HEIGHT//2 + (70)//7*LINK_GRIDSIZE + NODE_HEIGHT)), 
    'i4o13':(OUTER_LINK_LENGTH, 1, 4, 13, LINK_OUT, (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*3//2,
                                                    SCREEN_HEIGHT//2 - (70+OUTER_LINK_LENGTH)//7*LINK_GRIDSIZE - NODE_HEIGHT*2//2)),
    'i5o4' :(140, 1, 5, 4, LINK_NORMAL, (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*3//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE)),
    'i31o5':(OUTER_LINK_LENGTH, 1, 31, 5, LINK_IN, (SCREEN_WIDTH//2  + 175//7*LINK_GRIDSIZE + NODE_WIDTH*3//2,
                                                    SCREEN_HEIGHT//2 + (70)//7*LINK_GRIDSIZE + NODE_HEIGHT)), 

    'i8o33':(OUTER_LINK_LENGTH, 1, 8, 33, LINK_OUT, (SCREEN_WIDTH//2  - 175//7*LINK_GRIDSIZE- NODE_WIDTH*3//2,
                                                     SCREEN_HEIGHT//2 + 70//7*LINK_GRIDSIZE + NODE_HEIGHT)),
    'i3o6' :(140, 1, 3, 6, LINK_NORMAL,(SCREEN_WIDTH//2  + 91//7*LINK_GRIDSIZE + NODE_WIDTH//2,
                                        SCREEN_HEIGHT//2 - 70//7*LINK_GRIDSIZE)),
}
