#!/usr/bin/env python
# coding: utf-8

import math 
from blocStructure import Bloc

def compute_X(distance, orientation):
    """compute the x coordinate after moving in the distance and orientation given"""
    sign = 1
    if( 0 <= orientation < 90 or 180 <= orientation < 270):
        b = 90 - (orientation % 90)
    else: 
        b = orientation % 90
    
    if (90 < orientation < 270):
        sign = -1
    b = math.radians(b)
    return math.sin(b) * distance * sign


def compute_Y(distance, orientation):
    """compute the y coordinate after moving in the distance and orientation given"""
    sign = 1
    if( 0 <= orientation < 90 or 180 <= orientation < 270):
        b = orientation % 90
    else: 
        b = 90- (orientation % 90)

    if (180 < orientation < 360):
        sign = -1
    b = math.radians(b)
    return math.sin(b) * distance * sign

def computeOrientation(initialCoord, finalCoord):
    """compute the angle bewteen an horizontal line and the line formed by initialCoord to finalCoord"""
    adjacentSideLenght = abs(initialCoord[0] - finalCoord[0])
    opositeSideLenght = abs(initialCoord[1] - finalCoord[1])
    if(opositeSideLenght == 0):
        if(initialCoord[0] < finalCoord[0]):
            return 0
        else:
            return 180
    
    if(adjacentSideLenght != 0):
        angle = math.degrees(math.atan(opositeSideLenght / adjacentSideLenght))
    else:
        if(initialCoord[1] > finalCoord[1]):
            return 90
        else:
            return 270
        
    if(initialCoord[0] < finalCoord[0]):
        if(initialCoord[1] > finalCoord[1]):
            return angle
        else:
            return 360 - angle
    else:
        if(initialCoord[1] > finalCoord[1]):
            return 180 - angle
        else:
            return 180 + angle

def convertOrientation(scratchOrient):
    """convert the scratch orientation into this converter's orientation system"""
    if( -90 <= scratchOrient <= 90):
        return 90-scratchOrient
    else:
        return 450-scratchOrient

def computeDistance(coordinate, destination):
    """compute the distance bewteen the coordinate and the distination coordonate"""
    return  math.sqrt((coordinate[0] - destination[0])**2 + (coordinate[1] - destination[1])**2)


def getValue(dico, bloc : Bloc, id, variables, initCoordinates, coordinates, orientation):
    """return the calculated value of the idth input of the bloc"""
    if(bloc.inputs[id] in variables):
        return variables[bloc.inputs[id]]
    else:
        if(bloc.inputs[id] in dico):
            return operatorCompute(dico, dico[bloc.inputs[id]], initCoordinates, coordinates, orientation, variables )
    return int(bloc.inputs[id])


def operatorCompute(dico, bloc : Bloc, initCoordinates, coordinates, orientation, variables):
    """analyse the given operator block and return the result of it's action"""
    match bloc.opcode: 
        case "operator_add":
            return getValue(dico, bloc, 0,  variables, initCoordinates, coordinates, orientation) + getValue(dico, bloc, 1,  variables, initCoordinates, coordinates, orientation)
        case "operator_subtract":
            return getValue(dico, bloc, 0,  variables, initCoordinates, coordinates, orientation) - getValue(dico, bloc, 1,  variables, initCoordinates, coordinates, orientation)
        case "operator_multiply":
            return getValue(dico, bloc, 0,  variables, initCoordinates, coordinates, orientation) * getValue(dico, bloc, 1,  variables, initCoordinates, coordinates, orientation)
        case "operator_divide":
            return getValue(dico, bloc, 0,  variables, initCoordinates, coordinates, orientation) / getValue(dico, bloc, 1,  variables, initCoordinates, coordinates, orientation)
        case "operator_mod":
            return getValue(dico, bloc, 0,  variables, initCoordinates, coordinates, orientation) % getValue(dico, bloc, 1,  variables, initCoordinates, coordinates, orientation)
        case "motion_xposition":
            return coordinates[0] - initCoordinates[0]
        case "motion_yposition":
            return initCoordinates[1] - coordinates[1]
        case "motion_direction":
            return orientation
    print("operatorCompute: not in match case : " + bloc.opcode)
    return 0