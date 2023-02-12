# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 15:13:52 2022

@author: chggo
"""

import os
from src.topics.loc.common.dataProcessing.dataFormat import DataFormat  
import numpy as np
from src.topics.loc.training.modelTraining.models import Model
from src.topics.loc.training.modelTraining.trainEvaluate import Train
from sklearn import preprocessing
from src.topics.loc.common.dataProcessing.createJson_from_input import input2json
from scikitplot.metrics import plot_confusion_matrix, plot_roc
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import json
import pandas as pd
from src.module.logger import logger
from src.modules.pathHelper import path_resources,path_topicLoc
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings("ignore")
pjoin=os.path.join


# Intialize paths

path= r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData'
result_path=pjoin(path,'result')
checkpoint_path=pjoin(path,'model')
pred_path=pjoin(path,'DumpUnsure')


#.............................................................
# Paths related to inference 
onnx_path=os.path.join(path_topicLoc,'common','resources','loc.onnx')
inputShape_path=os.path.join(path_topicLoc,'common','resources','InputShape.json')
os.chdir(path)


# logging


logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
logger.info('Log Starts')
logger.info('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')



# Parameters

epochs=100
batch_size=4
val=0.15 # validation size
setLimit=90
    
class Main():
    def __init__(self,path,checkpoint_path):
        self.path=path
        self.checkpoint_path=checkpoint_path
      
    def Toarray(self,List,Dta,idx=None,Test=False):
        
        train,test = train_test_split(List, test_size=0.15, random_state=42)
        d_train=Dta.ExtractFromList(train,idx)
        d_test=Dta.ExtractFromList(test,idx)
       
        if idx != 3:
            in_shape=list(d_train[0].shape)
            d_train=Dta.toNumpy(d_train)
            d_test=Dta.toNumpy(d_test)
        else:
            in_shape=0
            d_train=np.array(d_train)
            d_test=np.array(d_test)
        return(d_train,d_test,in_shape)

   
    
    def getData(self,inputShape_path=inputShape_path):
        # get data
        Dta=DataFormat(self.path,setLimit=setLimit) 
        ListTrain,ListPred=Dta.getList(None,None)
        
        # save json
        logger.info('-------------------------------------------------------------------')
        logger.info('trainInput json Saved')
        
        input2json(self.path,ListTrain)
        
        # First Input
        logger.info('-------------------------------------------------------------------')
        logger.info('Preprocess train data')
        C_train,C_test,C_inShape=self.Toarray(ListTrain,Dta,0)
        # Second Input
        B_train,B_test,B_inShape=self.Toarray(ListTrain,Dta,1)
        # Third Input
        P_train,P_test,P_inShape=self.Toarray(ListTrain,Dta,2)
        # Labels
        L_train,L_test,L_inShape=self.Toarray(ListTrain,Dta,3)
        
        # Labels Encoding
        lb = preprocessing.LabelBinarizer()
        L_train = lb.fit_transform(L_train)
        L_test = lb.fit_transform(L_test)
        
        # save shape
        d={'C_inShape':C_inShape,'B_inShape':B_inShape}
       
        with open(inputShape_path, 'w') as outfile1:
            outfile1.write(json.dumps(d))
        
        logger.info('-------------------------------------------------------------------')
        logger.info('InputShape json Saved')
        return(C_inShape,B_inShape,P_inShape,C_train,B_train,P_train,C_test,B_test,P_test,L_train,L_test,Dta,ListPred)
    
    def getModel(self,result_path,val,epochs,batch_size):
        C_inShape,B_inShape,P_inShape,C_train,B_train,P_train,C_test,B_test,P_test,L_train,L_test,Dta,ListPred=self.getData()
        
        # Get Models
        M=Model(C_inShape,B_inShape,P_inShape)
        modelFirst=M.mixedKeras()
        #modelSecond=M.mixedCon()
        
        logger.info('C_train.shape abd type {} and {}:'.format(C_train.shape,type(C_train)))

        # Train Model and get results
        T=Train(self.path,self.checkpoint_path,result_path,False)
        T.trainModel(modelFirst,[C_train,B_train,P_train],L_train,[C_test,B_test,P_test], L_test,'modelFirst_info.png',val,epochs,batch_size)


        #T.trainModel(modelSecond,[C_train,B_train,P_train],L_train,[C_test,B_test,P_test], L_test,'modelSecond_info.png',val,epochs,batch_size)


        # Confusion Matrix
        y_pred= modelFirst.predict([C_test,B_test,P_test])
        y_pred=list(((y_pred>0.5).astype(int)).flatten())
        y_test=list(L_test.flatten())
        fig, ax = plt.subplots(figsize=(4,4))
        plot_confusion_matrix(y_test, y_pred,ax=ax)
        fig.savefig(os.path.join(result_path,'CM.png'))
        
        return(C_inShape,B_inShape,modelFirst,Dta,ListPred)
        
    def makePrediction(self,result_path,val,epochs,batch_size):
        
        # predict for test data(Unseen)
        C_inShape,B_inShape,modelFirst,Dta,ListPred=self.getModel(result_path,val,epochs,batch_size)
                   
        # get Pred data
       
        logger.info('testInput json Saved')
        logger.info('Preproces test data')
        input2json(self.path,ListPred,True)
        
        # Preprocess pred data
    
       
        Cpred,Bpred,Ppred,zipTest=Dta.Toarray_pred(ListPred)
        
        # PREDICT
        logger.info('Cpred.shape abd type {} and {}:'.format(Cpred.shape,type(Cpred)))
        preds = modelFirst.predict([Cpred,Bpred,Ppred])
        #pred2 = modelSecond.predict([Cpred,Bpred,Ppred])
        PredValue=list(((preds>0.5).astype(int)).flatten())
        prob=list(preds.flatten())
        pred_Labels=pd.DataFrame({'filename':zipTest,'labels':PredValue,'probability':prob})
      
        logger.info('Prediction is saved')
        pred_Labels.to_excel(os.path.join(result_path,'prediction.xlsx'))
        return
    
    def saveModel(self,onnx_path=onnx_path):
        
        # save to onnx
        model=os.path.join(self.checkpoint_path,'tmp')
       
        logger.info('ONNX model is saved')
        os.system(f'python -m tf2onnx.convert --keras {model}  --output {onnx_path}')
        return
                

M=Main(path,checkpoint_path)
M.makePrediction(result_path,val,epochs,batch_size)
M.saveModel()
