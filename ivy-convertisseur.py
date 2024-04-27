#!/usr/bin/env python
# coding: utf-8


# utiliser un path pour les SVG
import os
from typing import NamedTuple
import re
import math 
import array
from zipfile import ZipFile
from ivy.std_api import *

class Bloc(NamedTuple):
    opcode: str
    parent : str
    next: str
    values: array

dessin = False
coordonnees = [0, 0]
coordInit = [0, 0]
orientation = 0
stop = False

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
    values = []
    for m in input.split('],"'):
        if(len(m) > 0):
            value = re.search(',"(.+?)"]', m).group(1)
            values.append(value)
    return values

def genererDictionnaire(lecture):
    blocs = {}
    for m in re.finditer('"(.+?)":{"opcode":(.*?),"inputs":{(.*?)}(.*?),"fields":{(.*?)}(.*?)}', lecture):
        start = m.start()
        end = m.end()
        bloc = lecture[start:end]
        name = re.search('"(.+?)"', bloc).group(0)
        opcode = re.search('"opcode":"(.+?)"', bloc).group(1)
        next = re.search('"next":(.+?),"parent',bloc).group(1)
        parent = re.search('"parent":(.+?),',bloc).group(1)
        values = get_inputs(re.search('"inputs":{(.*?)},', bloc).group(1))
        object = Bloc(opcode,parent, next, values)
        blocs.update([(name, object)])
    return blocs


def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat", "pen_clear",
                     "motion_changeyby", "motion_changexby", "motion_setx", "motion_sety" ]

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

def cas_avancer(bloc, orientation):
    global dessin
    global coordonnees

    distance = int(bloc.values[0])
    x = calculX(distance, orientation)
    y = - calculY(distance, orientation)
    coordonnees[0] += x
    coordonnees[1] += y
    if(dessin):
        return creerLigne("l", x, y)
    else:
        return creerLigne("m", x, y)

def changer_x(bloc):
    global coordInit
    global dessin
    global coordonnees

    x = int(bloc.values[0]) + coordInit[0]

    coordonnees[0] = x
    if(dessin):
        return "H" + str(x)
    else:
        return creerLigne("M", x, coordonnees[1])

def changer_y(bloc):
    global coordonnees
    global coordInit

    y = coordInit[1] - int(bloc.values[0]) 
    coordonnees[1] = y
    if(dessin):
        return "V" + str(y)
    else:
        return creerLigne("M", coordonnees[0], y)

def cas_aller( bloc):
    global coordInit
    global coordonnees

    x = int(bloc.values[0]) + coordInit[0]
    y = coordInit[1] - int(bloc.values[1])
    coordonnees[0] = x
    coordonnees[1] = y
    
    if(dessin):
        return creerLigne("L", x, y)
    else:
        return creerLigne("M", x, y)


def changer_direction(bloc, droite):
    global orientation

    degree = int(bloc.values[0])
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
                return cas_avancer(bloc, orientation)
            case "motion_changexby":
                return cas_avancer(bloc, 0)
            case "motion_changeyby":
                return cas_avancer(bloc, 90)  
            case "motion_setx":
                return changer_x(bloc)
            case "motion_sety":
                return changer_y(bloc)      
            case "motion_gotoxy":
                return cas_aller( bloc)
            case "motion_turnright":
                changer_direction(bloc, True)
            case "motion_turnleft":
                changer_direction(bloc, False)
            case "motion_pointindirection":
                set_orientation(int(bloc.values[0]))
            case "control_repeat":
                for i in range (int(bloc.values[0])):
                    ajout +=  boucle(dico, dico['"' + bloc.values[1] + '"'] )
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


def genererLignes(dico, first_block):

    ajout = boucle(dico, dico[first_block])

    return ajout

def INITcoordonneesInitiales():
    global coordonnees
    global coordInit

    with open('blank.svg', 'r') as f:
        lecture = f.read()
        coord1 = re.search('M (.+?),', lecture).group(1)
        coord2 = re.search('M ' + coord1 + ',(.+?) ', lecture).group(1)
        coordonnees = [int(coord1), int(coord2)]
        coordInit = [int(coord1), int(coord2)]
    
    
def get_first_block(lecture):
    return re.search('blocks":{(.+?):{', lecture).group(1)

def conversionJSON():
    global first_block

    print("Génération du fichier svg...")
    with open('project.json', 'r') as f:
        lecture = f.read()
        lecture = lecture[lecture.find("block")+1:]
        lecture = lecture[lecture.find("block"):]

        first_block = get_first_block(lecture)
        INITcoordonneesInitiales()

        dico = genererDictionnaire(lecture[9:])
        nouvellesLignes = genererLignes(dico, first_block)

        insertLinesRVG(nouvellesLignes) 
        len = nouvellesLignes.count("\n")
        print("Génération terminée, nombre de lignes ajouté : ", len)

IvyInit("agent_convertisseur")
IvyStart()

def on_tabgo(agent):
    print("Agent %r sent tabgo"%agent)
    decompresserSB3("../sb3/Programme_scratch.sb3")
    conversionJSON()

def on_sb3(agent):
    print("Agent %r sent sb3"%agent)
    decompresserSB3("Programme_scratch.sb3")
    conversionJSON()

def on_json(agent):
    print("Agent %r sent json"%agent)
    conversionJSON()

IvyBindMsg(on_tabgo, "^tabgo: .*")
IvyBindMsg(on_sb3, "^sb3: .*")
IvyBindMsg(on_tabgo, "^json: .*")

while(not stop):
    a = 0











