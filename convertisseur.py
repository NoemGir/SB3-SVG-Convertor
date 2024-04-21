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
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy", "motion_pointindirection", "control_repeat"]


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

def cas_avancer(bloc, dessin, orientation):
    distance = int(bloc.values[0])
    x = calculX(orientation, distance)
    y = calculY(orientation, distance)

    if(dessin[0]):
        return creerLigne("l", x, y)
    else:
        return creerLigne("m", x, y)

def cas_aller( bloc, dessin):
     x = int(bloc.values[0])
     y = int(bloc.values[1])

     if(dessin[0]):
         return creerLigne("L", x, y)
     else:
         return creerLigne("M", x, y)


def changer_direction(bloc, orientation, droite):
    degree = int(bloc.values[0])
    if(droite):
        orientation[0] += degree
    else:
        orientation[0] -= degree
    orientation[0] = orientation[0]  % 360


def analyseBlock(dico, bloc, ajout, orientation, dessin):
    if( dessin[0] ):
        dessin[0] = bloc.opcode != "pen_penUp"
    else:
        dessin[0] = bloc.opcode == "pen_penDown"
    if(rightBloc(bloc)):
        match bloc.opcode:
            case "motion_movesteps":
                return cas_avancer(bloc, dessin, orientation)        
            case "motion_gotoxy":
                return cas_aller( bloc, dessin)
            case "motion_turnright":
                changer_direction(bloc, orientation, True)
            case "motion_turnleft":
                changer_direction(bloc, orientation, False)
            case "motion_pointindirection":
                orientation[0] = int(bloc.values[0])
            case "control_repeat":
                for i in range (int(bloc.values[0])):
                    ajout +=  boucle(dico, dico[bloc.values[1]], orientation, dessin)
    return ajout

def boucle(dico, bloc, orientation, dessin):
    blocsParcourus = False
    ajout = ""
    while(not blocsParcourus):
        nouvelleLigne = analyseBlock(dico, bloc, ajout, orientation, dessin)
        ajout += nouvelleLigne
        if (bloc.next in dico):
                bloc = dico[bloc.next]
        else:
            blocsParcourus = True
    return ajout


def genererLignes(dico):
    dessin = [False]
    orientation = [0]
    ajout = boucle(dico, dico['"bloc0"'], orientation, dessin)

    return ajout

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






