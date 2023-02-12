# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:19:54 2022

@author: chggo
"""

import random
import numpy as np
import cv2
import pandas as pd
import os
import matplotlib.pyplot as plt
import skimage

class Synthetic():
    def __init__(self,n):
        self.n=n
        self.columns=720
        self.rows = 540
        
    def getImg(self):
        List=[]
        random.seed(42)
        for i in range(self.n):
          r = random.randint(100,300)
          x = random.randint(int(r * 0.9), int(self.columns - r * 0.9))
          y = random.randint(int(r * 0.9), int(self.rows - r * 0.9))

          center_coordinates = (x, y)
          img = np.zeros((self.rows, self.columns), dtype = "uint8")
          cv2.circle(img, center_coordinates, r, 255, -1)
          img= skimage.util.random_noise(img,mode='s&p',amount=0.1)
          if  0 < random.uniform(-5,5):
              r,x,y,img=self.cutOut(r,x,y,img)
         
          img,r,x,y=self.resizeImg(img,r,x,y)
         
          List.append({'r':r,'x':x,'y':y,'img':img})
        return(List)
    
    def resizeImg(self,img1,r1,x1,y1):
        resized=cv2.resize(img1, None, fx = 0.5, fy = 0.5)   
        #resized=(resized/65535)
        #resized=(resized/255)
        x=int(x1/2)
        y=int(y1/2)
        r=int(r1/2)
        return(resized,r,x,y)
    
    def displaySynthetic(self,result_path,predRadius,predX,predY,testRadius,testX,testY):
        
        try: 
            
            path=os.path.join(result_path,'SyntheticResult')
            os.mkdir(path) 
            
        except OSError as error: 
            print(error)  
        
        for i in range(len(predX)):
            center_coordinates = (testX[i],testY[i])
            center_pred=  (predX[i],predY[i])
            img = np.zeros((540,720), dtype = "uint8")
            cv2.circle(img, center_coordinates, testRadius[i], 255, 2)
            cv2.circle(img, center_pred, predRadius[i],100, 2)
            file=os.path.join(path,'img_'+str(i)+'.png')
           # plt.imshow(img)
            plt.imsave(file,img)
            
    def findY(self,start,r,x,y):
        A=(r**2)-(x-start)**2
        if A>0:
            y1=int(y-np.sqrt(A))
            y2=int(y+np.sqrt(A))
        else:
            y1=y-r
            y2=y+r
        return(y1,y2)
    
    def cutOut(self,r,x,y,img):
        start=int(np.random.choice([random.uniform(x+r-60,x+r-20), np.random.uniform(max(x-r-60,0),max(x-r-20,0))]))  #top left x
        # once x=k is know now find y inside the circle only on the line x=k i.e start1 = y +- sqrt(r^2 -(x-k)^2) 
        y1,y2=self.findY(start,r,x,y)
        start1=int(random.uniform(y1-10,y2-10))
        img = cv2.rectangle(img,(start,start1),(start+70,start1+70), (0,0,0), -1)
    
        return(r,x,y,img)

   
    
  
        


    
    
  
        






