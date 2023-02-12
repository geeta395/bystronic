# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 12:36:47 2023

@author: chggo
"""
import time
from zipfile import ZipFile
import io
import os
import cv2
import json
import shutil
import numpy as np
from modules.logger import logger
from modules.pathHelper import path_work
from topics.pierce.common.visualization.readData import ReadData
from topics.pierce.common.modules.H5ReaderForPiercing import H5Reader
from topics.pierce.common.visualization.processImages import ProcessImages

class DoWorkPiercing():
    def __init__(self,helper):
        self.helper=helper
        
    def saveFinalImg(self,stream):
        start = time.perf_counter()
        
        logger.info("For this experiment timestamp is used as file name and clean up is not made, to cleanup umcomment")
        
        '''
        # cleanup
        try:
            tfile,tzip=self.helper.checkIf_file()
            
        except Exception as e:
            logger.exception('file is not removed from work folder')
        '''
           
        # Get stream
        logger.info("ZipFile")
        tfile=os.path.join(path_work,'t')
        zip_ref= ZipFile(io.BytesIO(stream))
        self.helper.Extract(stream,tfile)
        
        # read data and save Image
        h5,dumpImg,timeStamp=self.readDataFromStream(zip_ref)
        PI=ProcessImages(dumpImg,resultPath=tfile,gamma=2.5)
        idx=PI.pickImages()
        RD=ReadData(dataPath=None,resultPath=tfile,gamma=2.5)
        RD.getAttributes(h5,idx)
        Im=PI.mergePng(count=0)
        
        # Zip file again
      
        shutil.make_archive(os.path.join(path_work,timeStamp),'zip',tfile)
        
        # Remove tfile
        self.helper.Remove(tfile)
        
        logger.info("For this experiment no azure upload is made, uncomment to upload")
        '''
        # Upload zip
        logger.info("checkUpload")
        try:
            self.helper.checkUpload(tzip)
        except Exception as e:
            logger.exception('Azure upload is failed')
        '''
        logger.info(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f"doWork: done in {time.perf_counter() - start:0.4f} seconds")
        return
    
    def readDataFromStream(self,zip_ref):
        listOfFiles = zip_ref.namelist()
        dumpImg=[]
        for f in listOfFiles :
            
            if f.endswith('.h5') :
                # read h5
                f1=zip_ref.open(f)
                H5File=H5Reader(f1)
                h5=H5File.readH5()
               
                
            if f.endswith('.png') :
                # read images
                f2=zip_ref.open(f)
                string=f2.read()
                #img=cv2.imdecode(np.frombuffer(string, np.uint8),1) 
                img=cv2.imdecode(np.frombuffer(string, np.uint8),cv2.IMREAD_ANYDEPTH)    
                dumpImg.append(img)
                
            if f.endswith('metaInfo.json'):
                f2=zip_ref.open(f)
                meta=json.load(f2)
                timeStamp=meta['data']['time'].replace(':','_')

           
                
        return(h5,dumpImg,timeStamp)
