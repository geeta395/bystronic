# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 10:42:25 2023

@author: chggo
"""

import os
import json
from modules.logger import logger
from os.path import exists
from modules.pathHelper import path_work
from zipfile import ZipFile
import time

class DoWorkNozzleControl():
    def __init__(self,helper):
        self.helper=helper
       
  
    def doWorkNozzle(self,stream,topic):
        start = time.perf_counter()
        # check for already existing file
        tfile,tzip=self.helper.checkIf_file()
        # Create the zip at temporary location
        self.helper.saveStream(stream,tzip)
        # get file name
        jsonFile=os.path.join(path_work,'nozzleControl.json')
        # check if json exists
        if not exists(jsonFile):
            counter=1
            logger.info('nozzleControl.json is created')
            self.createNozzleJson(tzip,jsonFile,List=[])
        else:
            logger.info('nozzleControl.json alreday exists')
            counter=self.checkTag(tzip,jsonFile)
            
        if counter <= 10:
            self.helper.checkUpload(tzip,inf=True,topic=topic)
        else:
            logger.info('since upload counter is {},no upload is being made'.format(counter))
        
        logger.info(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        print(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        return
    
    
    def checkTag(self,tzip,jsonFile):
        j = open(jsonFile)
        content_J=json.load(j)
        List=content_J['data']['dumpCounter']
        tag=self.readImgJson(tzip)
    
        if not any(tag in d for d in List):
            logger.info('{} does not exist'.format(tag))
            counter=1
            List.append({tag:counter})
            logger.info('{} is appended'.format(tag))
            self.createNozzleJson(tzip,jsonFile,List,None)
        else:
            logger.info('{} exists, check for counter'.format(tag))
            counter=self.updateCounter(tag,List)
            self.createNozzleJson(tzip,jsonFile,List,None)
            
        return(counter)
               
                
                
    def updateCounter(self,tag,List):  
        tup=next((i,d) for i,d in enumerate(List) if tag in d)
        index=tup[0]
        counter=tup[1][tag]
        logger.info('The counter is {}'.format(counter))
        List[index][tag]=List[index][tag]+1
        return(counter)

    def readFromZip(self,tzip):
        # Read json from zip file
        zip_ref = ZipFile(tzip)
        listOfFiles = zip_ref.namelist()
        content=None
        for file in listOfFiles:
            if file.endswith('imgMeta.json'):
                f=zip_ref.open(file)
                content=json.load(f)
                break
        if content==None:
            logger.info('No imgMeta.json file exists')
           
        return(content)
        
    def readImgJson(self,tzip):
        # get tag from json file
        content=self.readFromZip(tzip)
        nozzleAcquisitionSubcommand=content['type']
        raster=content['data'][0]['meta']['cuttingHead']['raster']
        nozzleType=content['data'][0]['meta']['param']['nozzleType']
        tag= nozzleAcquisitionSubcommand+'_'+nozzleType+'_R'+ str(raster)
        return(tag)
               
    def createNozzleJson(self,tzip,jsonFile,List,tag='create'):
        if tag=='create':
            tag=self.readImgJson(tzip)
            dictt={tag:1}
            List.append(dictt)
            
        filterInfo={'type':'nozzleControl','data':{'dumpCounter':List}}
        
        with open(jsonFile, 'w') as file:
            file.write(json.dumps(filterInfo))  
        return
     