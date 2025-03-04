"""
Andy Strozewski, Ana Verulidze, and Katrina Ziebarth
CS 365 Lab B
andystrozewski-anaverulidze-katrinaziebarth-labB.py
"""

import os
import copy
import random

class Board:
    def __init__(self, rows, cols, pieces):
        self.rows = rows
        self.cols = cols
        self.pieceRows = pieces
        self.emptyRows = rows - 2 * pieces
        
    def getNumRows(self):
        return self.rows
    def getNumCols(self):
        return self.cols

class State:
    def __init__(self,pieceLocations):
        self.pieceLocations = pieceLocations
    def getPieceLocations(self):
        return self.pieceLocations
    
def initial_state_and_board(numRows, numCols, pieceRows): #pieceRows is an integer representing the number of rows each player has
    board = Board(numRows, numCols, pieceRows)
    locationDict = {}
    for i in range(pieceRows):
        for j in range(numCols):
            locationDict[(i, j)] = "X"
    for i in range(numRows-1, numRows-pieceRows-1, -1):
        for j in range(numCols):
            locationDict[(i, j)] = "O"
    state = State(locationDict)
    return state, board
    
def display_state(inputState, board):
    if os.path.isfile("currentState.txt"):
        os.remove("currentState.txt")
    pieces = inputState.getPieceLocations()
    piecesFile = open("currentState.txt", 'a')
    for r in range(board.getNumRows()):
        for c in range(board.getNumCols()):
            if (r,c) in inputState.getPieceLocations():
                piecesFile.write(inputState.getPieceLocations()[r,c])
            else:
                piecesFile.write("-")
        piecesFile.write("\n")
    print("")
    piecesFile.close()
    piecesFile = open("currentState.txt", 'r')
    print(piecesFile.read(), end="")
    piecesFile.close()

def generate_moves(currState, board, player):  #revised code
    possibleMoves = []
    for p in currState.pieceLocations.keys():
        if currState.pieceLocations[p] == player:
            if player == "X":
                newrow = p[0]+1 #movement will be south by one row
                #print(newrow)
            else: #if player is O
                newrow = p[0]-1 #movement will be north by one row
            if (newrow, p[1]) not in currState.pieceLocations.keys(): #pieces must be captured diagonally
                possibleMoves.append((p, "F"))
            if (newrow, p[1]+1) not in currState.pieceLocations.keys(
                    ):
                if p[1]+1 < board.cols:
                    possibleMoves.append((p, "FE"))
            else:
                if currState.getPieceLocations()[(newrow, p[1]+1)] != player:
                    possibleMoves.append((p, "FE"))#self.numCols
            if (newrow, p[1]-1) not in currState.pieceLocations.keys():
                if p[1]-1 > -1:
                    possibleMoves.append((p, "FW"))
            else:
                if currState.pieceLocations[(newrow, p[1]-1)] != player:
                    possibleMoves.append((p, "FW"))       
    return possibleMoves
    
def transition(currState, player, move):
    newLocations = copy.deepcopy(currState.pieceLocations)
    if player == "X":
        newrow = move[0][0]+1 #movement will be south by one row
    else: #if player is O
        newrow = move[0][0]-1 #movement will be north by one row
    if move[1] == "F":
        newLocations[(newrow, move[0][1])] = player
    elif move[1] == "FE":
        newLocations[(newrow, move[0][1]+1)] = player
    else:
        newLocations[(newrow, move[0][1]-1)] = player
    newLocations.pop(move[0])
    return State(newLocations)

def isTerminal(boardState, board):
    terminal = False
    for key, value in boardState.pieceLocations.items():
        if value == "X" and key[0] == board.getNumRows()-1:
                terminal = True
        else:
            if value == "O" and key[0] == 0:
                terminal = True
    return terminal    

def utility_evasive(boardState, board, player):
    numPieces = 0
    for value in boardState.pieceLocations.values():
        if value == player:
            numPieces += 1
    return numPieces + random.random()

def utility_conquerer(boardState, board, player):
    numOppPieces = 0
    for value in boardState.pieceLocations.values():
        if value != player:
            numOppPieces += 1
    return 0 - numOppPieces + random.random()

def get_utility(utility, boardState, board, player):
    if utility == 'evasive':
        return utility_evasive(boardState, board, player)
    elif utility == 'conquerer':
        return utility_conquerer(boardState, board, player)

class Node:
    def __init__(self, action, boardState, depth):
        self.children = []
        self.action = action
        self.boardState = boardState
        self.depth = depth
        self.utility = None

def recursive_traversal(root, maxDepth):
    if not root.utility:
        if root.depth % 2 == 0:
            maxValue = -(float('inf'))
            for child in root.children:
                childUtility = recursive_traversal(child, maxDepth)
                #print(root.depth + 1)
                #print("Child Utility: " + str(childUtility))
                #print("MaxValue: " + str(maxValue))
                if childUtility > maxValue:
                    maxValue = childUtility
                    #print("MaxValue: " + str(maxValue))
            root.utility = maxValue
        else:
            minValue = float('inf')
            for child in root.children:
                childUtility = recursive_traversal(child, maxDepth)
                #print("Child Utility: " + str(childUtility))
                #print("MinValue: " + str(minValue))
                if childUtility < minValue:
                    minValue = childUtility
                    #print("MinValue: " + str(minValue))
            root.utility = minValue
    return root.utility
                    
def return_desirable_move(boardState, board, utility, player):
    currDepth = 0
    maxDepth = 4
    stack = []
    root = Node(None, boardState, 0)
    currNode = root
    stack.append(root)
    while stack:
        currNode = stack.pop()
        currDepth = currNode.depth
        for move in generate_moves(currNode.boardState, board, player):
            newState = transition(currNode.boardState, player, move)
            newNode = Node(move, newState, currDepth+1)
            currNode.children.append(newNode)
            if newNode.depth == maxDepth or isTerminal(newNode.boardState, board):
                newNode.utility = get_utility(utility, newNode.boardState, board, player)
            else:
                stack.append(newNode)
        #print(currDepth)
        #print(len(currNode.children))
        #print(len(stack))
        #currNode = stack.pop()
    rootUtility = recursive_traversal(root, maxDepth)
    #print("length of child list is: " + str(len(root.children)))
    for child in root.children:
        #print('Child Utility ' + str(child.utility))
        if child.utility == rootUtility:
            action = child.action
    return action

def play_game(heuristicO, heuristicX, boardState, board):
    total_moves = 0
    while not isTerminal(boardState, board):
        nextMoveO = return_desirable_move(boardState, board, heuristicO, "O")
        boardState = transition(boardState, "O", nextMoveO)
        total_moves += 1
        if isTerminal(boardState, board):
            break
        nextMoveX = return_desirable_move(boardState, board, heuristicX, "X")
        boardState = transition(boardState, "X", nextMoveX)    
        total_moves += 1
    display_state(boardState, board)
    print("Total moves: " + str(total_moves))
    original_count = board.cols * board.pieceRows
    x_pieces = 0
    o_pieces = 0
    for key, value in boardState.getPieceLocations().items():
        if value == 'X':
            x_pieces += 1
        else:
            o_pieces += 1
    print("Number of White Pieces Captured (O): " + str(original_count - o_pieces))
    print("Number of Black Pieces Captured (X): " + str(original_count - x_pieces))
    
    
    
def main(numRows, numCols, pieces, o_heuristic, x_heuristic):
    state, board = initial_state_and_board(numRows, numCols, pieces)
    play_game(o_heuristic, x_heuristic, state, board)
    """
    display_state(state)
    piecesFile = open("currentState.txt", 'r')
    print(piecesFile.read(), end="")
    piecesFile.close()
    moves = generate_moves(state, "X")
    print("\nPossible Moves for X:")
    for move in moves:
        display_state(transition(state, "X", move))
        piecesFile = open("currentState.txt", 'r')
        print(piecesFile.read(), end="")
        piecesFile.close()
    """
        
if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser(description='Breakthrough')
        parser.add_argument('-r', '--rows', type = int, required = True)
        parser.add_argument('-c', '--cols', type = int, required = True)
        parser.add_argument('-p', '--pieces' , type = int, required = True)
        parser.add_argument('-w', '--white_heuristic', type = str, required = True)
        parser.add_argument('-b', '--black_heuristic' , type = str, required = True)
        args = parser.parse_args()
        main(args.rows, args.cols, args.pieces, args.white_heuristic, args.black_heuristic)
        
