# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 07:16:41 2022

@author: chggo
"""


import os
from zipfile import ZipFile
import io
import shutil
from modules.logger import logger
from topics.loc.machine.onnx.predict import Predict
import time
from os.path import exists
from modules.pathHelper import path_work


class DoWorkLOC():
    def __init__(self, helper):
        self.helper=helper

        
    def doWorkLocOfCut(self,stream,charts):
        
        global inf
        start = time.perf_counter()
        # cleanup
        try:
            tfile,tzip=self.helper.checkIf_file()
            
        except Exception as e:
            logger.exception('file is not removed from work folder')
           
        # Get stream
        logger.info("ZipFile")
        zip_ref= ZipFile(io.BytesIO(stream))
        self.helper.Extract(stream,tfile)

        if charts:
           
            # Get charts
            logger.info("processDump")
            try:
                self.processDump(zip_ref)
            except Exception as e:
                logger.exception('processDump is failed')
        
            zip_ref.close()
    
           
    
            # Save charts        
            
            try:
                self.saveImg(stream,tfile)
                logger.info("Image is saved")
            except Exception as e:
                logger.exception('saveImg is failed')
               

        if not charts:
            logger.info('Image is not required by the User')
            
            
        # Inference
        shutil.make_archive(tfile, 'zip', tfile) # create a zip again
       
        try:
         On=Predict(tfile)  
         inf=On.onnxPred()
        except Exception as e:
            logger.exception('Prediction is failed')
        
       # Remove file
        shutil.make_archive(tfile, 'zip', tfile) # create a zip again
        logger.info("Remove unzip file")
        self.helper.Remove(tfile)
        
        # Upload zip
        logger.info("checkUpload")
        try:
            self.helper.checkUpload(tzip)
        except Exception as e:
            logger.exception('Azure upload is failed')
        
            
        logger.info(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        return
    
        
    def processDump(self,zip_ref):
        from topics.loc.common.modules.dump_helper import DumpHelper
        M=DumpHelper(path_work)
        file1,file2 =M.get_H5_file_names(zip_ref)
        folder1=[file1,file2]
        ffolder=M.empty(folder1,90)
      
        if len(ffolder) !=0:
            
            self.charts(ffolder,'dump')
    
        return
        
            
    
    def charts(self,ffolder,newFile):
        #import files
        from topics.loc.common.visualization.mergeCV import mergePlot
        image=mergePlot(path_work,path_work)
        image.saveImg(0,ffolder,newFile)
        return
   
        
        
    def saveImg(self,stream,tfile):
        imagePath=os.path.join(path_work,'Preview_0.png')
        if exists(imagePath):
           
            shutil.move(imagePath,tfile,copy_function = shutil.copytree) # move image to folder
        else:
            logger.warning('empty folder, No Image')
       
        return
        

        
    