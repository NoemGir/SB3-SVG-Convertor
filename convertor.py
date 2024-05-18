#!/usr/bin/env python
# coding: utf-8

import fileManipulation as fm;
import patternMatching as pm;
import computeValues as cv;
from blocStructure import Bloc

"""
    blocs a tester :
        -pen_clear
"""

draw = False

coordinates = [0, 0]
initCoordinates = [0, 0]
orientation = 0
variables = {}

scale = 1
color = False
orientationLastMovement = 0
isNewMovement = False
hasMoved = False

def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat", "pen_clear",
                     "motion_changeyby", "motion_changexby", "motion_setx", "motion_sety", "control_repeat_until", "data_setvariableto", "data_changevariableby",
                      "control_if", "control_if_else" ]


def generateLine(lettre, x, y):
    return lettre + " " + str(x) + "," + str(y) + " "


def moveCase(dico, bloc, orientation):
    global orientationLastMovement
    global isNewMovement
    global hasMoved

    addedLine = ""
    orientationLastMovement = orientation
    distance = getValue(dico, bloc, 0)*scale

    if(color and isNewMovement):
        addedLine = drawColorStartLine()
        distance -= 28
        isNewMovement = False

    x = cv.compute_X(distance, orientation)
    y = (- cv.compute_Y(distance, orientation))

    coordinates[0] += x
    coordinates[1] += y

    if(draw):
        hasMoved = True
        return addedLine + generateLine("l", x, y)
    else:
        return generateLine("m", x, y)


def set_X(dico, bloc):
    global orientationLastMovement
    global isNewMovement
    global hasMoved

    newLine = ""

    x =  (getValue(dico, bloc, 0)*scale + initCoordinates[0])

    orientationLastMovement = cv.computeOrientation(coordinates, [x,coordinates[1]])
    if(color and isNewMovement):
        newLine = drawColorStartLine()
        isNewMovement = False

    coordinates[0] = x
    
    if(draw):
        hasMoved = True
        return newLine + "H " + str(x)
    else:
        return generateLine("M", x, coordinates[1])

def set_Y(dico, bloc):
    global orientationLastMovement
    global isNewMovement
    global hasMoved
    newLine = ""

    y = (initCoordinates[1] -  getValue(dico, bloc, 0)*scale)

    orientationLastMovement = cv.computeOrientation(coordinates, [coordinates[0],y])
    if(color and isNewMovement):
        newLine = drawColorStartLine()
        isNewMovement = False
        
    coordinates[1] = y

    if(draw):
        hasMoved = True
        return newLine + "V " + str(y)
    else:
        return generateLine("M", coordinates[0], y)


def goTo_X_Y(dico, bloc):
    global orientationLastMovement
    global isNewMovement
    global hasMoved
    
    newLine = ""

    x = (getValue(dico, bloc, 0)*scale + initCoordinates[0])
    y = (initCoordinates[1] - getValue(dico, bloc, 1)*scale)

    orientationLastMovement = cv.computeOrientation(coordinates, [x,y])
    if(color and isNewMovement):
        newLine = drawColorStartLine()
        isNewMovement = False
    
    coordinates[0] = x
    coordinates[1] = y
    
    if(draw):
        hasMoved = True
        return newLine + generateLine("L", x, y)
    else:
        return generateLine("M", x, y)


def modifyOrientation(dico, bloc, droite):
    global orientation

    degree = getValue(dico, bloc, 0)
    if(droite):
        orientation -= degree
    else:
        orientation += degree
    orientation = orientation  % 360


def getValue(dico, bloc, id):
    return cv.getValue(dico, bloc, id, variables, initCoordinates, coordinates, orientation)

def inEdge():
    global coordinates
    global initCoordinates

    return 0 < coordinates[0] < coordinates[0]*2 and 0 < coordinates[1] < coordinates[1]*2

def condition(dico, bloc : Bloc):
    match bloc.opcode: 
        case "operator_or":
            return condition(dico, dico[bloc.inputs[0]]) or condition(dico, dico[bloc.inputs[1]])
        case "operator_and":
            return condition(dico, dico[bloc.inputs[0]]) and condition(dico, dico[bloc.inputs[1]])
        case "operator_not":
            return not condition(dico, dico[bloc.inputs[0]])
        case "operator_equals":
            return getValue(dico, bloc, 0) == getValue(dico, bloc, 1)
        case "operator_gt":
            return getValue(dico, bloc, 0) > getValue(dico, bloc, 1)
        case "operator_lt":
            return getValue(dico, bloc, 0) < getValue(dico, bloc, 1)
        case "sensing_touchingobject":
            return not inEdge()
    print("condition: not in match case : " + bloc.opcode)
    return False

def controlRepeat(dico, bloc : Bloc):
    addedLines = ""
    for i in range (getValue(dico, bloc, 0)):
        addedLines +=  sequenceLoop(dico, dico[ bloc.inputs[1]] )
    return addedLines

def controlRepeatUntil(dico, bloc : Bloc):
    addedLines = ""
    while(not condition(dico, dico[bloc.inputs[1]]) ):
        addedLines +=  sequenceLoop(dico, dico[bloc.inputs[0]] )
    return addedLines

def controlIfElse(dico, bloc : Bloc):
    addedLines = ""
    if(condition(dico, dico[bloc.inputs[2]])):
        addedLines +=  sequenceLoop(dico, dico[bloc.inputs[0]] )
    else:
        addedLines +=  sequenceLoop(dico, dico[bloc.inputs[1]] )
    return addedLines

def controlIf( dico, bloc : Bloc):
    addedLines = ""
    if(condition(dico, dico[bloc.inputs[1]])):
        addedLines +=  sequenceLoop(dico, dico[bloc.inputs[0]] )
    return addedLines

def changeVariable(dico, bloc : Bloc):
    global variables 

    if(bloc.fields[0] in variables):
        value = variables[bloc.fields[0]]
        variables.update([(bloc.fields[0], value + getValue(dico, bloc, 0))])
    else:
        variables.update([(bloc.fields[0], getValue(dico, bloc, 0))])
    
def drawColors(orient):
    if(color):
        addedLines = fm.putColor(coordinates, "red")
        x = cv.compute_X(14, orient)
        y = (- cv.compute_Y(14, orient))

        addedLines += generateLine("l", x, y)
        addedLines += fm.putColor([coordinates[0] + x, coordinates[1] + y], "blue")
        addedLines += generateLine("l", x, y)

        return [addedLines, 2*x, 2*y]
    return ""

def drawColorEndLine():
    if(color and hasMoved):
        tempOrientation = (orientationLastMovement + 180) % 360
        addedLines = drawColors(tempOrientation)[0]
        return addedLines + fm.putColor(coordinates, "black")
    return ""


def drawColorStartLine():
    linesColors = drawColors(orientationLastMovement)
    addedLines = linesColors[0]
    
    coordinates[0] += linesColors[1]
    coordinates[1] += linesColors[2]
    return addedLines + fm.putColor(coordinates, "black")


def blockAnalysis(dico, bloc : Bloc):
    global draw
    global orientation
    global coordinates
    global isNewMovement
    global hasMoved

    addedLines = ""
    if( draw):
        draw = bloc.opcode != "pen_penUp"
        if(not draw):
           if(hasMoved):
                addedLines = drawColorEndLine()
           isNewMovement = False
           hasMoved = False
    else:
        draw = bloc.opcode == "pen_penDown"
        if(draw):
            hasMoved = False
            isNewMovement = True

    if(rightBloc(bloc)):
        match bloc.opcode:
            case "motion_movesteps":
                return addedLines + moveCase(dico, bloc, orientation)
            case "motion_changexby":
                return addedLines + moveCase(dico, bloc, 0)
            case "motion_changeyby":
                return addedLines + moveCase(dico, bloc, 90)  
            case "motion_setx":
                return addedLines + set_X(dico, bloc)
            case "motion_sety":
                return addedLines + set_Y(dico, bloc)      
            case "motion_gotoxy":
                return addedLines + goTo_X_Y(dico,  bloc)
            case "motion_turnright":
                modifyOrientation(dico, bloc, True)
            case "motion_turnleft":
                modifyOrientation(dico, bloc, False)
            case "motion_pointindirection":
                orientation = cv.convertOrientation(getValue(dico, bloc, 0))
            case "control_repeat":
                return addedLines + controlRepeat(dico, bloc)
            case "control_repeat_until":
                return addedLines + controlRepeatUntil(dico, bloc)
            case "control_if_else":
                return addedLines + controlIfElse(dico, bloc)
            case "control_if":
                return addedLines + controlIf(dico, bloc)
            case "data_setvariableto":
                variables.update([(bloc.fields[0], getValue(dico, bloc, 0))])
            case "data_changevariableby":
                changeVariable(dico, bloc)
                
    return addedLines

def sequenceLoop(dico, bloc : Bloc):
    blocsParcourus = False
    addedLines = ""
    while(not blocsParcourus):
        
        addedLines += blockAnalysis(dico, bloc)

        if (bloc.next in dico):
                bloc = dico[bloc.next]
        else:
            blocsParcourus = True
    return addedLines


def generateNewLines():
    global initCoordinates
    global coordinates

    initCoordinates = fm.getInitialCoordinate()
    coordinates = [coord for coord in initCoordinates]

    JsonReader = fm.JSONreader()
    first_blocks = JsonReader[0]
    dico = JsonReader[1]

    addedLines = generateLine("M", initCoordinates[0], initCoordinates[1])

    for first in first_blocks:
        addedLines += sequenceLoop(dico, dico[first]) + drawColorEndLine()

    fm.insertLinesRVG(addedLines)

def on_tabgo():
    fm.extractSB3("../sb3/Programme_scratch.sb3")
    generateNewLines()

def on_sb3():
    fm.extractSB3("Programme_scratch.sb3")
    generateNewLines()

def on_json():
    generateNewLines()

def printable():
    global scale
    global color 
    global isNewMovement
    isNewMovement = False
    color = True
    scale = 1.4
    on_sb3()
    fm.addBigStroke()
    fm.transform(0, 0)

printable()
#on_sb3()
