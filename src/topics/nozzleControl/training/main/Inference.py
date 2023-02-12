# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:37:54 2022

@author: chggo
"""

import os
import cv2
import glob
from typing import List
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
import json
from modules.pathHelper import path_work,path_resources



# windows

result_path = r'C:\Users\chggo\REG_analysis\icpNozzleCentering\result'
source_root=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\data\img\test\20220602_AP2E_NozzleCentering\MC7'

# Linux
'''
result_path=r'/data/EL1947-NozzleCentering/icpNozzleSegmentation/result/'
source_root=r'/data/EL1947-NozzleCentering/icpNozzleSegmentation/data/img/test/20220602_AP2E_NozzleCentering/MC7'
'''

class Inference():
    def __init__(self,source_root,result_path,jsonFile='normalize.json'):
     
        self.source_root=source_root
        self.result_path=result_path
        self.jsonFile=jsonFile
    
    def list_files(self,directory, suffix=".png") -> List[str]:
        files_list = []
        for subdir, dirs, files in os.walk(directory):
            for filename in sorted(files):
                filepath = os.path.join(subdir, filename)
                if filepath.endswith(suffix):
                    files_list.append(filepath)
        
        return files_list


    def process(self,img):
        
        resized=(cv2.resize(img, None, fx = 0.5, fy = 0.5))/65535
        img = resized[:, :, np.newaxis]
        return(resized)
    
    def formatList(self):
        img_dirs = glob.glob(self.source_root + "*/*")

        for img_dir in img_dirs:
            images = [(img) for img in self.list_files(img_dir) if "_c0" in img]
            
        Img=[]
        for i in images:
            Img.append(self.process(cv2.imread(i,cv2.IMREAD_ANYDEPTH)))  
        ImgFormat=np.stack(Img, axis=0)
        return(ImgFormat,images)
        
    def Predict(self):
        ImgFormat,images = self.formatList()
        # Load model
        model = keras.models.load_model(os.path.join(path_work,'topics','nozzleControl','common','resources','imgReg.h5'),compile=False) 
        y_hat = model.predict(ImgFormat)
        return(y_hat,images)
    
    def UnNormalized(self):
        y_hat,images=self.Predict()
        with open(os.path.join(path_resources,self.jsonFile), 'r') as openfile:
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
        
        return(predRadius,predX,predY,images)
    
    def realImg(self):
        realImage=[]
        
        predRadius,predX,predY,images=self.UnNormalized()
        for i in images:
            img=cv2.imread(i)  
            realImage.append(img)
            
        return(predRadius,predX,predY,realImage)
    
    def makeCircle(self):
        predRadius,predX,predY,realImage=self.realImg()

        imageList=[]
        
        try: 
            path=os.path.join(self.result_path,'Inference')
            os.mkdir(path) 
        except OSError as error: 
            print(error)  
            i=1
        for i in range(len(realImage)):
            image=realImage[i]
            pred=(cv2.circle(image, (predX[i],predY[i]),predRadius[i],(0,255,0),2))
            cv2.putText(img=pred, text='[X,Y,R]:'+str([predX[i],predY[i],predRadius[i]]), org=(10,20), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255,0),thickness=1)
            filename=os.path.join(self.result_path,'Inference','img_'+str(i)+'.png')
            imageList.append(filename)
            cv2.imwrite(filename,pred)
        
       
            
        # save result
        data={'Radius':predRadius,'X':predX,'Y':predY,'Image':imageList}
        Data=pd.DataFrame(data)  
        Data.to_excel(os.path.join(self.result_path,'Inference.xlsx'))
        return(Data)
    
P=Inference(source_root,result_path)
Data=P.makeCircle()

