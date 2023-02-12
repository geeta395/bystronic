# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 12:14:30 2023

@author: chggo
"""

import pandas as pd
import os
import warnings
import tensorflow as tf
from tensorflow import keras
from keras import backend as K
import json
from topics.nozzleControl.training.dataPreprocessing.syntheticData import Synthetic
from topics.nozzleControl.training.dataPreprocessing.dataAugment import DataAugment
from topics.nozzleControl.training.labelling.validateLabels import Validate
from topics.nozzleControl.training.dataPreprocessing.dataFormat import Format_Data
from topics.nozzleControl.training.dataPreprocessing.dataAugment import DataAugment
from topics.nozzleControl.training.modelTraining.model import ModelImg
from topics.nozzleControl.training.modelTraining.model2 import Model
from modules.pathHelper import path_work,path_resources
from topics.nozzleControl.training.modelTraining.trainModel import Training
from topics.nozzleControl.common.visualization.displayCircle import displayCircles 
from topics.nozzleControl.training.confidence_.confidenceScore import Confidence


class Helper():
    def __init__(self,parameters):
        self.parameters=parameters
    
        
    def checkForGPU(self):
        warnings.filterwarnings("ignore")
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


        #Check GPU
        from tensorflow.python.client import device_lib
        print(device_lib.list_local_devices())
        print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

        # Clean Occupied Memeory
        from keras import backend as K
        K.clear_session()
        return
        
        
    def readData(self):
        
        # Read Data
        if self.parameters['synthetic']==True:
            S=Synthetic(self.parameters['total_synthetic_images'])
            List=S.getImg()
            
        else:
            df = pd.read_excel(os.path.join(self.parameters['data_path'],"data","label.xlsx"))
            df1=pd.DataFrame(df, columns=['r','x','y','img'])
            
            # Data preprocessing     
            Dp=DataAugment(df1,self.parameters['data_path'],self.parameters['imgReplicate'])
            if self.parameters['dataAugmentation']:
                List=Dp.List()         
            else:
                List=Dp.labelList()     
        return(List)
    
    def validateInput(self,List):
        
        V=Validate(List,self.parameters['data_path'],self.parameters['result_path'])
        
        # Validate Input
        if self.parameters['validate_Input']:
           V.trainDistribution()
            
        # Validate distribution
        if self.parameters['validate_inference']:
            V.comparison(self.parameters['result_path'])   
            
        return(V)
    
    def preProcess(self,List):
        
        # Preprocess data
        PP=Format_Data(self.parameters['result_path'])
        Img,Radius,X,Y=PP.getInputData(List)
        out=[(Radius[i],X[i],Y[i]) for i in range(len(X))]
        
        
        out=PP.toStack(out,Input=False)
        mean_1,mean_2,mean_3,std_1,std_2,std_3,normOut=PP.normalizeTarget(out)  #Normalize target
        
        #save to json
        self.saveJson( mean_1,mean_2,mean_3,std_1,std_2,std_3)
        return( mean_1,mean_2,mean_3,std_1,std_2,std_3,normOut,Img,PP)
           
    def modelTraining(self, mean_1,mean_2,mean_3,std_1,std_2,std_3,normOut,Img,PP):
        
        # Model 
        MA=ModelImg()
        #MA=Model()
        input1 = keras.Input(shape=Img[1].shape)
        output=MA.imgReg(input1)
        model = keras.Model(input1, output)
        model.summary()
        
        # Training
        T=Training(Img,normOut,self.parameters['result_path'],model,self.parameters['checkpoint_path'],self.parameters['epochs'],self.parameters['batch_size'],self.parameters['randomSeed'])
        y_hat,y_test,X_test=T.Train(self.parameters['intial_lr'])
        
        # Save Model
        model.save(os.path.join(path_work,'topics','nozzleControl','common','resources','imgReg.h5'))
        imageList,predRadius,predX,predY,testRadius,testX,testY,dataTest=self.predict(X_test,y_hat,y_test,mean_1,mean_2,mean_3,std_1,std_2,std_3,PP)
        return( imageList,predRadius,predX,predY,testRadius,testX,testY,dataTest,T)
    
    def predict(self,X_test,y_hat,y_test,mean_1,mean_2,mean_3,std_1,std_2,std_3,PP):
        
        # create test folder
        try: 
            
            path=os.path.join(self.parameters['result_path'],'testResult')
            os.mkdir(path) 
            
        except OSError as error: 
            print(error)  
            
        # save test images
        imageList,predRadius,predX,predY,testRadius,testX,testY,dataTest=PP.save(X_test,y_hat,y_test,mean_1,mean_2,mean_3,std_1,std_2,std_3)
        
        # save prediction
        DC=displayCircles(imageList,predRadius,predX,predY,testRadius,testX,testY)
        DC.Save(self.parameters['result_path'])
    
        return(imageList,predRadius,predX,predY,testRadius,testX,testY,dataTest)
    
    def saveJson(self,mean_1,mean_2,mean_3,std_1,std_2,std_3):
        # save json 
        normalPara={'mean1':mean_1,'mean2':mean_2,'mean3':mean_3,'std1':std_1,'std2':std_2,'std3':std_3}
        with open(os.path.join(path_work,'topics','nozzleControl','common','resources',"normalize.json"), "w") as outfile:
            json.dump(normalPara, outfile)
        return
    
    def visualize(self,List,PP,T,V,imageList,predRadius,predX,predY,testRadius,testX,testY):
        
        # plot histograms of pixel differences
        r_diff,x_diff,y_diff,diff=PP.pixelDiff(predRadius,predX,predY,testRadius,testX,testY)
        V.histograms(r_diff,None,'Radius pixel difference','Radius',['green'])
        V.histograms(x_diff,None,'X-coor pixel difference','X_coor',['red'])
        V.histograms(y_diff,None,'Y-coor pixel difference','Y_coor',['blue'])
        
        # Accuracy
        df_6=PP.accuracy(diff,imageList,allowedPixels=6)
        df_5=PP.accuracy(diff,imageList,allowedPixels=5)
        df_4=PP.accuracy(diff,imageList,allowedPixels=4)
        df=pd.concat([df_4,df_5,df_6])
        
        T.Table(df,'accurcy.png')
        return
        
    def ensemble(self,PP,Img,V,T,normOut,imageList,dataTest):
        # clear session
        K.clear_session()
        import gc
        for i in range(5):
            gc.collect()
            
        # emsemble training
        C=Confidence(Img, normOut,self.parameters['intial_lr'],self.parameters['epochEnsemble'],self.parameters['ensemble_batch_size'],self.parameters['allowedPixels'],self.parameters['heads'],self.parameters['result_path'])
        ensemble,Y_hat,Score,y_test,cs=C.getResult()
        C.plot(cs)
        
        # display result
        DC=displayCircles(imageList,ensemble['r'],ensemble['X'],ensemble['Y'],ensemble['rTest'],ensemble['xTest'],ensemble['yTest'],'ensembleResult')
        DC.Save(self.parameters['result_path'])
        
        
        # saving all predictions
        data=C.savePred(Y_hat)
        
        # see radius predictions for single image
        C.visualize(imgId=0,heads=self.parameters['heads'],dataTest=dataTest,data=data,dataE=ensemble)
            
        with open(os.path.join(self.parameters['result_path'],'allScore.json'), 'w') as f:
            json.dump(Score, f)
            
        # Ensemble Accuracy
        r_en,x_en,y_en,en_diff=PP.pixelDiff(ensemble['r'],ensemble['X'],ensemble['Y'],ensemble['rTest'],ensemble['xTest'],ensemble['yTest'])
        V.histograms(r_en,None,'Radius pixel difference ensemble','Radius',['green'])
        V.histograms(x_en,None,'X-coor pixel difference ensemble','X_coor',['red'])
        V.histograms(y_en,None,'Y-coor pixel difference ensemble','Y_coor',['blue'])
        
        # Accuracy
        en_6=PP.accuracy(en_diff,imageList,allowedPixels=6)
        en_5=PP.accuracy(en_diff,imageList,allowedPixels=5)
        en_4=PP.accuracy(en_diff,imageList,allowedPixels=4)
        en=pd.concat([en_4,en_5,en_6])
        
        T.Table(en,'accurcyEn.png')
        return(data)
                
            