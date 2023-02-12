# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 14:05:36 2022

@author: chggo
"""

import os
import json
from modules.logger import logger
from modules.pathHelper import path_work,path_resources
from tensorflow import keras
from zipfile import ZipFile
import numpy as np
import cv2
import shutil
from os.path import exists
import matplotlib.pyplot as plt

class DoWorkNozzleCentering():
    def __init__(self,imgFlag):
        self.imgFlag=imgFlag
        self.json='normalize.json'

  
    def doWorkNozzleCentering(self,tzip,tfile):
        
        resized,exp,zip_ref=self.readFromZip(tzip)
        predRadius,predX,predY=self.predict(resized)
        if self.imgFlag==True:
            self.makeCircle(predRadius, predX, predY, exp,zip_ref,tzip,tfile)
        
        return(predRadius,predX,predY)
    
    
    def readFromZip(self,tzip):
        # Read json from zip file
        zip_ref = ZipFile(tzip)
        listOfFiles = zip_ref.namelist()
        Im=[]
        for file in listOfFiles:
            if file.endswith('.png'):
                zip_ref.open(file)
                img=zip_ref.read(file)
                buff=np.frombuffer(img,np.uint8)
                img = cv2.imdecode(buff,cv2.IMREAD_ANYDEPTH)
                Im.append(img)
        logger.info('All images are read')
        exp=self.fusion(Im)
        resized=self.resizeImg(exp)
       
        return(resized,exp,zip_ref)
    
    def fusion(self,Im):
       
        #Merge
        mergeMertens = cv2.createMergeMertens()
        exp = mergeMertens.process(Im)
           
        #UnNormalize 
        alpha = 0xFFFF / (np.max(exp)-np.min(exp))
        beta = -np.min(exp)* alpha
        exp=alpha*exp+beta
        exp = exp.astype(np.uint16)
        #plt.imshow(exp)
        logger.info('Images are Fused')
        return(exp)
        
    def resizeImg(self,img):
        resized=cv2.resize(img, None, fx = 0.5, fy = 0.5)   
        resized=(resized/65535)
        resized = resized[np.newaxis,:, :, np.newaxis]
        logger.info('Fused image is reshaped to {}'.format(resized.shape))
        print('image is converted to tensor with shape:{}'.format(resized.shape))
        return(resized)
     
    def predict(self,exp):
        
        try:
            model = keras.models.load_model(os.path.join(path_work,'topics','nozzleControl','common','resources','imgReg.h5'),compile=False) 
            y_hat = model.predict(exp)
            predRadius,predX,predY=self.UnNormalized(y_hat)
            logger.info('Predicted center and radius [R,X,Y]: {}'.format([int(predRadius[0]),int(predX[0]),int(predY[0])]))
        except Exception as e:
            logger.exception('Prediction is failed')
            
        return(int(predRadius[0]),int(predX[0]),int(predY[0]))
    
    
    def UnNormalized(self,y_hat):
       
        logger.info('Read mean and std from json file')
        with open(os.path.join(path_resources,self.json), 'r') as openfile:
            json_object = json.load(openfile)
        
        m1=json_object['mean1']
        m2=json_object['mean2']
        m3=json_object['mean3']
        
        s1=json_object['std1']
        s2=json_object['std2']
        s3=json_object['std3']
        
        predRadius = list(2*(s1*y_hat[:,0] + m1))
        predX = list(2*(s2*y_hat[:,1] + m2))
        predY = list(2*(s3*y_hat[:,2] + m3))

        predRadius=[int(i) for i in predRadius]
        predX=[int(i) for i in predX]
        predY=[int(i) for i in predY]
        
        return(predRadius,predX,predY)
    
    def makeCircle(self,predRadius,predX,predY,exp,zip_ref,tzip,tfile):
       
        zip_ref.extractall(tfile)
        logger.info('zip file is extracted to save result image')
        pred=cv2.circle(exp,(predX,predY),predRadius,(0,255,0),2)
        cv2.putText(img=pred, text='[X,Y,R]:'+str([predX,predY,predRadius]), org=(10,20), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255,0),thickness=1)
        filename=os.path.join(tfile,'prediction.png')
        
        plt.imsave(filename,pred,cmap='jet',vmin=0,vmax=65535)
        logger.info('image saved with prediction and circle is drawn at {}'.format(filename))
        zip_ref.close()
        shutil.make_archive(tfile, 'zip', tfile) # create a zip again
        logger.info('zip is created along with result image')
        return