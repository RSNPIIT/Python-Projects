import turtle
turtle.tracer(0,0)
import time

s = turtle.Screen()
s.title('chess')
s.register_shape('king',  ((-5,-8),(5,-8),(5,-3),(4,-2),(4,0),(2,1),(2,6),(4,6),(4,7),(2,7),(2,9),(-2,9),(-2,7),(-4,7),(-4,6),(-2,6),(-2,1),(-4,0),(-4,-2),(-5,-3),(-5,-8)))
s.register_shape('queen', ((-5,-8),(5,-8),(5,-3),(4,-2),(4,0),(2,1),(2,5),(3,6),(4,5),(5,6),(5,7),(3,8),(1,7),(0,8),(-1,7),(-3,8),(-5,7),(-5,6),(-4,5),(-3,6),(-2,5),(-2,1),(-4,0),(-4,-2),(-5,-3),(-5,-8)))
s.register_shape('bishop',((0,7),(1,6),(2,5),(1,4),(2,3),(1,2),(3,1),(4,0),(3,-1),(3,-3),(4,-4),(4,-8),(-4,-8),(-4,-4),(-3,-3),(-3,-1),(-4,0),(-3,1),(-1,2),(-2,3),(-1,4),(-2,5),(-1,6),(0,7)))
s.register_shape('knight',((-5,-8),(5,-8),(5,-3),(1,-3),(4,1),(1,5),(-2,4),(-2,0),(-5,0),(-5,-8)))
s.register_shape('rook', ((-4,4),(4,4),(4,2),(3,1),(3,-2),(5,-6),(5,-8),(-5,-8),(-5,-6),(-3,-2),(-3,1),(-4,2),(-4,4)))
s.register_shape('pawn',((0,6),(1,6),(2,5),(2,4),(2,2),(1,1),(2,0),(2,-2),(3,-3),(4,-6),(3,-7),(0,-7),(-3,-7),(-4,-6),(-3,-3),(-2,-2),(-2,0),(-1,1),(-2,2),(-2,4),(-2,5),(-1,6),(0,6)))


backgroundColor = '#404040'
squareColor1 = '#18242b'
squareColor2 = '#84c9FB'
loopCount = 0
selectedPiece = None
selectedSquare = None
activeTeam = 'white'
capturedPiece = None
turtle.bgcolor(backgroundColor)

notation = { ##CHESS NOTATION COORDINATE DICTIONARY
    'a1':[-295, -260],'a2':[-295, -180],'a3':[-295, -100],'a4':[-295, -20],'a4':[-295, -20],'a5':[-295, 60],'a6':[-295, 140],'a7':[-295, 220],'a8':[-295, 300],
    'b1':[-215, -260],'b2':[-215, -180],'b3':[-215, -100],'b4':[-215, -20],'b4':[-215, -20],'b5':[-215, 60],'b6':[-215, 140],'b7':[-215, 220],'b8':[-215, 300],
    'c1':[-135, -260],'c2':[-135, -180],'c3':[-135, -100],'c4':[-135, -20],'c4':[-135, -20],'c5':[-135, 60],'c6':[-135, 140],'c7':[-135, 220],'c8':[-135, 300],
    'd1':[-55, -260],'d2':[-55, -180],'d3':[-55, -100],'d4':[-55, -20],'d4':[-55, -20],'d5':[-55, 60],'d6':[-55, 140],'d7':[-55, 220],'d8':[-55, 300],
    'e1':[25, -260],'e2':[25, -180],'e3':[25, -100],'e4':[25, -20],'e4':[25, -20],'e5':[25, 60],'e6':[25, 140],'e7':[25, 220],'e8':[25, 300],
    'f1':[105, -260],'f2':[105, -180],'f3':[105, -100],'f4':[105, -20],'f4':[105, -20],'f5':[105, 60],'f6':[105, 140],'f7':[105, 220],'f8':[105, 300],
    'g1':[185, -260],'g2':[185, -180],'g3':[185, -100],'g4':[185, -20],'g4':[185, -20],'g5':[185, 60],'g6':[185, 140],'g7':[185, 220],'g8':[185, 300],
    'h1':[265, -260],'h2':[265, -180],'h3':[265, -100],'h4':[265, -20],'h4':[265, -20],'h5':[265, 60],'h6':[265, 140],'h7':[265, 220],'h8':[265, 300],
    }

enPassantDict = notation.copy()
for e in enPassantDict:
    enPassantDict[e] = False

piecePositions = { ##PIECE POSTIONS
    'a1':"wr1",'a2':"wp1",'a3':"empty",'a4':"empty",'a4':"empty",'a5':"empty",'a6':"empty",'a7':"bp1",'a8':"br1",
    'b1':"wk1",'b2':"wp2",'b3':"empty",'b4':"empty",'b4':"empty",'b5':"empty",'b6':"empty",'b7':"bp2",'b8':"bk1",
    'c1':"wb1",'c2':"wp3",'c3':"empty",'c4':"empty",'c4':"empty",'c5':"empty",'c6':"empty",'c7':"bp3",'c8':"bb1",
    'd1':"wq",'d2':"wp4",'d3':"empty",'d4':"empty",'d4':"empty",'d5':"empty",'d6':"empty",'d7':"bp4",'d8':"bq",
    'e1':"wk",'e2':"wp5",'e3':"empty",'e4':"empty",'e4':"empty",'e5':"empty",'e6':"empty",'e7':"bp5",'e8':"bk",
    'f1':"wb2",'f2':"wp6",'f3':"empty",'f4':"empty",'f4':"empty",'f5':"empty",'f6':"empty",'f7':"bp6",'f8':"bb2",
    'g1':"wk2",'g2':"wp7",'g3':"empty",'g4':"empty",'g4':"empty",'g5':"empty",'g6':"empty",'g7':"bp7",'g8':"bk2",
    'h1':"wr2",'h2':"wp8",'h3':"empty",'h4':"empty",'h4':"empty",'h5':"empty",'h6':"empty",'h7':"bp8",'h8':"br2"
    }

pieces = {  ##PIECES
    'wp1':['pawn','a2','white',False, False,{}], 'wp2':['pawn','b2','white',False, False,{}], 'wp3':['pawn','c2','white',False, False,{}], 'wp4':['pawn','d2','white',False,False,{}], 'wp5':['pawn','e2','white',False,False,{}], 'wp6':['pawn','f2','white',False,False,{}], 'wp7':['pawn','g2','white',False,False,{}], 'wp8':['pawn','h2','white',False,False,{}],
    'wk1':['knight', 'b1', 'white', False, False,{}], 'wk2':['knight','g1','white', False, False,{}],
    'wb1':['bishop', 'c1', 'white', False, False,{}], 'wb2':['bishop', 'f1', 'white', False, False,{}],
    'wr1':['rook', 'a1', 'white', False, False,{}],'wr2':['rook', 'h1', 'white', False, False,{}],
    'wq':['queen', 'd1', 'white', False, False,{}],
    'wk':['king', 'e1', 'white', False, False,{}],
    'bp1':['pawn','a7','black',False, False,{}], 'bp2':['pawn','b7','black',False, False,{}], 'bp3':['pawn','c7','black',False, False,{}], 'bp4':['pawn','d7','black',False,False,{}], 'bp5':['pawn','e7','black',False,False,{}], 'bp6':['pawn','f7','black',False,False,{}], 'bp7':['pawn','g7','black',False,False,{}], 'bp8':['pawn','h7','black',False,False,{}],
    'bk1':['knight', 'b8', 'black', False, False,{}], 'bk2':['knight','g8','black', False, False,{}],
    'bb1':['bishop', 'c8', 'black', False, False,{}], 'bb2':['bishop', 'f8', 'black', False, False,{}],
    'br1':['rook', 'a8', 'black', False, False,{}],'br2':['rook', 'h8', 'black', False, False,{}],
    'bq':['queen', 'd8', 'black', False, False,{}],
    'bk':['king', 'e8', 'black', False, False,{}],
}

for n in notation: ##CREATE BOARD SQUARE TURTLES
    loopCount = loopCount + 1
    if loopCount % 9 == 0:
        loopCount = loopCount + 1
    if loopCount % 2:
        coords = str(notation[n])
        coords = coords[1:-1]
        exec(str(n)+'= turtle.Turtle()')
        exec(str(n) + '.penup()')
        exec(str(n) + '.shape' + '("' + 'square' + '")')
        exec(str(n) + '.turtlesize' + '(4)')
        exec(str(n)+'.goto'+'(' +coords + ')')
        exec(str(n)+'.fillcolor('+'"'+squareColor1+'")')
        exec(str(n) + '.onclick(lambda x, y: selectSquare(x, y, "' + str(n) + '"))')
    else:
        coords = str(notation[n])
        coords = coords[1:-1]
        exec(str(n)+'= turtle.Turtle()')
        exec(str(n) + '.penup()')
        exec(str(n) + '.shape' + '("' + 'square' + '")')
        exec(str(n) + '.turtlesize' + '(4)')
        exec(str(n)+'.goto'+'(' +coords + ')')
        exec(str(n)+'.fillcolor('+'"'+squareColor2+'")')
        exec(str(n) + '.onclick(lambda x, y: selectSquare(x, y, "' + str(n) + '"))')

for p in pieces: ## CREATE PIECES FROM PIECES DICTIONARY
    coords = pieces[p][1]
    exec(str(p)+'= turtle.Turtle()')
    exec(str(p) + '.penup()')
    exec(str(p)+'.color("white")') if pieces[p][2] == 'black' else exec(str(p)+'.color("black")')
    exec(str(p)+'.fillcolor('+'"'+str(pieces[p][2])+'")')
    exec(str(p)+'.goto'+'(' + str(notation[str(coords)]) + ')')
    exec(str(p) + '.onclick(lambda x, y: selectPiece(x, y, "' + str(p) + '"))')
    if pieces[p][0] == 'pawn':
        exec(str(p) + '.shape' + '("' + 'turtle' + '")')
        exec(str(p) + '.turtlesize' + '(2)')
        exec(str(p) + '.left(90)')

    if pieces[p][0] == 'knight':
        exec(str(p) + '.shape' + '("' + 'knight' + '")')
        exec(str(p) + '.turtlesize' + '(4)')
        exec(str(p) + '.left(90)')

    if pieces[p][0] == 'bishop':
        exec(str(p) + '.shape' + '("' + 'bishop' + '")')
        exec(str(p) + '.turtlesize' + '(4)')
        exec(str(p) + '.left(90)')
    
    if pieces[p][0] == 'rook':
        exec(str(p) + '.shape' + '("' + 'rook' + '")')
        exec(str(p) + '.turtlesize' + '(4)')
        exec(str(p) + '.left(90)')

    if pieces[p][0] == 'queen':
        exec(str(p) + '.shape' + '("' + 'queen' + '")')
        exec(str(p) + '.turtlesize' + '(4)')
        exec(str(p) + '.left(90)')

    if pieces[p][0] == 'king':
        exec(str(p) + '.shape' + '("' + 'king' + '")')
        exec(str(p) + '.turtlesize' + '(4)')
        exec(str(p) + '.left(90)')

##BOARD FLIP

def flip():
    turtle.tracer(0,0)
    for n in notation:
        x = notation[n][0]
        y = notation[n][1]
        notation[n][0] = (x * -1) - 30
        notation[n][1] = (y * -1) + 40
        coords = str(notation[n])
        exec(str(n)+'.goto'+'(' +coords + ')')

    for p in pieces:
        coords = str(notation[(pieces[p][1])])
        exec(str(p)+'.goto'+'(' +coords + ')')
    turtle.tracer(1,0)
    global activeTeam
    activeTeam = 'black' if activeTeam =='white' else 'white'
    

## GAMEPLAY AND MOVEMENT

def squareIsAttacked(defendingTeam, square): ##CHECK IF SQUARE IS ATTACKED
    attackerTeam = 'black' if defendingTeam == 'white' else 'white'

    prevTeam = globals()['activeTeam']
    prevSelected=globals()['selectedPiece']

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
    
turtle.tracer(1,0)

def selectPiece(x,y, piece): ##SELECTED PIECE LOGIC
    global selectedPiece
    
    if selectedPiece != None and activeTeam == 'white':
        exec(selectedPiece + '.fillcolor("' + 'white' +'")')

    if selectedPiece != None and activeTeam == 'black':
            exec(selectedPiece + '.fillcolor("' + 'black' +'")')
    
    if activeTeam == pieces[piece][2]:
        selectedPiece = piece
        exec(selectedPiece + '.fillcolor("' + '#CF6679' +'")')

    if selectedPiece != None:
        if activeTeam != pieces[piece][2] and pieces[selectedPiece][2] == activeTeam:
            targetSquare = pieces[piece][1]
            selectSquare(x=0,y=0,square=targetSquare)

def kingSideCastle(): ## KINGSIDE CASTLE
    global kingSideRook
    kingSideRook = 'wr2' if activeTeam == 'white' else 'br2'
    kingSideDistance = 160 if activeTeam == 'white' else -160
    x = notation[(pieces[kingSideRook][1])][0] - kingSideDistance
    y = notation[(pieces[kingSideRook][1])][1]
    castleTarget = [key for key, value in notation.items() if value == [x,y]]
    result = [key for key, value in piecePositions.items() if value == str(kingSideRook)]
    exec(str(kingSideRook) + f'.goto({x},{y})')
    piecePositions.update({str(result[0]):'empty'})
    piecePositions.update({str(castleTarget[0]):str(kingSideRook)})
    pieces[kingSideRook][1] = castleTarget[0]
    pieces[kingSideRook][4] = True
    

def queenSideCastle(): ##QUEENSIDE CASTLE
    global queenSideRook
    queenSideRook = 'wr1' if activeTeam == 'white' else 'br1'
    queenSideDistance = -240 if activeTeam == 'white' else 240
    x = notation[(pieces[queenSideRook][1])][0] - queenSideDistance
    y = notation[(pieces[queenSideRook][1])][1]
    castleTarget = [key for key, value in notation.items() if value == [x,y]]
    result = [key for key, value in piecePositions.items() if value == str(queenSideRook)]
    exec(str(queenSideRook) + f'.goto({x},{y})')
    piecePositions.update({str(result[0]):'empty'})
    piecePositions.update({str(castleTarget[0]):str(queenSideRook)})
    pieces[queenSideRook][1] = castleTarget[0]
    pieces[queenSideRook][4] = True

def checkSquare(x,y, square): ## MOVE TO SQUARE LOGIC
    global selectedSquare
    global selectedPiece
    selectedSquare = square
    
    if selectedPiece != None and ((piecePositions[selectedSquare] == 'empty') or pieces[piecePositions[selectedSquare]][2] != activeTeam): ##CHECK IF PIECE IS SELECTED AND SELECTED SQUARE IS EMPTY
        ##PAWN LOGIC
        if piecePositions[selectedSquare] == 'empty':
            if pieces[selectedPiece][0] == 'pawn' and pieces[selectedPiece][2] == activeTeam:

                if enPassantDict[selectedSquare] == True:
                    if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 80 \
                        or notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] - 80) and \
                    notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80:
                        return True
                    else:
                        return False

                checkCoord = [(notation[(pieces[selectedPiece][1])][0]), (notation[(pieces[selectedPiece][1])][1] + 160)]
                notationResult = [key for key, value in notation.items() if value == checkCoord]
                notationResult = str(notationResult)[2:-2]
                if pieces[selectedPiece][4] == False:
                    if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 80 or notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] + 160))\
                        and piecePositions[notationResult][0] != 'empty':
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
                        return

                
        ##KNIGHT LOGIC
        if pieces[selectedPiece][0] == 'knight':
            if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 80 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] +160)) \
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 160 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] +80))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 160 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] -80))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + 80 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] -160))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] -80 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] -160))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] -160 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] -80))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] -160 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] +80))\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] -80 and (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] +160)):
                return True
            else: 
                return False
                
        ##BISHOP LOGIC
        if pieces[selectedPiece][0] == 'bishop':
            blocked = False
            if abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]):
                dist = notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]
                trav = abs(dist) / 80 - 1

                if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0]:
                    xVar = 1
                else:
                    xVar = -1
                
                if (notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1]):
                    yVar = 1 
                else:
                    yVar = -1

                for i in range(int(trav)):
                    xPos = i * xVar * 80 + (80 * xVar) + notation[(pieces[selectedPiece][1])][0]
                    yPos = i * yVar * 80 + (80 * yVar) + notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])]!='empty':
                        blocked = True
                
                if not blocked:                
                    return True
                else: 
                    return False
                
        ##ROOK LOGIC
        if pieces[selectedPiece][0] == 'rook':
            blocked = False
            if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and notation[selectedSquare][1] != notation[(pieces[selectedPiece][1])][1]) \
                or (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and notation[selectedSquare][0] != notation[(pieces[selectedPiece][1])][0]):
                dist = (notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) + (notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])
                trav = abs(dist) / 80 - 1
                
                if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0]:
                    xVar = 1
                else:
                    xVar = -1
                
                if (notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1]):
                    yVar = 1 
                else:
                    yVar = -1

                for i in range(int(trav)):
                    xPos = (i * xVar * 80) + (80 * xVar) + notation[(pieces[selectedPiece][1])][0] if notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0] != 0 else notation[(pieces[selectedPiece][1])][0]
                    yPos = (i * yVar * 80) + (80 * yVar) + notation[(pieces[selectedPiece][1])][1] if notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1] != 0 else notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])]!='empty':
                        blocked = True
                
                if not blocked:                
                    return True
                else: 
                    return False
        
        ##QUEEN LOGIC
        if pieces[selectedPiece][0] == 'queen':
            if abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]):
                blocked = False
                dist = notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]
                trav = abs(dist) / 80 - 1

                if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0]:
                    xVar = 1
                else:
                    xVar = -1
                
                if (notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1]):
                    yVar = 1 
                else:
                    yVar = -1

                for i in range(int(trav)):
                    xPos = i * xVar * 80 + (80 * xVar) + notation[(pieces[selectedPiece][1])][0]
                    yPos = i * yVar * 80 + (80 * yVar) + notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])]!='empty':
                        blocked = True
                    
                
                
                if not blocked:                
                    return True
                else: 
                    return False
                
            if (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] and notation[selectedSquare][1] != notation[(pieces[selectedPiece][1])][1]) \
                or (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1] and notation[selectedSquare][0] != notation[(pieces[selectedPiece][1])][0]):
                blocked = False
                dist = (notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) + (notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1])
                trav = abs(dist) / 80 - 1
                
                if notation[selectedSquare][0] > notation[(pieces[selectedPiece][1])][0]:
                    xVar = 1
                else:
                    xVar = -1
                
                if (notation[selectedSquare][1] > notation[(pieces[selectedPiece][1])][1]):
                    yVar = 1 
                else:
                    yVar = -1

                for i in range(int(trav)):
                    xPos = (i * xVar * 80) + (80 * xVar) + notation[(pieces[selectedPiece][1])][0] if notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0] != 0 else notation[(pieces[selectedPiece][1])][0]
                    yPos = (i * yVar * 80) + (80 * yVar) + notation[(pieces[selectedPiece][1])][1] if notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1] != 0 else notation[(pieces[selectedPiece][1])][1]
                    checkCoord = [xPos, yPos]
                    notationResult = [key for key, value in notation.items() if value == checkCoord]
                    if piecePositions[str(notationResult[0])]!='empty':
                        blocked = True
                
                if not blocked:                
                    return True
                else: 
                    return False
                
        ##KING LOGIC
        if pieces[selectedPiece][0] == 'king':
            global kingSideRook
            kingSideRook = 'wr2' if activeTeam == 'white' else 'br2'
            kingSideCheck = 'f1' if activeTeam == 'white' else 'f8'
            kingSideDistance = 160 if activeTeam =='white' else -160
            queenSideRook = 'wr1' if activeTeam == 'white' else 'br1'
            queenSideCheck = ['c1','d1'] if activeTeam == 'white' else ['c8','d8']
            queenSideDistance = -160 if activeTeam =='white' else 160
            
            if (abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == 80 or 0) and abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]) == 80 or 0\
            or (notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0]) and (abs(notation[selectedSquare][1] - notation[(pieces[selectedPiece][1])][1]) == 80) \
            or (notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1]) and (abs(notation[selectedSquare][0] - notation[(pieces[selectedPiece][1])][0]) == 80):
                if kingCheckCheck(selectedSquare):
                        return False
                return True
            
            elif ((pieces[selectedPiece][4] == False and pieces[kingSideRook][4] == False) and notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + kingSideDistance)\
                and notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1]\
                and piecePositions[kingSideCheck] == 'empty':
                return True
            
            elif ((pieces[selectedPiece][4] == False and pieces[queenSideRook][4] == False) and notation[selectedSquare][0] == notation[(pieces[selectedPiece][1])][0] + queenSideDistance)\
                and notation[selectedSquare][1] == notation[(pieces[selectedPiece][1])][1]\
                and (piecePositions[queenSideCheck[0]] == 'empty' and piecePositions[queenSideCheck[1]] == 'empty'):
                return True
            
            else: 
                return False   
            
for p in list(pieces.keys()):
    selectedPiece = p
    for n in notation:
        legal = checkSquare(0, 0, n)
        if legal == None:
            legal = False
        pieces[selectedPiece][5][n] = legal

selectedPiece = None

def selectSquare(x,y, square):
    global selectedPiece
    global selectedSquare
    global triggerKingSideCastle
    xVar = 160 if activeTeam == 'white' else -160
    selectedSquare = square
    if selectedPiece != None:
        if pieces[selectedPiece][5][selectedSquare]:
            exec(selectedPiece + '.fillcolor("' + 'white' +'")') if activeTeam == 'white' else  exec(selectedPiece + '.fillcolor("' + 'black' +'")')
            exec(selectedPiece + '.goto(' + 'notation["'+selectedSquare+'"])')
            if piecePositions[selectedSquare] != 'empty':
                if pieces[piecePositions[selectedSquare]][2] != activeTeam:
                    global capturedPiece
                    capturedPiece = [piecePositions[selectedSquare]]
                    del pieces[str(capturedPiece)[2:-2]]
                    turtle.tracer(0,0)
                    exec(str(capturedPiece)[2:-2] + '.setpos(1000,1000)')
                    turtle.tracer(1,0)
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
                turtle.tracer(0,0)
                exec(captured_id + '.setpos(1000,1000)')
                turtle.tracer(1,0)
                piecePositions[captured_sq] = 'empty'
            
            for k in enPassantDict:
                enPassantDict[k] = False

            if pieces[selectedPiece][0] == 'pawn' and notation[selectedSquare][1] == \
               notation[(pieces[selectedPiece][1])][1] + 160:
                dest_file = selectedSquare[0]
                dest_rank = int(selectedSquare[1])
                passed_rank = dest_rank - 1 if activeTeam == 'white' else dest_rank + 1
                enPassantSquare = dest_file + str(passed_rank)
                enPassantDict[enPassantSquare] = True


            result = [key for key, value in piecePositions.items() if value == str(selectedPiece)]
            piecePositions.update({str(result[0]):'empty'})
            piecePositions.update({str(selectedSquare):str(selectedPiece)})
            pieces[selectedPiece][1] = selectedSquare
            pieces[selectedPiece][4] = True
            
            flip()

        for p in list(pieces.keys()):
            selectedPiece = p
            for n in notation:
                legal = checkSquare(0, 0, n)
                if legal == None:
                    legal = False
                pieces[selectedPiece][5][n] = legal
        
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
        prevTeam = globals()['activeTeam']
        
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
            exec ('bk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('bk.fillcolor("black")')
            time.sleep(.25)
            exec ('bk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('bk.fillcolor("black")')
            time.sleep(.25)
            exec ('bk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('bk.fillcolor("black")')
            time.sleep(.25)
            exec ('bk.fillcolor("#CF6679")')
            print('black in check')

        if whiteInCheck:
            exec ('wk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('wk.fillcolor("white")')
            time.sleep(.25)
            exec ('wk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('wk.fillcolor("white")')
            time.sleep(.25)
            exec ('wk.fillcolor("#CF6679")')
            time.sleep(.25)
            exec ('wk.fillcolor("white")')
            time.sleep(.25)
            exec ('wk.fillcolor("#CF6679")')
            print('white in check')
        

turtle.done()
