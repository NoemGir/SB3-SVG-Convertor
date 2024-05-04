#!/usr/bin/env python
# coding: utf-8

import math 
from blocStructure import Bloc

def compute_X(distance, orientation):

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

    sign = 1
    if( 0 <= orientation < 90 or 180 <= orientation < 270):
        b = orientation % 90
    else: 
        b = 90- (orientation % 90)

    if (180 < orientation < 360):
        sign = -1
    b = math.radians(b)
    return math.sin(b) * distance * sign

#return the calculated value of the idth input of the bloc
def getValue(dico, bloc : Bloc, id, variables, initCoordinates, coordinates, orientation):
    if(bloc.inputs[id] in variables):
        return variables[bloc.inputs[id]]
    else:
        if(bloc.inputs[id] in dico):
            return operatorCompute(dico, dico[bloc.inputs[id]], initCoordinates, coordinates, orientation )
    return int(bloc.inputs[id])


def operatorCompute(dico, bloc : Bloc, initCoordinates, coordinates, orientation ):

    match bloc.opcode: 
        case "operator_add":
            return getValue(dico, bloc, 0) + getValue(dico, bloc, 1)
        case "operator_subtract":
            return getValue(dico, bloc, 0) - getValue(dico, bloc, 1)
        case "operator_multiply":
            return getValue(dico, bloc, 0) * getValue(dico, bloc, 1)
        case "operator_divide":
            return getValue(dico, bloc, 0) / getValue(dico, bloc, 1)
        case "motion_xposition":
            return coordinates[0] - initCoordinates[0]
        case "motion_yposition":
            return initCoordinates[1] - coordinates[1]
        case "motion_direction":
            return orientation
    print("operatorCompute: not in match case : " + bloc.opcode)
    return 0