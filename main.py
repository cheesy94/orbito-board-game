# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 12:34:32 2023

@author: Cheesy94
"""

import numpy as np
from scipy.signal import convolve2d

### Functions
def askCoords(gamestate):
    coords = []
    while not coords:
        position = input("Choose position row,col: ")
        
        # Skip
        if position == "" and gamestate == 1:
            #print("\n")
            return "skip"
        
        position = position.split(",")
    
        # Check length
        if len(position) != 2:
            print("Input error: not 2 coordinates")
            continue
    
        # Check numbers
        for i,p in enumerate(position):
            try:
                pos = int(p)-1
            except ValueError:
                print("Input error: coord[{}] not an int".format(i))
                coords = []
                break
            if not pos in range(size[i]):
                print("Input error: coord[{}] not in range".format(i))
                coords = []
                break
            coords.append(pos)
            
    return tuple(coords)

def askDirection(coords,board):
    loop = True
    while loop:
        direction = input("Choose direction (up/down/left/right, w/a/s/d): ")
        
        # Not moved
        if direction == "":
            print("Not moved")
            loop = False
            return board
        
        direction = direction.lower()
        newcoords = list(coords)
        if direction.lower() == "up" or direction == "w":
            newcoords[0] -= 1
            loop = False
        elif direction == "down" or direction == "s":
            newcoords[0] += 1
            loop = False
        elif direction == "left" or direction == "a":
            newcoords[1] -= 1
            loop = False
        elif direction == "right" or direction == "d":
            newcoords[1] += 1
            loop = False
        else:
            print("Input error")
            continue
        newcoords = tuple(newcoords)

        # Out of bounds
        try:
            tmp = board[newcoords]
        except:
            print("Error: out of bounds")
            loop = True
            continue
        
        # Not empty
        if tmp != 0:
            print("Input error: destination is not empty")
            loop = True
            
    board[newcoords] = board[coords]
    board[coords] = 0
            
    return board

def turnBoard(board,spin):
    size = len(board)
    rotated = np.zeros_like(board)
    
    # Iterate over i-,j- quadrant (odd function)
    for j in range(int(size/2)):
        for i in range(int(size/2)):
            
            quadrants = np.array(((       i,       j),
                                  (size-1-j,       i),
                                  (size-1-i,size-1-j),
                                  (       j,size-1-i)))
            
            # Check matrix diagonal for directions
            if i>j:
                directions = spin * np.array(((1,0),(0,1),(-1,0),(0,-1)))
                # spin +: down, right, up, left
                # spin -: up, left, down, right
            elif i<j:
                directions = spin * np.array(((0,-1),(1,0),(0,1),(-1,0)))
                # spin +: left, down, right, up
                # spin -: right, up, left, down
            elif i==j:
                directions = np.array(((1,0),(0,spin),(-1,0),(0,-spin)))[:,::spin]
                # spin +: down, right, up, left
                # spin -: right, up, left, down
            
            # Apply directions
            for d,q in zip(directions,quadrants):
                rotated[tuple(d+q)] = board[tuple(q)]
    
    return rotated

def checkC4(board):
    # adapted from Manuel Faysse answer in stackoverflow
    horizontal_kernel = np.array([[ 1, 1, 1, 1]])
    vertical_kernel = np.transpose(horizontal_kernel)
    diag1_kernel = np.eye(4, dtype=np.uint8)
    diag2_kernel = np.fliplr(diag1_kernel)
    detection_kernels = [horizontal_kernel, vertical_kernel, diag1_kernel, diag2_kernel]
    
    for p in range(1,3):
        for kernel in detection_kernels:
            if(convolve2d(board==p,kernel,mode="valid") == 4).any():
                return p
    return 0

### Game
gamestate = 0
loop = 0
overloop = 0
player = False
size = (4,4)
spin = +1 # -1 clockwise / +1 anti-clockwise
board = np.zeros(size,dtype=np.ubyte)

# Main loop
while gamestate < 4:
    
    # First turn (0)
    if gamestate == 0:
        print(board,"\n")
        gamestate += 1
        if loop == 0:
            gamestate += 1
    
    # No places left
    if not (board==0).any():
        gamestate = 3
        overloop += 1
    
    # Move opponent (1)
    if gamestate == 1:
        print("Player {} can move an opponent piece (empty for skip)".format(player+1))
        coords = askCoords(gamestate)
        
        # Skip
        if coords == "skip":
            print("Skipped\n")
            gamestate += 1
            continue
        # Empty place
        if board[coords] == 0:
            print("Input error: coord is empty") #!!! newline?
            continue
        # Own piece
        if board[coords] == player+1:
            print("Input error: player own piece") #!!! newline?
            continue
        
        board = askDirection(coords,board)
        print(board,"\n")
        gamestate += 1
    
    # Add piece (2)
    if gamestate == 2:
        print("Player {} has to place a piece".format(player+1))
        coords = askCoords(gamestate)
        
        # Not empty place
        if board[coords] != 0:
            print("Input error: destination is not empty") #!!! newline?
            continue
        
        # Everything fine
        board[coords] = player+1
        print(board,"\n")
        gamestate += 1

    # Turn board (3)
    if gamestate==3:
        print("Board turned")
        board = turnBoard(board,spin)
        print(board,"\n")
    
        # Check connect-4 to continue
        if not loop > 6:
            winner = 0
        else:
            winner = checkC4(board)
        
        # Check 5 turns after board full
        if overloop > 5 or winner != 0:
             gamestate += 1
        else:
            player = not player
            gamestate = 1
            loop += 1
    
print("Winner: ",int(winner)+1)