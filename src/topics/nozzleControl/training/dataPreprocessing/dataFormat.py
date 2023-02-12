# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 15:38:07 2022

@author: chggo
"""

import numpy as np
import cv2
import pandas as pd
import os
import matplotlib.pyplot as plt
pjoin=os.path.join

class Format_Data():
    def __init__(self,result_path):
        self.result_path=result_path
    
    # To Tensor
    def toStack(self,a,Input=True):  
        a1=np.array(a)
        a2=np.stack(a1, axis=0)
        if Input==True:
            a2 = a2[:, :, :, np.newaxis]
        return(a2)


    # Get raw input data for model
    def getInputData(self,listAugmented):
        Img=[]
        Radius=[]
        X=[]
        Y=[]
       
        for i in range(len(listAugmented)):
            Img.append(listAugmented[i]['img'])
            Radius.append(listAugmented[i]['r'])
            X.append(listAugmented[i]['x'])
            Y.append(listAugmented[i]['y'])
            
            
        Img=self.toStack(Img)
   
        return(Img,Radius,X,Y)
    
    # Normalize Target
    def normalizeTarget(self,out):
        # Normalize target data
        
        m1=np.mean(out[:,0])
        m2=np.mean(out[:,1])
        m3=np.mean(out[:,2])
        
        s1=np.std(out[:,0])
        s2=np.std(out[:,1])
        s3=np.std(out[:,2])
        
        C1=(out[:,0]-m1)/s1
        C2=(out[:,1]-m2)/s2
        C3=(out[:,2]-m3)/s3
       
        normOut=np.transpose(np.vstack((C1,C2,C3)))
        return(m1,m2,m3,s1,s2,s3,normOut)


    def UnNormalized(self,y_hat,y_test,m1,m2,m3,s1,s2,s3):
        # get back real traget
        predRadius = list(2*(s1*y_hat[:,0] + m1))
        predX = list(2*(s2*y_hat[:,1] + m2))
        predY = list(2*(s3*y_hat[:,2] + m3))

        predRadius=[int(i) for i in predRadius]
        predX=[int(i) for i in predX]
        predY=[int(i) for i in predY]

        # Test data
        testRadius = list(2*(s1*y_test[:,0] + m1))
        testX = list(2*(s2*y_test[:,1] + m2))
        testY = list(2*(s3*y_test[:,2] + m3))

        testRadius=[int(i) for i in testRadius]
        testX=[int(i) for i in testX]
        testY=[int(i) for i in testY]
        return(predRadius,predX,predY,testRadius,testX,testY)
    
    def save(self,X_test,y_hat,y_test,m1,m2,m3,s1,s2,s3):

        # Get back data (unnormalized)
        predRadius,predX,predY,testRadius,testX,testY=self.UnNormalized(y_hat,y_test,m1,m2,m3,s1,s2,s3)
        h,w=X_test[0].shape[:2]
        imageList=[]
        for i in range(len(X_test)):
            filename=pjoin(self.result_path,'testResult','img_'+str(i)+'.png')
         
            img=cv2.resize(X_test[i],(w,h))
            img=(cv2.resize(255*X_test[i], None, fx = 2, fy = 2))
        
            cv2.imwrite(filename,img)
            #plt.imsave(filename,img,cmap='jet')
            imageList.append(filename)
            
        data={'RadiusPred':predRadius,'radiusTest':testRadius,'predX':predX,'testX':testX,'predY':predY,'testY':testY,'Image':imageList}
        Data=pd.DataFrame(data)  
        Data.to_excel(pjoin(self.result_path,'testLabels.xlsx'))
        return(imageList,predRadius,predX,predY,testRadius,testX,testY,Data)

    def pixelDiff(self,predRadius,predX,predY,testRadius,testX,testY):
        
        r_diff=[np.abs(predRadius[i]-testRadius[i]) for i in range(len(predRadius))]
        x_diff=[np.square(predX[i]-testX[i]) for i in range(len(predRadius))]
        y_diff=[np.square(predY[i]-testY[i]) for i in range(len(predRadius))]
        diff=pd.DataFrame({'r':r_diff,'x':x_diff,'y':y_diff})
        return(r_diff,x_diff,y_diff,diff)
    
    def accuracy(self,diff,imageList,allowedPixels):
        count=0
        for i in range(diff.shape[0]):
          if diff.iloc[i,0]>allowedPixels or np.sqrt(diff.iloc[i,1]+diff.iloc[i,2])>allowedPixels:
            count=count+1
        acc=(len(imageList)-count)/len(imageList)
        print('accuracy with {} pixels error is {}'.format(allowedPixels,acc))
        print('total faulty images are {} out of {}'.format(count,len(imageList)))
        df=pd.DataFrame({'allowedPixels':[allowedPixels],'accuray':[acc],'faultyPrediction':[count],'TotalPredictions':[len(imageList)]})
        return(df)