#!/usr/bin/env python
# coding: utf-8


# utiliser un path pour les SVG
import os
from typing import NamedTuple
import re
import math 
import array
from zipfile import ZipFile


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

class Bloc(NamedTuple):
    opcode: str
    parent : str
    next: str
    inputs: array
    fields: array

dessin = False
coordonnees = [0, 0]
coordInit = [0, 0]
orientation = 0
variables = {}

def decompresserSB3(sb3_name):
    print("Décompression du sb3...")
    with ZipFile(sb3_name, "r") as obj_zip:
        FileNames = obj_zip.namelist()
        for fileName in FileNames:
            if fileName.endswith(".json"):
                obj_zip.extract(fileName, "")


def insertLinesRVG(nouvellesLignes):

    with open('blank.svg', 'r') as f:
        lines = f.readlines()
        
    lines.insert(8, nouvellesLignes)

    with open('result.svg', 'w') as f_res:
        f_res.writelines(lines)    

def grouper(value):
    if(value != None ):
        return value.group(1)
    else:
        return None


def get_inputs(input):
    inputs = []
    for m in input.split('],"'):
        if(len(m) > 0):
            value = re.search(',"(.+?)"', m)
            if(value != None):
                value = value.group(1)
                inputs.append(value)
    return inputs

# a améliorer
def get_fields(input):
    fields = []
    for m in input.split('],"'):
        if(len(m) > 0):
            value = re.search('\["(.+?)",', m)
            if(value != None):
                value = value.group(1)
                fields.append(value)
    return fields

def genererDictionnaire(lecture):
    blocs = {}
    for m in re.finditer('"(.+?)":{"opcode":(.*?),"inputs":{(.*?)}(.*?),"fields":{(.*?)},"shadow"(.+?)}', lecture):
        start = m.start()
        end = m.end()
        bloc = lecture[start:end]
        name = re.search('"(.+?)"', bloc).group(1)
        opcode = re.search('"opcode":"(.+?)"', bloc).group(1)
        next = re.search('"next":(?:"|)(.+?)(?:"|),"parent',bloc).group(1)
        parent = re.search('"parent":(?:"|)(.+?)(?:"|),',bloc).group(1)
        inputs = get_inputs(re.search('"inputs":{(.*?)},', bloc).group(1))
        fields = get_fields(re.search('"fields":{(.*?)},"shadow', bloc).group(1))
        object = Bloc(opcode,parent, next, inputs, fields)
        print("bloc ajouté : ", name, object)
        blocs.update([(name, object)])
    return blocs


def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat", "pen_clear",
                     "motion_changeyby", "motion_changexby", "motion_setx", "motion_sety", "control_repeat_until", "data_setvariableto", "data_changevariableby",
                      "control_if", "control_if_else" ]

def calculX(distance, orientation):

    signe = 1
    if( 0 <= orientation < 90 or 180 <= orientation < 270):
        b = 90 - (orientation % 90)
    else: 
        b = orientation % 90
    
    if (90 < orientation < 270):
        signe = -1
    b = math.radians(b)
    return math.sin(b) * distance * signe


def calculY(distance, orientation):

    signe = 1
    if( 0 <= orientation < 90 or 180 <= orientation < 270):
        b = orientation % 90
    else: 
        b = 90- (orientation % 90)

    if (180 < orientation < 360):
        signe = -1
    b = math.radians(b)
    return math.sin(b) * distance * signe


def creerLigne(lettre, x, y):
    return lettre + " " + str(x) + "," + str(y) + "\n"

def cas_avancer(dico, bloc, orientation):
    global dessin
    global coordonnees

    distance = get_value(dico, bloc, 0)
    x = calculX(distance, orientation)
    y = - calculY(distance, orientation)
    coordonnees[0] += x
    coordonnees[1] += y
    if(dessin):
        return creerLigne("l", x, y)
    else:
        return creerLigne("m", x, y)

def changer_x(dico, bloc):
    global coordInit
    global dessin
    global coordonnees

    x =  get_value(dico, bloc, 0) + coordInit[0]

    coordonnees[0] = x
    if(dessin):
        return "H" + str(x)
    else:
        return creerLigne("M", x, coordonnees[1])

def changer_y(dico, bloc):
    global coordonnees
    global coordInit

    y = coordInit[1] -  get_value(dico, bloc, 0)
    coordonnees[1] = y
    if(dessin):
        return "V" + str(y)
    else:
        return creerLigne("M", coordonnees[0], y)

def cas_aller(dico, bloc):
    global coordInit
    global coordonnees

    x = get_value(dico, bloc, 0) + coordInit[0]
    y = coordInit[1] - get_value(dico, bloc, 1)
    coordonnees[0] = x
    coordonnees[1] = y
    
    if(dessin):
        return creerLigne("L", x, y)
    else:
        return creerLigne("M", x, y)


def changer_direction(dico, bloc, droite):
    global orientation

    degree = get_value(dico, bloc, 0)
    if(droite):
        orientation -= degree
    else:
        orientation += degree
    orientation = orientation  % 360


def set_orientation(value):
    global orientation

    if(value < 0):
        orientation = (-value+90) % 380
    else:
        orientation = (470-value) % 380

#return the calculated value of the idth input of the bloc
def get_value(dico, bloc, id):
    if(bloc.inputs[id] in variables):
        return variables[bloc.inputs[id]]
    else:
        if(bloc.inputs[id] in dico):
            return operator_compute(dico, dico[bloc.inputs[id]])
    return int(bloc.inputs[id])


def operator_compute(dico, bloc):
    global coordInit
    global coordonnees

    match bloc.opcode: 
        case "operator_add":
            return get_value(dico, bloc, 0) + get_value(dico, bloc, 1)
        case "operator_subtract":
            return get_value(dico, bloc, 0) - get_value(dico, bloc, 1)
        case "operator_multiply":
            return get_value(dico, bloc, 0) * get_value(dico, bloc, 1)
        case "operator_divide":
            return get_value(dico, bloc, 0) / get_value(dico, bloc, 1)
        case "motion_xposition":
            return coordonnees[0] - coordInit[0]
        case "motion_yposition":
            return coordInit[1] - coordonnees[1]
        case "motion_direction":
            return orientation
    print("operator_compute: not in match case : " + bloc.opcode)
    return 0

def in_edge():
    global coordonnees
    global coordInit

    return 0 < coordonnees[0] < coordonnees[0]*2 and 0 < coordonnees[1] < coordonnees[1]*2

def condition(dico, bloc):
    match bloc.opcode: 
        case "operator_or":
            return condition(dico, dico[bloc.inputs[0]]) or condition(dico, dico[bloc.inputs[1]])
        case "operator_and":
            return condition(dico, dico[bloc.inputs[0]]) and condition(dico, dico[bloc.inputs[1]])
        case "operator_not":
            return not condition(dico, dico[bloc.inputs[0]])
        case "operator_equals":
            return get_value(dico, bloc, 0) == get_value(dico, bloc, 1)
        case "operator_gt":
            return get_value(dico, bloc, 0) > get_value(dico, bloc, 1)
        case "operator_lt":
            return get_value(dico, bloc, 0) < get_value(dico, bloc, 1)
        case "sensing_touchingobject":
            return not in_edge()
    print("condition: not in match case : " + bloc.opcode)
    return False

def control_repeat(dico, bloc):
    ajout = ""
    for i in range (get_value(dico, bloc, 0)):
        ajout +=  boucle(dico, dico[ bloc.inputs[1]] )
    return ajout

def control_repeat_until(dico, bloc):
    ajout = ""
    while(not condition(dico, dico[bloc.inputs[1]]) ):
        ajout +=  boucle(dico, dico[bloc.inputs[0]] )
    return ajout

def control_if_else(dico, bloc):
    ajout = ""
    if(condition(dico, dico[bloc.inputs[2]])):
        ajout +=  boucle(dico, dico[bloc.inputs[0]] )
    else:
        ajout +=  boucle(dico, dico[bloc.inputs[1]] )
    return ajout

def control_if( dico, bloc):
    ajout = ""
    if(condition(dico, dico[bloc.inputs[1]])):
        ajout +=  boucle(dico, dico[bloc.inputs[0]] )
    return ajout

def change_variable(dico, bloc):
    global variables 

    if(bloc.fields[0] in variables):
        value = variables[bloc.fields[0]]
        variables.update([(bloc.fields[0], value + get_value(dico, bloc, 0))])
    else:
        variables.update([(bloc.fields[0], get_value(dico, bloc, 0))])

def analyseBlock(dico, bloc):
    global dessin
    global orientation
    global coordonnees
    
    ajout = ""
    if( dessin):
        dessin = bloc.opcode != "pen_penUp"
    else:
        dessin = bloc.opcode == "pen_penDown"
    if(rightBloc(bloc)):
        match bloc.opcode:
            case "motion_movesteps":
                return cas_avancer(dico, bloc, orientation)
            case "motion_changexby":
                return cas_avancer(dico, bloc, 0)
            case "motion_changeyby":
                return cas_avancer(dico, bloc, 90)  
            case "motion_setx":
                return changer_x(dico, bloc)
            case "motion_sety":
                return changer_y(dico, bloc)      
            case "motion_gotoxy":
                return cas_aller(dico,  bloc)
            case "motion_turnright":
                changer_direction(dico, bloc, True)
            case "motion_turnleft":
                changer_direction(dico, bloc, False)
            case "motion_pointindirection":
                set_orientation(get_value(dico, bloc, 0))
            case "control_repeat":
                return control_repeat(dico, bloc)
            case "control_repeat_until":
                return control_repeat_until(dico, bloc)
            case "control_if_else":
                return control_if_else(dico, bloc)
            case "control_if":
                return control_if(dico, bloc)
            case "data_setvariableto":
                variables.update([(bloc.fields[0], get_value(dico, bloc, 0))])
            case "data_changevariableby":
                change_variable(dico, bloc)
                
    return ajout

def boucle(dico, bloc):
    blocsParcourus = False
    ajout = ""
    while(not blocsParcourus):
        if(bloc.opcode != "pen_clear"):
            nouvelleLigne = analyseBlock(dico, bloc)
            ajout += nouvelleLigne
        else:
            ajout = ""
        if (bloc.next in dico):
                bloc = dico[bloc.next]
        else:
            blocsParcourus = True
    return ajout


def genererLignes(dico, first_blocks):
    ajout = creerLigne("M", coordInit[0], coordInit[1])
    for first in first_blocks:
        ajout += boucle(dico, dico[first])
    
    return ajout

def INITcoordonneesInitiales():
    global coordonnees
    global coordInit

    with open('blank.svg', 'r') as f:
        lecture = f.read() 
        xsize = re.search('viewBox="0 0 (.+?) ', lecture).group(1) #viewBox="0 0 1000 1000"
        ysize = re.search('viewBox="0 0 ' + xsize + ' (.+?)"', lecture).group(1)
        coord1 = int(xsize)/2
        coord2 = int(ysize)/2
        coordonnees = [coord1,  coord2]
        coordInit = [coord1,  coord2]
    
    
def get_first_blocks(lecture):
    first = []
    for m in re.finditer('[^"]+(?=":{"opcode":"event_|":{"opcode":"event_)', lecture):
        start = m.start()
        end = m.end()
        name = lecture[start:end]
        print("-----------name = " + name)
        first.append(name)
    return first

def conversionJSON():
    global first_block

    print("Génération du fichier svg...")
    with open('project.json', 'r') as f:
        lecture = f.read()
        lecture = lecture[lecture.find("block")+1:]
        lecture = lecture[lecture.find("block"):]

        first_blocks = get_first_blocks(lecture)
        INITcoordonneesInitiales()

        dico = genererDictionnaire(lecture[9:])
        nouvellesLignes = genererLignes(dico, first_blocks)

        insertLinesRVG(nouvellesLignes) 
        len = nouvellesLignes.count("\n")
        print("Génération terminée, nombre de lignes ajouté : ", len)

def on_tabgo():
    decompresserSB3("../sb3/Programme_scratch.sb3")
    conversionJSON()

def on_sb3():
    decompresserSB3("Programme_scratch.sb3")
    conversionJSON()

def on_json():
    conversionJSON()

on_sb3()







