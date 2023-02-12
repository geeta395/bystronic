# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 15:35:55 2023

@author: chggo
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import cv2
import numpy as np
import os
import math

class ProcessImages():
    def __init__(self,dumpImg,resultPath,gamma=2.5):
        self.dumpImg=dumpImg
        self.resultPath=resultPath
        self.gamma=gamma
        
    def pickImages(self):
        subList=[]
        idx=np.round(np.linspace(0, len(self.dumpImg) - 1, 10)).astype(int)  # pick equally spaced 10 images
        for i in range(len(self.dumpImg)):
              if i in idx:
                img=self.dumpImg[i]
                img=img[92:292,92:292]  #crop
                img=cv2.resize(img,(96,96))
                img=self.gammaCorrection(img,self.gamma)
                cv2.putText(img=img, text='frame-'+str(i), org=(10,12), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.3,color=0xBDF7,thickness=1)
               
                subList.append(img)
        Img=(cv2.hconcat(subList))
        
        path=os.path.join(self.resultPath,'img.png')
        #cv2.imwrite(path,Img)
        plt.imsave(path,Img,cmap='jet',vmin=0,vmax=65535)
        return(idx)
    
    def gammaCorrection(self,src, gamma):
        inv_gamma = 1 / gamma
        table = ((np.arange(0, 65536) / 65535) ** inv_gamma) * 65535
        table = table.astype(np.uint16)
      
        return table[src]
    
    def makeList(self):
        # create list for all graphs which are saved or to be saved
        imageNameList=[]
    
        L=['maxIn.png','img.png','Plot1.png','Plot2.png']
        for i in L:
            imageNameList.append(os.path.join(self.resultPath,i))
        return(imageNameList)
    
    def readPng(self):
        Im=[]
        imageNameList= self.makeList()
        for j in imageNameList:
            im=cv2.imread(j,cv2.IMREAD_ANYCOLOR)
            Im.append(im)
        return(Im,imageNameList)
    
    def mergePng(self,count):
        Im,imageNameList=self.readPng()
        
        graph=cv2.vconcat(Im)
        path=os.path.join(self.resultPath,'final_'+str(count)+'.png')
        cv2.imwrite(path,graph)
        self.remove(imageNameList)
        
        return(Im)
        
    def remove(self,imageNameList):
        for i in imageNameList:
           os.remove(i)
        
        
   

