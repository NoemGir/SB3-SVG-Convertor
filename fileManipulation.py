#!/usr/bin/env python
# coding: utf-8

import re
from zipfile import ZipFile
import patternMatching as pm;

def extractSB3(sb3_name):
    print("Décompression du sb3...")
    with ZipFile(sb3_name, "r") as obj_zip:
        FileNames = obj_zip.namelist()
        for fileName in FileNames:
            if fileName.endswith(".json"):
                obj_zip.extract(fileName, "")


def insertLinesRVG(newLines):

    with open('blank.svg', 'r') as f:
        lines = f.readlines()
        
    lines.insert(8, newLines)

    with open('result.svg', 'w') as f_res:
        f_res.writelines(lines)

    len = newLines.count("\n")
    print("Génération terminée, nombre de lignes ajouté : ", len)    



def getInitialCoordinate():
    initCoordinates

    with open('blank.svg', 'r') as f:
        fileReading = f.read() 
        xsize = pm.recognize_X_size(fileReading)
        ysize = pm.recognize_Y_size(xsize, fileReading)
        coord1 = int(xsize)/2
        coord2 = int(ysize)/2
        initCoordinates = [coord1,  coord2]
        return initCoordinates
    
def JSONreader():
    print("Génération du fichier svg...")
    with open('project.json', 'r') as f:
        fileReading = f.read()
        fileReading = pm.advanceBlock(fileReading)
        
        first_blocks = pm.get_first_blocks(fileReading)
        dico = pm.createDictionnary(fileReading[9:])

        return [first_blocks, dico]
        
