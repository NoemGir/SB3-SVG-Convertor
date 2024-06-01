#!/usr/bin/env python
# coding: utf-8

import re
from zipfile import ZipFile
import patternMatching as pm;

def extractSB3(sb3_name):
    """ Extract the .json file from the given .sb3 file and put it in the current repertory"""
    print("Décompression du sb3...")
    with ZipFile(sb3_name, "r") as obj_zip:
        FileNames = obj_zip.namelist()
        for fileName in FileNames:
            if fileName.endswith(".json"):
                obj_zip.extract(fileName, "")


def insertLinesRVG(newLines):
    """insert in result.svg the new generated lines"""
    with open('blank.svg', 'r') as f:
        lines = f.readlines()
    
    newLines = '    <path stroke = "black" d="' + newLines + '"/>'
    lines.insert(4, newLines)

    with open('result.svg', 'w') as f_res:
        f_res.writelines(lines)

    len = newLines.count("\n") +1
    print("Génération terminée, nombre de lignes ajouté : ", len)    

def getInitialCoordinate():
    """return the coordinate of the middle of the reference svg"""
    with open('blank.svg', 'r') as f:
        fileReading = f.read() 
        xsize = pm.recognize_X_size(fileReading)
        ysize = pm.recognize_Y_size(xsize, fileReading)
        coord1 = int(xsize)/2
        coord2 = int(ysize)/2
        initCoordinates = [coord1,  coord2]
        return initCoordinates
    
def modifySize(scale):
    """modify the size of the generated svg : existing_size * scale"""
    print("Ajuste la taille de la page...")
    with open('result.svg', 'r') as f:
        lines = f.read()

    xsize = pm.recognize_X_size(lines)
    ysize = pm.recognize_Y_size(xsize, lines)
    lines = lines.replace(xsize, str(int(xsize)*scale))
    lines = lines.replace(ysize, str(int(ysize)*scale))

    with open('result.svg', 'w') as f_res:
        f_res.write(lines)

def transform(x, y):
    """modify the values inside the 'translate' fields to change the position of the figure"""
    print("Ajustement de la position de la figure...")
    with open('result.svg', 'r') as f:
        lines = f.read()

    lines = lines.replace("translate(0,0)", "translate(" + str(x) + "," + str(y) + ")")

    with open('result.svg', 'w') as f_res:
        f_res.write(lines)

def addBigStroke():
    """increase the thickness of the stroke"""
    print("Ajustement de la taille du trait...")
    with open('result.svg', 'r') as f:
        lines = f.read()

    lines = lines.replace('stroke-width="1"', 'stroke-width="14"')

    with open('result.svg', 'w') as f_res:
        f_res.write(lines)

    
def JSONreader():
    """read the json file and return the dictionary containing the bloc informations and the first blocs"""
    print("Génération du fichier svg...")
    with open('project.json', 'r') as f:
        fileReading = f.read()
        fileReading = pm.advanceBlock(fileReading)
        
        first_blocks = pm.get_first_blocks(fileReading)
        dico = pm.createDictionnary(fileReading[9:])

        return [first_blocks, dico]
        
def putColor(coordinate, color):
    """return the lines to add to the svg in order to change the color
    
        the argument 'coordinate' is used to keep the cursor at the same place as previously

    """
    return '"/>\n    <path stroke = "' + color + '" d= "M ' + str(coordinate[0]) + "," + str(coordinate[1]) + " "
    