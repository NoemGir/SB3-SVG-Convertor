#!/usr/bin/env python
# coding: utf-8


# utiliser un path pour les SVG
import os
from typing import NamedTuple
import re
import math 
import array
from zipfile import ZipFile


class Bloc(NamedTuple):
    opcode: str
    parent : str
    next: str
    values: array


def decompresserSB3(sb3_name):
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

def genererDictionnaire(lecture):
    blocs = {}
    for m in re.finditer('"bloc(.+?)":{(.*?)}', lecture):
        start = m.start()
        end = m.end()
        bloc = lecture[start:end]
        name = re.search('"(.+?)"', bloc).group(0)
        opcode = re.search('"opcode":"(.+?)"', bloc).group(1)
        next = re.search('"next":(.+?),',bloc).group(1)
        parent = re.search('"parent":(.+?),',bloc).group(1)
        value1 = re.search('0,"(.+?)"]]', bloc)
        value2 = re.search('2,(.+?)]', bloc)

        list = [grouper(value1), grouper(value2)]
        object = Bloc(opcode,parent, next, list)
        blocs.update([(name, object)])
    return blocs


def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat", "pen_clear",
                     "motion_changeyby", "motion_changexby", "motion_setx", "motion_sety" ]

def calculX(orientation, distance):
    signe = 1
    if( 0 <= orientation[0] < 90 or 180 <= orientation[0] < 270):
        b = 90 - (orientation[0] % 90)
    else: 
        b = orientation[0] % 90
    
    if (90 < orientation[0] < 270):
        signe = -1
    b = math.radians(b)
    return math.sin(b) * distance * signe


def calculY(orientation, distance):
    signe = 1
    if( 0 <= orientation[0] < 90 or 180 <= orientation[0] < 270):
        b = orientation[0] % 90
    else: 
        b = 90- (orientation[0] % 90)

    if (180 < orientation[0] < 360):
        signe = -1
    b = math.radians(b)
    return math.sin(b) * distance * signe


def creerLigne(lettre, x, y):
    return lettre + " " + str(x) + "," + str(y) + "\n"

def cas_avancer(bloc, dessin, orientation, coordonnees):
    distance = int(bloc.values[0])
    x = calculX(orientation, distance)
    y = - calculY(orientation, distance)
    coordonnees[0] += x
    coordonnees[1] += y
    if(dessin[0]):
        return creerLigne("l", x, y)
    else:
        return creerLigne("m", x, y)

def changer_x(bloc, dessin, coordonnees):

    coordInit = coordonneesInitiales()
    x = int(bloc.values[0]) + coordInit[0]
    coordonnees[0] = x
    if(dessin[0]):
        return "H" + str(x)
    else:
        return creerLigne("M", x, coordonnees[1])

def changer_y(bloc, dessin, coordonnees):

    coordInit = coordonneesInitiales()
    y = coordInit[1] - int(bloc.values[0]) 
    coordonnees[1] = y
    if(dessin[0]):
        return "V" + str(y)
    else:
        return creerLigne("M", coordonnees[0], y)

def cas_aller( bloc, dessin, coordonnees):

    coordInit = coordonneesInitiales()
    x = int(bloc.values[0]) + coordInit[0]
    y = coordInit[1] - int(bloc.values[1])
    coordonnees[0] = x
    coordonnees[1] = y
    
    if(dessin[0]):
        return creerLigne("L", x, y)
    else:
        return creerLigne("M", x, y)


def changer_direction(bloc, orientation, droite):
    degree = int(bloc.values[0])
    if(droite):
        orientation[0] -= degree
    else:
        orientation[0] += degree
    orientation[0] = orientation[0]  % 360


def set_orientation(orientation, value):
    if(value < 0):
        orientation[0] = (-value+90) % 380
    else:
        orientation[0] = (470-value) % 380

def analyseBlock(dico, bloc, orientation, dessin, coordonnees):
    ajout = ""
    if( dessin[0] ):
        dessin[0] = bloc.opcode != "pen_penUp"
    else:
        dessin[0] = bloc.opcode == "pen_penDown"
    if(rightBloc(bloc)):
        match bloc.opcode:
            case "motion_movesteps":
                return cas_avancer(bloc, dessin, orientation, coordonnees)
            case "motion_changexby":
                return cas_avancer(bloc, dessin, [0], coordonnees)
            case "motion_changeyby":
                return cas_avancer(bloc, dessin, [90], coordonnees)  
            case "motion_setx":
                return changer_x(bloc, dessin, coordonnees)
            case "motion_sety":
                return changer_y(bloc, dessin, coordonnees)      
            case "motion_gotoxy":
                return cas_aller( bloc, dessin, coordonnees)
            case "motion_turnright":
                changer_direction(bloc, orientation, True)
            case "motion_turnleft":
                changer_direction(bloc, orientation, False)
            case "motion_pointindirection":
                set_orientation(orientation, int(bloc.values[0]))
            case "control_repeat":
                for i in range (int(bloc.values[0])):
                    ajout +=  boucle(dico, dico[bloc.values[1]], orientation, dessin, coordonnees)
    return ajout

def boucle(dico, bloc, orientation, dessin, coordonnees):
    blocsParcourus = False
    ajout = ""
    while(not blocsParcourus):
        if(bloc.opcode != "pen_clear"):
            nouvelleLigne = analyseBlock(dico, bloc, orientation, dessin, coordonnees)
            ajout += nouvelleLigne
        else:
            ajout = ""
        if (bloc.next in dico):
                bloc = dico[bloc.next]
        else:
            blocsParcourus = True
    return ajout


def genererLignes(dico):
    dessin = [False]
    orientation = [0]
    coordonnees = coordonneesInitiales()
    ajout = boucle(dico, dico['"bloc0"'], orientation, dessin, coordonnees)

    return ajout

def coordonneesInitiales():
    with open('blank.svg', 'r') as f:
        lecture = f.read()
        coord1 = re.search('M (.+?),', lecture).group(1)
        return [int(coord1), int(coord1)]

def conversionJSON():
    with open('project.json', 'r') as f:
        lecture = f.read()
        lecture = lecture[lecture.find("block")+1:]
        lecture = lecture[lecture.find("block"):]
        
        dico = genererDictionnaire(lecture)
        nouvellesLignes = genererLignes(dico)

        insertLinesRVG(nouvellesLignes)    

decompresserSB3("Programme_scratch.sb3")
conversionJSON()






