# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 15:09:08 2022

@author: chggo
"""

import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import os
pjoin=os.path.join

class displayCircles():
    def __init__(self,imageList,Radius,X,Y,RadiusTest,XTest,YTest,folder='PredictResult'):
        self.imageList=imageList
        self.Radius=Radius
        self.X=X
        self.Y=Y
        self.RadiusTest=RadiusTest
        self.XTest=XTest
        self.YTest=YTest
        self.folder=folder
        

        
    def circle(self):
        Cat=[]
       
        for i in range(len(self.X)):
            image=self.imageList[i]
            im1=cv2.imread(image,cv2.IMREAD_ANYDEPTH)   # don't add anydepth here
            im2=im1.copy()
           
            
            pred=(cv2.circle(im1, (int(self.X[i]),int(self.Y[i])), int(self.Radius[i]), (0,0,255),3))
            cv2.putText(img=pred, text='Predicted', org=(10,20), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 0, 255),thickness=1)

            Test=(cv2.circle(im2, (int(self.XTest[i]),int(self.YTest[i])), int(self.RadiusTest[i]), (0,255,0),3))
            cv2.putText(img=Test, text='True', org=(10,20), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)
            cat=np.concatenate((pred,Test), axis=1)
        
            Cat.append(cat)
            
        return(Cat)
   
    
    def Save(self,result_path):
        Cat=self.circle()
        
        try: 
            path=pjoin(result_path,self.folder)
            os.mkdir(path) 
        except OSError as error: 
            print(error)  
            
        for i in range(len(Cat)):
            filename=pjoin(result_path,self.folder,'img_'+str(i)+'.png')
            plt.imsave(filename,Cat[i],cmap='jet')
        return
 