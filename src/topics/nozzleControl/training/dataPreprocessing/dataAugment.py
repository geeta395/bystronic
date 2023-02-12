# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 09:03:26 2022

@author: chggo
"""
import cv2
import pandas as pd
import numpy as np
import random
import os


class DataAugment():
    def __init__(self,df1,data_path,imgReplicate):
        self.df1=df1
        self.data_path=data_path
        self.listAugmented=[]
        self.imgReplicate=imgReplicate
      
        
    def resizeImg(self,img1,r1,x1,y1):
        resized=cv2.resize(img1, None, fx = 0.5, fy = 0.5)   
        resized=(resized/65535)
        x=int(x1/2)
        y=int(y1/2)
        r=int(r1/2)
        return(resized,r,x,y)
        
    def labelList(self):
      
        label=[]
        for j in range(self.df1.shape[0]):
            r=int(self.df1['r'][j])
            x=self.df1['x'][j]
            y=self.df1['y'][j]
            jj = os.path.join(self.data_path,self.df1['img'][j])
            img=cv2.imread(jj,cv2.IMREAD_ANYDEPTH)  # to do...change according to resolution
            img,r,x,y=self.resizeImg(img,r,x,y)
            l={'r':r,'x':x,'y':y,'img':img}
            label.append(l)
        return(label)
    
    def getBorder(self,l,zoom,flipH,flipV):
        h,w=l['img'].shape
        r1=l['r']*zoom
        x1=l['x']
        y1=l['y']
        if flipH==True:
            x1=w-x1-1
        if flipV==True:
            y1=h-y1-1
        leftX=x1-r1
        rightX=w-(x1+r1)
        topY=y1-r1
        bottomY=h-(y1+r1)
        return(leftX,rightX,topY,bottomY)
        
    def gerneratParam(self,seed,l):
        params = []
        while len(params) < self.imgReplicate:
            p = {}
            p['zoom'] = random.uniform(0.8,1.3)
            p['shiftX'] = int(random.uniform(-40,40))
            p['shiftY'] = int(random.uniform(-40,40))   #np.random.choice(20)
            p['angle'] = np.random.choice(5)
           
            p['flipX'] = 0 < random.uniform(-5,5)
            p['flipY'] = 0 < random.uniform(-7,7)
            p['cutOut']=  0 < random.uniform(-5,5)
            leftX,rightX,topY,bottomY=self.getBorder(l,p['zoom'],p['flipX'],p['flipY'])
            if(p['shiftX'] >0 and  p['shiftX'] < rightX-10) or (p['shiftX'] <0 and  p['shiftX'] < leftX-10) or (p['shiftY'] <0 and  p['shiftY'] < bottomY-10) or (p['shiftY'] >0 and  p['shiftY'] < topY-10):
                params.append(p)
        return params
    
    def getPara(self):
        label=self.labelList()
        randomPara=[]
        for i in range(len(label)):
            seed=np.random.seed(i)
            randomPara.append(self.gerneratParam(seed,label[i]))
        return(randomPara,label)
    
    
    def flip(self,r,x,y,img,f=None):
       
        h,w=img.shape
        if f=='H':
            img=cv2.flip(img, 1)
            x=w-x-1
        else:
            img = cv2.flip(img, 0)
            y=h-y-1
        return(r,x,y,img)
    
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
    
    def imgWrap(self,r,x,y,img,param):
        
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY),param['angle'],param['zoom'])
        # to translate
        M[1,2]=param['shiftX']+M[1,2]
        M[0,2]=param['shiftY']+M[0,2]
       
        # Modify center and radius 
        X=np.array((x,y,1))
        x=int(np.sum(np.dot(X,M[0,:])))
        y=int(np.sum(np.dot(X,M[1,:])))
        r=int(r*param['zoom'])
    
        img = cv2.warpAffine(img, M, (w, h),borderMode = cv2.BORDER_REFLECT)
           
        return(r,x,y,img)
        
    def applyFilters(self,r,x,y,img,Para):
        for j in Para:
            r1,x1,y1,img1=r,x,y,img.copy()
            if j['flipX']==True:
                r1,x1,y1,img1=self.flip(r1,x1,y1,img1,'H')
            if j['flipY']==True:
                r1,x1,y1,img1=self.flip(r1,x1,y1,img1)
            if True:
                r1,x1,y1,img1=self.imgWrap(r1,x1,y1,img1,j)
            if j['cutOut']==True:
                r1,x1,y1,img1=self.cutOut(r1,x1,y1,img1)
            self.listAugmented.append({'r':r1,'x':x1,'y': y1,'img':img1})
        
    
    def List(self):
        randomPara,label=self.getPara()
        for i in range(len(label)):
            if len(randomPara)==len(label):
                self.applyFilters(label[i]['r'],label[i]['x'],label[i]['y'],label[i]['img'],randomPara[i])
           
        return(self.listAugmented)