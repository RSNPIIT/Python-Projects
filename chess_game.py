import turtle
import time

s = turtle.Screen()
s.title('chess')
# 1. Lock window and canvas dimensions to fit the 640x640 board with 40px border
s.setup(width=720, height=720)
s.screensize(700, 700)
turtle.tracer(0, 0)

# Custom Piece Geometries
s.register_shape('king',  ((-5,-8),(5,-8),(5,-3),(4,-2),(4,0),(2,1),(2,6),(4,6),(4,7),(2,7),(2,9),(-2,9),(-2,7),(-4,7),(-4,6),(-2,6),(-2,1),(-4,0),(-4,-2),(-5,-3),(-5,-8)))
s.register_shape('queen', ((-5,-8),(5,-8),(5,-3),(4,-2),(4,0),(2,1),(2,5),(3,6),(4,5),(5,6),(5,7),(3,8),(1,7),(0,8),(-1,7),(-3,8),(-5,7),(-5,6),(-4,5),(-3,6),(-2,5),(-2,1),(-4,0),(-4,-2),(-5,-3),(-5,-8)))
s.register_shape('bishop',((0,7),(1,6),(2,5),(1,4),(2,3),(1,2),(3,1),(4,0),(3,-1),(3,-3),(4,-4),(4,-8),(-4,-8),(-4,-4),(-3,-3),(-3,-1),(-4,0),(-3,1),(-1,2),(-2,3),(-1,4),(-2,5),(-1,6),(0,7)))
s.register_shape('knight',((-5,-8),(5,-8),(5,-3),(1,-3),(4,1),(1,5),(-2,4),(-2,0),(-5,0),(-5,-8)))
s.register_shape('rook',  ((-4,4),(4,4),(4,2),(3,1),(3,-2),(5,-6),(5,-8),(-5,-8),(-5,-6),(-3,-2),(-3,1),(-4,2),(-4,4)))
s.register_shape('pawn',  ((0,6),(1,6),(2,5),(2,4),(2,2),(1,1),(2,0),(2,-2),(3,-3),(4,-6),(3,-7),(0,-7),(-3,-7),(-4,-6),(-3,-3),(-2,-2),(-2,0),(-1,1),(-2,2),(-2,4),(-2,5),(-1,6),(0,6)))

backgroundColor = '#2c2c2c'
squareColor1 = '#18242b'
squareColor2 = '#84c9FB'
loopCount = 0
selectedPiece = None
selectedSquare = None
activeTeam = 'white'
capturedPiece = None
turtle.bgcolor(backgroundColor)

# 2. Symmetrically centered coordinates (-280 to +280 in steps of 80)
files_x = {'a': -280, 'b': -200, 'c': -120, 'd': -40, 'e': 40, 'f': 120, 'g': 200, 'h': 280}
ranks_y = {'1': -280, '2': -200, '3': -120, '4': -40, '5': 40, '6': 120, '7': 200, '8': 280}

notation = {f"{f}{r}": [files_x[f], ranks_y[r]] for f in 'abcdefgh' for r in '12345678'}

enPassantDict = {e: False for e in notation}

piecePositions = { ## PIECE POSITIONS
    'a1':"wr1",'a2':"wp1",'a3':"empty",'a4':"empty",'a5':"empty",'a6':"empty",'a7':"bp1",'a8':"br1",
    'b1':"wk1",'b2':"wp2",'b3':"empty",'b4':"empty",'b5':"empty",'b6':"empty",'b7':"bp2",'b8':"bk1",
    'c1':"wb1",'c2':"wp3",'c3':"empty",'c4':"empty",'c5':"empty",'c6':"empty",'c7':"bp3",'c8':"bb1",
    'd1':"wq", 'd2':"wp4",'d3':"empty",'d4':"empty",'d5':"empty",'d6':"empty",'d7':"bp4",'d8':"bq",
    'e1':"wk", 'e2':"wp5",'e3':"empty",'e4':"empty",'e5':"empty",'e6':"empty",'e7':"bp5",'e8':"bk",
    'f1':"wb2",'f2':"wp6",'f3':"empty",'f4':"empty",'f5':"empty",'f6':"empty",'f7':"bp6",'f8':"bb2",
    'g1':"wk2",'g2':"wp7",'g3':"empty",'g4':"empty",'g5':"empty",'g6':"empty",'g7':"bp7",'g8':"bk2",
    'h1':"wr2",'h2':"wp8",'h3':"empty",'h4':"empty",'h5':"empty",'h6':"empty",'h7':"bp8",'h8':"br2"
}

pieces = {  ## PIECES
    'wp1':['pawn','a2','white',False, False,{}], 'wp2':['pawn','b2','white',False, False,{}], 'wp3':['pawn','c2','white',False, False,{}], 'wp4':['pawn','d2','white',False,False,{}],
    'wp5':['pawn','e2','white',False,False,{}], 'wp6':['pawn','f2','white',False,False,{}], 'wp7':['pawn','g2','white',False,False,{}], 'wp8':['pawn','h2','white',False,False,{}],
    'wk1':['knight', 'b1', 'white', False, False,{}], 'wk2':['knight','g1','white', False, False,{}],
    'wb1':['bishop', 'c1', 'white', False, False,{}], 'wb2':['bishop', 'f1', 'white', False, False,{}],
    'wr1':['rook', 'a1', 'white', False, False,{}],  'wr2':['rook', 'h1', 'white', False, False,{}],
    'wq':['queen', 'd1', 'white', False, False,{}],
    'wk':['king', 'e1', 'white', False, False,{}],
    'bp1':['pawn','a7','black',False, False,{}], 'bp2':['pawn','b7','black',False, False,{}], 'bp3':['pawn','c7','black',False, False,{}], 'bp4':['pawn','d7','black',False,False,{}],
    'bp5':['pawn','e7','black',False,False,{}], 'bp6':['pawn','f7','black',False,False,{}], 'bp7':['pawn','g7','black',False,False,{}], 'bp8':['pawn','h7','black',False,False,{}],
    'bk1':['knight', 'b8', 'black', False, False,{}], 'bk2':['knight','g8','black', False, False,{}],
    'bb1':['bishop', 'c8', 'black', False, False,{}], 'bb2':['bishop', 'f8', 'black', False, False,{}],
    'br1':['rook', 'a8', 'black', False, False,{}],  'br2':['rook', 'h8', 'black', False, False,{}],
    'bq':['queen', 'd8', 'black', False, False,{}],
    'bk':['king', 'e8', 'black', False, False,{}],
}

# CREATE BOARD SQUARES
for file_idx, f in enumerate('abcdefgh'):
    for rank_idx, r in enumerate('12345678'):
        sq_name = f + r
        sq_color = squareColor1 if (file_idx + rank_idx) % 2 == 0 else squareColor2
        
        exec(f'{sq_name} = turtle.Turtle()')
        exec(f'{sq_name}.penup()')
        exec(f'{sq_name}.shape("square")')
        exec(f'{sq_name}.turtlesize(4)')
        exec(f'{sq_name}.goto({notation[sq_name][0]}, {notation[sq_name][1]})')
        exec(f'{sq_name}.fillcolor("{sq_color}")')
        exec(f'{sq_name}.onclick(lambda x, y, name="{sq_name}": selectSquare(x, y, name))')

# CREATE PIECES
for p in pieces:
    coords = pieces[p][1]
    exec(f'{p} = turtle.Turtle()')
    exec(f'{p}.penup()')
    exec(f'{p}.color("white")' if pieces[p][2] == 'black' else f'{p}.color("black")')
    exec(f'{p}.fillcolor("{pieces[p][2]}")')
    exec(f'{p}.goto({notation[coords][0]}, {notation[coords][1]})')
    exec(f'{p}.onclick(lambda x, y, name="{p}": selectPiece(x, y, name))')
    
    piece_type = pieces[p][0]
    if piece_type == 'pawn':
        exec(f'{p}.shape("turtle")')
        exec(f'{p}.turtlesize(2)')
    else:
        exec(f'{p}.shape("{piece_type}")')
        exec(f'{p}.turtlesize(4)')
    exec(f'{p}.left(90)')

turtle.update()

## BOARD FLIP (Pure symmetry now that (0,0) is true center)
def flip():
    turtle.tracer(0, 0)
    for n in notation:
        notation[n][0] = -notation[n][0]
        notation[n][1] = -notation[n][1]
        exec(f'{n}.goto({notation[n][0]}, {notation[n][1]})')

    for p in pieces:
        sq = pieces[p][1]
        exec(f'{p}.goto({notation[sq][0]}, {notation[sq][1]})')
        
    turtle.update()
    turtle.tracer(1, 0)
    global activeTeam
    activeTeam = 'black' if activeTeam == 'white' else 'white'

## GAMEPLAY AND MOVEMENT
def squareIsAttacked(defendingTeam, square):
    attackerTeam = 'black' if defendingTeam == 'white' else 'white'
    prevTeam = globals()['activeTeam']
    prevSelected = globals()['selectedPiece']

    attacked = False
    globals()['activeTeam'] = attackerTeam

    for p in list(pieces.keys()):
        value = pieces[p]
        if value[2] == attackerTeam:
            globals()['selectedPiece'] = p
            if checkSquare(0, 0, square) == True:
                attacked = True
                break

    globals()['activeTeam'] = prevTeam
    globals()['selectedPiece'] = prevSelected
    return attacked

def kingCheckCheck(targetSquare):
    global selectedPiece
    startSquare = pieces[selectedPiece][1]
    capturedID = piecePositions[targetSquare]
    capturedData = pieces[capturedID].copy() if capturedID != 'empty' else None

    if capturedID != 'empty':
        del pieces[capturedID]

    piecePositions[startSquare] = 'empty'
    piecePositions[targetSquare] = selectedPiece
    pieces[selectedPiece][1] = targetSquare

    inCheck = squareIsAttacked(activeTeam, targetSquare)

    pieces[selectedPiece][1] = startSquare
    piecePositions[startSquare] = selectedPiece
    piecePositions[targetSquare] = capturedID

    if capturedID != 'empty':
        pieces[capturedID] = capturedData

    return inCheck

turtle.tracer(1, 0)

def selectPiece(x, y, piece):
    global selectedPiece
    
    if selectedPiece != None and activeTeam == 'white':
        exec(f'{selectedPiece}.fillcolor("white")')

    if selectedPiece != None and activeTeam == 'black':
        exec(f'{selectedPiece}.fillcolor("black")')
    
    if activeTeam == pieces[piece][2]:
        selectedPiece = piece
        exec(f'{selectedPiece}.fillcolor("#CF6679")')

    if selectedPiece != None:
        if activeTeam != pieces[piece][2] and pieces[selectedPiece][2] == activeTeam:
            targetSquare = pieces[piece][1]
            selectSquare(x=0, y=0, square=targetSquare)

def kingSideCastle():
    global kingSideRook
    kingSideRook = 'wr2' if activeTeam == 'white' else 'br2'
    kingSideDistance = 160 if activeTeam == 'white' else -160
    x = notation[(pieces[kingSideRook][1])][0] - kingSideDistance
    y = notation[(pieces[kingSideRook][1])][1]
    castleTarget = [key for key, value in notation.items() if value == [x,y]]
    result = [key for key, value in piecePositions.items() if value == str(kingSideRook)]
    exec(f'{kingSideRook}.goto({x}, {y})')
    piecePositions.update({str(result[0]): 'empty'})
    piecePositions.update({str(castleTarget[0]): str(kingSideRook)})
    pieces[kingSideRook][1] = castleTarget[0]
    pieces[kingSideRook][4] = True

def queenSideCastle():
    global queenSideRook
    queenSideRook = 'wr1' if activeTeam == 'white' else 'br1'
    queenSideDistance = -240 if activeTeam == 'white' else 240
    x = notation[(pieces[queenSideRook][1])][0] - queenSideDistance
    y = notation[(pieces[queenSideRook][1])][1]
    castleTarget = [key for key, value in notation.items() if value == [x,y]]
    result = [key for key, value in piecePositions.items() if value == str(queenSideRook)]
    exec(f'{queenSideRook}.goto({x}, {y})')
    piecePositions.update({str(result[0]): 'empty'})
    piecePositions.update({str(castleTarget[0]): str(queenSideRook)})
    pieces[queenSideRook][1] = castleTarget[0]
    pieces[queenSideRook][4] = True

def checkSquare(x, y, square):
    global selectedSquare, selectedPiece
    selectedSquare = square
    
    if selectedPiece != None and ((piecePositions[selectedSquare] == 'empty') or pieces[piecePositions[selectedSquare]][2] != activeTeam):
        # PAWN LOGIC
        if piecePositions[selectedSquare] == 'empty':
            if pieces[selectedPiece][0] == 'pawn' and pieces[selectedPiece][2] == activeTeam:
                if enPassantDict[selectedSquare] == True:
                    if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 80 or notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] - 80) and \
                       notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80:
                        return True
                    else:
                        return False

                checkCoord = [notation[(pieces[selectedPiece][1])][0], notation[(pieces[selectedPiece][1])][1] + 160]
                notationResult = [key for key, value in notation.items() if value == checkCoord]
                notationResult = str(notationResult)[2:-2]
                if pieces[selectedPiece][4] == False:
                    if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80 or notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 160)) and piecePositions[notationResult][0] != 'empty':
                        return True
                    else: 
                        return False    
                else:
                    if notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80):
                        return True
                    else: 
                        return False
        
        if piecePositions[selectedSquare] != 'empty':   
            if pieces[piecePositions[selectedSquare]][2] != activeTeam:
                if pieces[selectedPiece][0] == 'pawn':
                    if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 80 or notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] - 80) and \
                       notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80:
                        return True
                    else:
                        return False

        # KNIGHT LOGIC
        if pieces[selectedPiece][0] == 'knight':
            dx = abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0])
            dy = abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])
            if (dx == 80 and dy == 160) or (dx == 160 and dy == 80):
                return True
            else: 
                return False
                
        # BISHOP LOGIC
        if pieces[selectedPiece][0] == 'bishop':
            blocked = False
            if abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]):
                dist = notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]
                trav = abs(dist) / 80 - 1
                xVar = 1 if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0] else -1
                yVar = 1 if notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1] else -1

                for i in range(int(trav)):
                    xPos = i * xVar * 80 + (80 * xVar) + notation[(pieces[selectedPiece][1])][0]
                    yPos = i * yVar * 80 + (80 * yVar) + notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])] != 'empty':
                        blocked = True
                return not blocked
            return False
                
        # ROOK LOGIC
        if pieces[selectedPiece][0] == 'rook':
            blocked = False
            if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and notation[selectedSquare][1] != notation[(pieces[selectedPiece][1])][1]) or \
               (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and notation[selectedSquare][0] != notation[(pieces[selectedPiece][1])][0]):
                dist = (notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) + (notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])
                trav = abs(dist) / 80 - 1
                xVar = 1 if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0] else -1
                yVar = 1 if notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1] else -1

                for i in range(int(trav)):
                    xPos = (i * xVar * 80) + (80 * xVar) + notation[(pieces[selectedPiece][1])][0] if notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0] != 0 else notation[(pieces[selectedPiece][1])][0]
                    yPos = (i * yVar * 80) + (80 * yVar) + notation[(pieces[selectedPiece][1])][1] if notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1] != 0 else notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])] != 'empty':
                        blocked = True
                return not blocked
            return False
        
        # QUEEN LOGIC
        if pieces[selectedPiece][0] == 'queen':
            # Diagonal
            if abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]):
                blocked = False
                dist = notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]
                trav = abs(dist) / 80 - 1
                xVar = 1 if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0] else -1
                yVar = 1 if notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1] else -1

                for i in range(int(trav)):
                    xPos = i * xVar * 80 + (80 * xVar) + notation[(pieces[selectedPiece][1])][0]
                    yPos = i * yVar * 80 + (80 * yVar) + notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])] != 'empty':
                        blocked = True
                if not blocked: return True
                
            # Straight
            if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and notation[selectedSquare][1] != notation[(pieces[selectedPiece][1])][1]) or \
               (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and notation[selectedSquare][0] != notation[(pieces[selectedPiece][1])][0]):
                blocked = False
                dist = (notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) + (notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])
                trav = abs(dist) / 80 - 1
                xVar = 1 if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0] else -1
                yVar = 1 if notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1] else -1

                for i in range(int(trav)):
                    xPos = (i * xVar * 80) + (80 * xVar) + notation[(pieces[selectedPiece][1])][0] if notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0] != 0 else notation[(pieces[selectedPiece][1])][0]
                    yPos = (i * yVar * 80) + (80 * yVar) + notation[(pieces[selectedPiece][1])][1] if notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1] != 0 else notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])] != 'empty':
                        blocked = True
                if not blocked: return True
            return False
                
        # KING LOGIC
        if pieces[selectedPiece][0] == 'king':
            global kingSideRook
            kingSideRook = 'wr2' if activeTeam == 'white' else 'br2'
            kingSideCheck = 'f1' if activeTeam == 'white' else 'f8'
            kingSideDistance = 160 if activeTeam == 'white' else -160
            queenSideRook = 'wr1' if activeTeam == 'white' else 'br1'
            queenSideCheck = ['c1','d1'] if activeTeam == 'white' else ['c8','d8']
            queenSideDistance = -160 if activeTeam == 'white' else 160
            
            dx = abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0])
            dy = abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])

            if (dx <= 80 and dy <= 80) and (dx != 0 or dy != 0):
                if kingCheckCheck(selectedSquare):
                    return False
                return True
            
            elif (pieces[selectedPiece][4] == False and pieces[kingSideRook][4] == False) and \
                 notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + kingSideDistance and \
                 notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and \
                 piecePositions[kingSideCheck] == 'empty':
                return True
            
            elif (pieces[selectedPiece][4] == False and pieces[queenSideRook][4] == False) and \
                 notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + queenSideDistance and \
                 notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and \
                 (piecePositions[queenSideCheck[0]] == 'empty' and piecePositions[queenSideCheck[1]] == 'empty'):
                return True
            else: 
                return False   

# Pre-calculate legal moves
for p in list(pieces.keys()):
    selectedPiece = p
    for n in notation:
        legal = checkSquare(0, 0, n)
        pieces[selectedPiece][5][n] = bool(legal)

selectedPiece = None

def selectSquare(x, y, square):
    global selectedPiece, selectedSquare
    xVar = 160 if activeTeam == 'white' else -160
    selectedSquare = square
    if selectedPiece != None:
        if pieces[selectedPiece][5].get(selectedSquare, False):
            exec(f'{selectedPiece}.fillcolor("white")' if activeTeam == 'white' else f'{selectedPiece}.fillcolor("black")')
            exec(f'{selectedPiece}.goto({notation[selectedSquare][0]}, {notation[selectedSquare][1]})')
            
            if piecePositions[selectedSquare] != 'empty':
                if pieces[piecePositions[selectedSquare]][2] != activeTeam:
                    global capturedPiece
                    capturedPiece = piecePositions[selectedSquare]
                    del pieces[capturedPiece]
                    turtle.tracer(0, 0)
                    exec(f'{capturedPiece}.setpos(1000, 1000)')
                    turtle.update()
                    turtle.tracer(1, 0)
                    capturedPiece = None

            if pieces[selectedPiece][0] == 'king' and notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + xVar:
                kingSideCastle()

            if pieces[selectedPiece][0] == 'king' and notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] - xVar:
                queenSideCastle()

            if pieces[selectedPiece][0] == 'pawn' and piecePositions[selectedSquare] == 'empty' and enPassantDict[selectedSquare] == True:
                dest_file = selectedSquare[0]
                dest_rank = int(selectedSquare[1])
                captured_rank = dest_rank - 1 if activeTeam == 'white' else dest_rank + 1
                captured_sq = dest_file + str(captured_rank)
                captured_id = piecePositions[captured_sq]
                del pieces[captured_id]
                turtle.tracer(0, 0)
                exec(f'{captured_id}.setpos(1000, 1000)')
                turtle.update()
                turtle.tracer(1, 0)
                piecePositions[captured_sq] = 'empty'
            
            for k in enPassantDict:
                enPassantDict[k] = False

            if pieces[selectedPiece][0] == 'pawn' and notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 160:
                dest_file = selectedSquare[0]
                dest_rank = int(selectedSquare[1])
                passed_rank = dest_rank - 1 if activeTeam == 'white' else dest_rank + 1
                enPassantSquare = dest_file + str(passed_rank)
                enPassantDict[enPassantSquare] = True

            result = [key for key, value in piecePositions.items() if value == str(selectedPiece)]
            piecePositions.update({str(result[0]): 'empty'})
            piecePositions.update({str(selectedSquare): str(selectedPiece)})
            pieces[selectedPiece][1] = selectedSquare
            pieces[selectedPiece][4] = True
            
            flip()

        for p in list(pieces.keys()):
            selectedPiece = p
            for n in notation:
                legal = checkSquare(0, 0, n)
                pieces[selectedPiece][5][n] = bool(legal)
        
        whiteKingSquare = pieces['wk'][1]
        whiteInCheck = False
        prevTeam = globals()['activeTeam']

        for p, value in pieces.items():
            if value[2] == 'black':
                globals()['activeTeam'] = 'black'
                selectedPiece = p
                if checkSquare(0, 0, whiteKingSquare) == True:
                    whiteInCheck = True
                    break

        globals()['activeTeam'] = prevTeam
        selectedPiece = None
        
        blackInCheck = False
        blackKingSquare = pieces['bk'][1]

        for p, value in pieces.items():
            if value[2] == 'white':
                globals()['activeTeam'] = 'white'
                selectedPiece = p
                if checkSquare(0, 0, blackKingSquare) == True:
                    blackInCheck = True
                    break

        globals()['activeTeam'] = prevTeam
        selectedPiece = None

        if blackInCheck:
            for _ in range(3):
                exec('bk.fillcolor("#CF6679")')
                turtle.update()
                time.sleep(0.15)
                exec('bk.fillcolor("black")')
                turtle.update()
                time.sleep(0.15)
            exec('bk.fillcolor("#CF6679")')
            print('black in check')

        if whiteInCheck:
            for _ in range(3):
                exec('wk.fillcolor("#CF6679")')
                turtle.update()
                time.sleep(0.15)
                exec('wk.fillcolor("white")')
                turtle.update()
                time.sleep(0.15)
            exec('wk.fillcolor("#CF6679")')
            print('white in check')

turtle.done()