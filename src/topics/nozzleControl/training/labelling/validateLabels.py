# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:00:38 2022

@author: chggo
"""

import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd




class Validate():
    def __init__(self,List,data_path,result_path):
        self.List=List
        self.data_path=data_path
        self.result_path=result_path
        
        
    def validateImg(self):
        
        try: 
            path=os.path.join(self.result_path,'InputValidation')
            os.mkdir(path) 
        except OSError as error: 
            print(error)  
        R=[]
        X=[]
        Y=[]
        for j in range(len(self.List)):
            r1=self.List[j]['r']
            x1=self.List[j]['x']
            y1=self.List[j]['y']
            img1=self.List[j]['img']
            img2=img1.copy()
            img=cv2.circle(img2,(x1,y1),r1,(0,255,255),2)
            filename=os.path.join(self.result_path,'InputValidation','img_'+str(j)+'.png')
            plt.imsave(filename,img,cmap='jet')
            R.append(r1)
            X.append(x1)
            Y.append(y1)
        return(R,X,Y)
            
            
    def validateDistribution(self,Inference_path):
        testData=pd.read_excel(os.path.join(Inference_path,"Inference.xlsx"))
        Img = np.zeros((800,800,3),np.uint8)
        R=[]
        X=[]
        Y=[]
        for j in range(len(self.List)):
            r1=self.List[j]['r']
            R.append(r1)
            x1=self.List[j]['x']
            X.append(x1)
            y1=self.List[j]['y']
            Y.append(y1)
            cv2.circle(Img,(x1,y1),r1,(255,200,0),2)
            
        for i in range(testData.shape[0]):
            r=testData['Radius'][i]
            x=testData['X'][i]
            y=testData['Y'][i]
            cv2.circle(Img,(x,y),r,(0,200,255),2)
        cv2.putText(img=Img, text='Distribution-{Train:Yellow,Test:SeaGreen}', org=(0,780), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 255, 0),thickness=2)
        plt.imshow(Img)
        plt.imsave(os.path.join(self.result_path,'distribution.png'),Img)
        plt.close()
        return(R,X,Y)
    
    def histograms(self,x,y,title,label,color):
        
        #bins=np.linspace(100,300, 100)
        plt.hist(x,bins = 20, label=label[0],color=color[0])
        if y != None:
            plt.hist(y,bins = 20,label=label[1],color=color[1])
        plt.legend(prop={'size': 10})
        plt.title(title)
        plt.savefig(os.path.join(self.result_path,title+'.png'))
        plt.close()
        return
    

    def comparison(self,Inference_path):
        R,X,Y=self.validateDistribution(Inference_path)
        testData=pd.read_excel(os.path.join(Inference_path,"Inference.xlsx"))
        testR=(testData['Radius']/2)
        testX=testData['X']
        testY=testData['Y']
        
        
        self.histograms(R,testR,'Radius Comparison',['Train','Test'],['red','green'])
        self.histograms(X,testX,'X_coor Comparison',['Train','Test'],['blue','orange'])
        self.histograms(Y,testY,'Y_coor Comparison',['Train','Test'],['brown','gold'])
        return
    
    def trainDistribution(self):
        R,X,Y=self.validateImg()  
        self.histograms(R,None,'Radius distribution','Radius',['green'])
        self.histograms(X,None,'X_coor distribution','X',['orange'])
        self.histograms(Y,None,'Y_coor distribution','Y',['gold'])
    
        
            
           