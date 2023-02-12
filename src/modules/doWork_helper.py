# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 17:04:30 2022

@author: chggo
"""

import os
from os.path import exists
from modules.pathHelper import path_work
import shutil
from modules.logger import logger
from zipfile import ZipFile
import io
import stat

class DoWorkHelper():
    def __init__(self,uploader):
        self.uploader=uploader
    
    def removeReadOnly(self,tfile):
        #it removes file 't' which has 'read only' attribute
        os.chmod( tfile, stat.S_IWRITE )
        os.unlink(tfile)
        
    def checkIf_file(self):
        logger.info('Clean existing files')
        tfile=os.path.join(path_work,'t')
        tzip=(tfile+'.zip')
        if exists(tfile):
            shutil.rmtree(tfile, onerror = self.removeReadOnly )
            
        if exists(tzip):
            os.remove(tzip)
        return(tfile,tzip)
    
    def saveStream(self,stream,tzip):
        # save stream to zip
        f = open(tzip, "wb")
        f.write(stream)
        logger.info("Zip Created")
        f.close()
        return
    
        
    def Remove(self,tfile):
        imagePath=os.path.join(path_work,'Preview_0.png')
        if exists(imagePath):
            os.remove(imagePath) 
        if exists(tfile):
            shutil.rmtree(tfile)
        return
           
    
    def Extract(self,stream,tfile):
        zip_obj= ZipFile(io.BytesIO(stream),"r")
      
        zip_obj.extractall(tfile)
        zip_obj.close()
        return

    def checkUpload(self,filePath,inf=True,topic='icp/dumps/lossOfCutDetected'):
       
        if inf==True:
            if topic == 'icp/dumps/lossOfCutDetected':
                logger.info('Inference is True now upload on azure')
            
            r,f=self.uploader.upload_using_sas(filePath)
            logger.info("Upload Status :" + str(r))
            if r != 201 :
                logger.warning('No upload is made check proxy settings')
            
            logger.info("Upload Status")
            print('uploded on Azure')
        else:
            logger.warning('No upload is made as the file was not fit for inference')
        
        # Remove file after all process is completed
        logger.info('Removing zip file')
        if exists(filePath):
            os.remove(filePath)
        
        return
    
