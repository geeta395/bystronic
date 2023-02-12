#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 10:28:24 2022

@author: chggo
"""

from modules.pathHelper import path_work,path_resources
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint
from keras import backend as K
import keras
import pandas as pd
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from keras import backend as K
from scipy import stats as st
import gc



class Confidence():
    def __init__(self,Img,normOut,lr,epochs,batch_size,allowedPixels,heads,result_path):
        self.Img=Img
        self.normOut=normOut
        self.lr=lr
        self.epochs=epochs
        self.batch_size=batch_size
        self.allowedPixels=allowedPixels
        self.heads=heads
        self.result_path=result_path
        
        
    def rmse(self,y_true, y_pred):
        R=K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))
        
        return R

    def coeff_determination(self,y_true, y_pred):
        SS_res =  K.sum(K.square( y_true-y_pred ))
        SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
        return ( 1 - SS_res/(SS_tot + K.epsilon()) )


    def trainPredict(self,checkpoint_path):
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(self.Img,self.normOut, test_size=0.1,random_state=42)
       
        # Load model
        model = keras.models.load_model(os.path.join(path_work,'topics','nozzleControl','common','resources','imgReg.h5'),custom_objects={'rmse':self.rmse,'coeff_determination':self.coeff_determination},compile=True) 
        
       
        # freeze convolution part
        for layer in model.layers[:21]:
            layer.trainable=False
       
        checkpoint = ModelCheckpoint(checkpoint_path, monitor='loss',save_weights_only=True,verbose=1, save_best_only=True, mode='min')
      
        callbacks_list = [checkpoint]  
    
       
        # fit model
        model.fit(X_train,y_train,epochs=self.epochs,shuffle=True,batch_size=self.batch_size,validation_split=0.1,callbacks=callbacks_list)
        
        # Evaluate
        score = model.evaluate(X_test,y_test, verbose=2)
        score = {'loss':score[0],'rmse':score[1],'Coeff_det':score[2]}
        y_hat = model.predict(X_test)
        y_hat=self.UnNormalized(y_hat)
        y_test=self.UnNormalized(y_test)
        CS=self.confidenceScore(y_hat, y_test)
        y_hat['cs']=CS
        
        #release memory
        del model
        K.clear_session()
        for i in range(10):
            gc.collect()
       
        return(y_hat,y_test,score)
    
    def UnNormalized(self,y_hat):
        
        with open(os.path.join(path_work,'topics','nozzleControl','common','resources','normalize.json'), 'r') as openfile:
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
        
        y_hat = {'r':predRadius,'X':predX,'Y':predY}
        
        return(y_hat)
    
    def confidenceScore(self,y_hat,y_test):
        
        r_diff=[np.abs(y_hat['r'][i]-y_test['r'][i]) for i in range(len(y_hat['r']))]
        x_diff=[np.square(y_hat['X'][i]-y_test['X'][i]) for i in range(len(y_hat['r']))]
        y_diff=[np.square(y_hat['Y'][i]-y_test['Y'][i]) for i in range(len(y_hat['r']))]
        CS=[]
        for i in range(len(r_diff)):
          if r_diff[i]> self.allowedPixels or np.sqrt(x_diff[i]+y_diff[i])>self.allowedPixels:
              CS.append(0)
          else:
              CS.append(1)
        return(CS)
        
        
    def loopOver(self):
        Y_hat=[]
        Score=[]
        for i in range(self.heads):
            print('training sample number : {}'.format(i))
            checkpoint_path=os.path.join(path_resources,'head_'+str(i)+'.h5')
            y_hat,y_test,score=self.trainPredict(checkpoint_path)
            Y_hat.append(y_hat)
            Score.append(score)
            
        return(Y_hat,Score,y_test)
    
    def getWeights(self,Score):
        # find weights using score
        S=[]
        S1=0
        for i in range(len(Score)):
            loss=Score[i]['loss']
            S1=S1+loss
            S.append(loss)
        S=[round(x/S1,4) for x in S]
        return(S)
    
    def getAverage(self,Y_hat,col,S=None):
        # weighted sum
        l=len(Y_hat)
        Sum=[]
        for i in range(l):
            if col=='cs':
                listt= Y_hat[i][col]
            else:
                #mode=st.mode(Y_hat[i][col])
                listt= [S[i]*k for k in Y_hat[i][col]]
            Sum.append(listt)
        avg=sum(map(np.array, Sum))  # don't divide by l as alreday weighted 
        if col=='cs':
            avg=np.round_(avg,2)
        else:
            avg=np.round(avg)
      
        return(avg)
    
    def getResult(self):
        Y_hat,Score,y_test=self.loopOver()
        S=self.getWeights(Score)
        avgCS=self.getAverage(Y_hat,'cs')
        avgR=self.getAverage(Y_hat,'r',S)
        avgX=self.getAverage(Y_hat,'X',S)
        avgY=self.getAverage(Y_hat,'Y',S)
        en={'r':avgR,'rTest':y_test['r'],'X':avgX,'xTest':y_test['X'],'Y':avgY,'yTest':y_test['Y'],'cs':avgCS}
        ensemble=pd.DataFrame(en)
        ensemble.to_excel(os.path.join(self.result_path,'ensembleResult.xlsx'))
        cs=ensemble['cs']
        
        return(ensemble,Y_hat,Score,y_test,cs)

    def plot(self,cs):
        
        values,counts=np.unique(cs,return_counts=True)
        sns.set_style('darkgrid')
        ax = sns.barplot(x=values, y=counts, hue=[round(cs[cs == val].mean(),2) for val in values],
                         palette='turbo', dodge=False) #width=0.2)
        for i in range(len(values)):
            ax.bar_label(ax.containers[i],color='red',fontsize=10)
      
        plt.title('confidence score')
        plt.xlabel('CS score')
        plt.ylabel('Number of predictions')
        plt.savefig(os.path.join(self.result_path,'confidenceScore'+'.png'))
        plt.show()
        plt.close()
    
        return
    
    def savePred(self,Y_hat):
        dfs = []
        for i in range(len(Y_hat)):
            d=pd.DataFrame(Y_hat[i])
            d.rename(columns={'r':'r_'+str(i),'X':'x_'+str(i),'Y':'y_'+str(i),'cs':'cs_'+str(i)},inplace =True)
            #d['empty'] = np.nan
            dfs.append(d)
        data = pd.concat(dfs, axis=1)
        data.to_excel(os.path.join(self.result_path,'allPredictions.xlsx'))
        return(data)
    
    def visualize(self,imgId,heads,dataTest,data,dataE):
        for i in range(heads):
            if i==0:
                plt.plot([i],data['r_'+str(i)][imgId], marker="o", markersize=10,color='green',label='heads')
            else:
                plt.plot([i],data['r_'+str(i)][imgId], marker="o", markersize=10,color='green')
        plt.plot([i+1],dataTest['RadiusPred'][imgId],marker='*',markersize=10,color='orange',label='Single model')
        plt.plot([i+1],dataE['r'][imgId],marker='p',markersize=10,color='gold',label='Ensemble')
        plt.plot([i+1],dataE['rTest'][imgId],marker='D',markersize=10,color='red',label='True')
        plt.axhline(y=dataE['rTest'][imgId]-2,color='b',label='limit',ls='--',lw=1)
        plt.axhline(y=dataE['rTest'][imgId]+2,color='b',ls='--',lw=1)
        plt.xlim(-1, heads+4)
        leg=plt.legend(loc=0,prop={'size': 8},fancybox = True)
        plt.title('Predicted radius by different model setting for image : {}'.format(str(imgId)))
        plt.savefig(os.path.join(self.result_path,'predictedRadius.png'))
        return

#C=Confidence(Img, normOut, lr=intial_lr,epochs=5,batch_size=BS,allowedPixels=5,heads=5,result_path=result_path)
#enesemble,Y_hat,Score,y_test=C.getResult()


    
