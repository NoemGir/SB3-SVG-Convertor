#!/usr/bin/env python
# coding: utf-8

import fileManipulation as fm;
import patternMatching as pm;
import computeValues as cv;
from blocStructure import Bloc

"""
    blocs a ajouter : 
        - control_stop

    blocs a ajouter ivy :
        - sending_answer
        - sending_askandwait
        - looks_say
        - look_sayforsecs

    blocs a tester :
        -pen_clear
        - si ... alors control_il
        - control_repeat_until
        - control_if_else
"""

draw = False
coordinates = [0, 0]
initCoordinates = [0, 0]
orientation = 0
variables = {}


def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat", "pen_clear",
                     "motion_changeyby", "motion_changexby", "motion_setx", "motion_sety", "control_repeat_until", "data_setvariableto", "data_changevariableby",
                      "control_if", "control_if_else" ]


def generateLine(lettre, x, y):
    return lettre + " " + str(x) + "," + str(y) + "\n"

def moveCase(dico, bloc, orientation):
    global draw
    global coordinates

    distance = getValue(dico, bloc, 0)
    x = cv.compute_X(distance, orientation)
    y = - cv.compute_Y(distance, orientation)
    coordinates[0] += x
    coordinates[1] += y
    if(draw):
        return generateLine("l", x, y)
    else:
        return generateLine("m", x, y)

def set_X(dico, bloc):
    global initCoordinates
    global draw
    global coordinates

    x =  getValue(dico, bloc, 0) + initCoordinates[0]

    coordinates[0] = x
    if(draw):
        return "H" + str(x)
    else:
        return generateLine("M", x, coordinates[1])

def set_Y(dico, bloc):
    global coordinates
    global initCoordinates

    y = initCoordinates[1] -  getValue(dico, bloc, 0)
    coordinates[1] = y
    if(draw):
        return "V" + str(y)
    else:
        return generateLine("M", coordinates[0], y)

def goTo_X_Y(dico, bloc):
    global initCoordinates
    global coordinates

    x = getValue(dico, bloc, 0) + initCoordinates[0]
    y = initCoordinates[1] - getValue(dico, bloc, 1)
    coordinates[0] = x
    coordinates[1] = y
    
    if(draw):
        return generateLine("L", x, y)
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


def setOrientation(value):
    global orientation

    if(value < 0):
        orientation = (-value+90) % 380
    else:
        orientation = (470-value) % 380

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

def blockAnalysis(dico, bloc : Bloc):
    global draw
    global orientation
    global coordinates
    
    addedLines = ""
    if( draw):
        draw = bloc.opcode != "pen_penUp"
    else:
        draw = bloc.opcode == "pen_penDown"
    if(rightBloc(bloc)):
        match bloc.opcode:
            case "motion_movesteps":
                return moveCase(dico, bloc, orientation)
            case "motion_changexby":
                return moveCase(dico, bloc, 0)
            case "motion_changeyby":
                return moveCase(dico, bloc, 90)  
            case "motion_setx":
                return set_X(dico, bloc)
            case "motion_sety":
                return set_Y(dico, bloc)      
            case "motion_gotoxy":
                return goTo_X_Y(dico,  bloc)
            case "motion_turnright":
                modifyOrientation(dico, bloc, True)
            case "motion_turnleft":
                modifyOrientation(dico, bloc, False)
            case "motion_pointindirection":
                setOrientation(getValue(dico, bloc, 0))
            case "control_repeat":
                return controlRepeat(dico, bloc)
            case "control_repeat_until":
                return controlRepeatUntil(dico, bloc)
            case "control_if_else":
                return controlIfElse(dico, bloc)
            case "control_if":
                return controlIf(dico, bloc)
            case "data_setvariableto":
                variables.update([(bloc.fields[0], getValue(dico, bloc, 0))])
            case "data_changevariableby":
                changeVariable(dico, bloc)
                
    return addedLines

def sequenceLoop(dico, bloc : Bloc):
    blocsParcourus = False
    addedLines = ""
    while(not blocsParcourus):
        if(bloc.opcode != "pen_clear"):
            addedLines += blockAnalysis(dico, bloc)
        else:
            addedLines = ""
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
        addedLines += sequenceLoop(dico, dico[first])

    fm.insertLinesRVG(addedLines)

def on_tabgo():
    fm.extractSB3("../sb3/Programme_scratch.sb3")
    generateNewLines()

def on_sb3():
    fm.extractSB3("Programme_scratch.sb3")
    generateNewLines()

def on_json():
    generateNewLines()

on_sb3()







