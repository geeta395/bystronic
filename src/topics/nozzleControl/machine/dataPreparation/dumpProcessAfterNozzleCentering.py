# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 17:53:55 2022

@author: chggo
"""
import os
import json
from modules.logger import logger
from os.path import exists
from modules.pathHelper import path_work,path_resources
from zipfile import ZipFile
import time
import numpy as np
import cv2
from topics.nozzleControl.machine.dataPreparation.doWorkNozzleCentering import DoWorkNozzleCentering

class DoWorkNozzleControl():
    def __init__(self,helper):
        self.helper=helper
       
  
    def doWorkNozzle(self,stream,topic):
        start = time.perf_counter()
        uploadFlag=False
        # check for already existing file
        tfile,tzip=self.helper.checkIf_file()
        
        # Create the zip at temporary location
        self.helper.saveStream(stream,tzip)
        # get file name
        jsonFile=os.path.join(path_resources,'nozzleControl.json')
        # check if json exists
        if not exists(jsonFile):
            counter=1
            logger.info('nozzleControl.json is created')
            mean=self.createNozzleJson(tzip,jsonFile,List=[])
        else:
            logger.info('nozzleControl.json alreday exists')
            counter,mean=self.checkTag(tzip,jsonFile)
            
        if mean>100:
            # if images are bright make prediction
            DWN=DoWorkNozzleCentering(imgFlag=True)
            predRadius,predX,predY=DWN.doWorkNozzleCentering(tzip,tfile)
            self.helper.checkIf_file()
            
            if counter <= 10 :
                #upload iafter checking counter, in future replace counter by confidence score
                uploadFlag=True
                self.helper.checkUpload(tzip,inf=True,topic=topic)
               
            else:
                if counter > 10:
                    logger.info('since upload counter is {},no upload is being made'.format(counter))
        else:
            logger.info('since pixel mean is {}(too low),no upload is being made'.format(mean))
        
        logger.info(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        print(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        return(uploadFlag)
    
    
    def checkTag(self,tzip,jsonFile):
        j = open(jsonFile)
        content_J=json.load(j)
        List=content_J['data']['dumpCounter']
        tag,mean=self.readImgJson(tzip)
    
        if not any(tag in d for d in List):
            logger.info('{} does not exist'.format(tag))
            counter=1
            List.append({tag:counter})
            logger.info('{} is appended'.format(tag))
            mean=self.createNozzleJson(tzip,jsonFile,List,None)
        else:
            logger.info('{} exists, check for counter'.format(tag))
            counter=self.updateCounter(tag,List)
            mean=self.createNozzleJson(tzip,jsonFile,List,None)
            
        return(counter,mean)
               
                
                
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
        imgId=0
        for file in listOfFiles:
            if file.endswith('imgMeta.json'):
                f=zip_ref.open(file)
                content=json.load(f)
                
            if file.endswith('.png') and imgId==0:
                zip_ref.open(file)
                img=zip_ref.read(file)
                buff=np.frombuffer(img,np.uint8)
                img = cv2.imdecode(buff,cv2.IMREAD_ANYDEPTH)
                mean=round(np.mean(img),3)
                imgId=imgId+1
                
        if content==None:
            logger.info('No imgMeta.json file exists')
           
        return(content,mean)
        
    def readImgJson(self,tzip):
        # get tag from json file
        content,mean=self.readFromZip(tzip)
        nozzleAcquisitionSubcommand=content['type']
        raster=content['data'][0]['meta']['cuttingHead']['raster']
        nozzleType=content['data'][0]['meta']['param']['nozzleType']
        tag= nozzleAcquisitionSubcommand+'_'+nozzleType+'_R'+ str(raster)
        return(tag,mean)
               
    def createNozzleJson(self,tzip,jsonFile,List,tag='create'):
        tag,mean=self.readImgJson(tzip)
        if tag=='create':
           
            dictt={tag:1}
            List.append(dictt)
            
        filterInfo={'type':'nozzleControl','data':{'dumpCounter':List}}
        
        with open(jsonFile, 'w') as file:
            file.write(json.dumps(filterInfo))  
        return(mean)
     
