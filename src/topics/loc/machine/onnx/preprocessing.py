# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 15:51:11 2022

@author: chggo
"""


import os
import json
from topics.loc.common.dataProcessing import createJson_from_input
from modules.logger import logger
from topics.loc.common.dataProcessing.dataFormat import DataFormat
from modules.pathHelper import path_work



class Preprocessing():
    def __init__(self, file_path, jsonPath):
        self.file_path=file_path
        self.jsonPath = jsonPath
       
       
    def jsonSaved(self):
        
        List,data=self.formatInput()
        logger.info('Save inputJson')
        createJson_from_input.input2json(None,List,True,True,self.file_path)
    
        
        return(List,data)
    
    def formatInput(self):
       f=open(self.jsonPath)
       data=json.load(f)
       logger.info('inputShape.json is read')
       # get input
       Dta=DataFormat(path_work,setLimit=90)
       
       L,List=Dta.getList(data['C_inShape'],data['B_inShape'],pred=True)
       
       return(List,data)