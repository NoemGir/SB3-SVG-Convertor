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



def genererDictionnaire(lecture):
    blocs = {}
    for m in re.finditer('"bloc(.+?)":{(.*?)}', lecture):
        start = m.start()
        end = m.end()
        bloc = lecture[start:end]
        name = re.search('"(.+?)"', bloc).group(0)
        opcode = re.search('"opcode":"(.+?)"', bloc).group(1)
        next = re.search('"next":(.+?),',bloc).group(1)
        values = re.search('0,"(.+?)"]]', bloc)
        if(values != None ):
            list = [int(values.group(1))]
            object = Bloc(opcode, next, list)
        else: 
            object = Bloc(opcode, next, None)
        blocs.update([(name, object)])
    return blocs


def rightBloc(bloc):
    opcode = bloc.opcode
    return opcode in ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_gotoxy"]



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



def ajouterLigne(lettre, ajout, x, y):
    ligne = lettre + " " + str(x) + "," + str(y) + "\n"
   # print("ligne ajoutée = " + ligne) 
    ajout = ajout + ligne
    return ajout


def cas_avancer(ajout, bloc, dessin, orientation):
    distance = bloc.values[0]
    x = calculX(orientation, distance)
    y = calculY(orientation, distance)

    if(dessin):
        ajout = ajouterLigne("l", ajout, x, y)
    else:
        ajout = ajouterLigne("m", ajout, x, y)
    return ajout


def cas_aller(ajout, bloc, dessin):
     x = bloc.values[0]
     y = bloc.values[1]

     if(dessin):
         ajout = ajouterLigne("L", ajout, x, y)
     else:
         ajout = ajouterLigne("M", ajout, x, y)
     return ajout


def changer_direction(bloc, orientation, droite):
    degree = bloc.values[0]
    if(droite):
        orientation[0] += degree
    else:
        orientation[0] -= degree
    orientation[0] = orientation[0]  % 360


def actionBloc(ajout, bloc, dessin, orientation):
    match bloc.opcode:
        case "motion_movesteps":
            ajout = cas_avancer(ajout, bloc, dessin, orientation)        
        case "motion_gotoxy":
            ajout = cas_aller(ajout, bloc, dessin)
        case "motion_turnright":
            changer_direction(bloc, orientation, True)
        case "motion_turnleft":
            changer_direction(bloc, orientation, False)
    return ajout



def genererLignes(dico):
    blocsParcourus = False;
    bloc = dico['"bloc0"']
    ajout = ""
    dessin = False
    orientation = [0]
    while(not blocsParcourus):
       # print("BLOC = " + bloc.opcode)
        if( dessin ):
            dessin = bloc.opcode != "pen_penUp"
        else:
            dessin = bloc.opcode == "pen_penDown"

        if(rightBloc(bloc)):
            ajout = actionBloc(ajout, bloc, dessin, orientation)
            
        if (bloc.next in dico):
            bloc = dico[bloc.next]
        else:
            blocsParcourus = True;
    return ajout


decompresserSB3("Programme_scratch.sb3")
with open('project.json', 'r') as f:
    lecture = f.read()
    lecture = lecture[lecture.find("block")+1:]
    lecture = lecture[lecture.find("block"):]
    
    dico = genererDictionnaire(lecture)
    nouvellesLignes = genererLignes(dico)

    insertLinesRVG(nouvellesLignes)    






