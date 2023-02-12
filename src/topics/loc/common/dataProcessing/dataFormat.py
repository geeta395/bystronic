# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 12:42:55 2022

@author: chggo
"""


import numpy as np
from topics.loc.common.dataProcessing.dataPreprocessing import DataPreProcessing
from topics.loc.machine.dataPreparation.normalize_input import SCALED_PARAMS
from modules.logger import logger

class DataFormat():
    def __init__(self,path,setLimit):
        self.path=path
   
        self.setLimit=setLimit
    
    
    def ExtractFromList(self,lst,idx=None):
        # Extract C,B and para from list
        return [item[idx] for item in lst]
    
    def minLen(self,List):
        # get minimum no. of rows
        minlen=[]
        for element in List:
            minlen.append(element.shape[0])
        return(min(minlen))
    
        
    def adjustShape(self,listData,idx,C_inShape,B_inShape):
        List1=[]
        List=self.ExtractFromList(listData,idx)
       
        if idx ==2 or idx ==3 or idx ==4:
            List1=List
        # select same number of rows for each dataframe in list
        else:
            if C_inShape is None:
                minimum1=self.minLen(List)
                minimum2=self.minLen(List)
            else:
                minimum1=C_inShape[0]
                minimum2=B_inShape[0]
            for element in List:
                Max=element.shape[0]
                if idx==1:
                # for B take last r points
                    element=element.iloc[Max-minimum2:,:]                 
                if idx==0:
                # for C take first r points
                    element=element.iloc[0:minimum1,:]                       
                List1.append(element)
              
            
        return(List1)
    
    def normalize(self,listData,idx,C_inShape,B_inShape):
      
        df1=self.adjustShape(listData,idx,C_inShape,B_inShape)
        if idx==0:
            for df in df1:
                df.iloc[:,0]=df.iloc[:,0]/SCALED_PARAMS['cut_control'][1]
        elif idx==1:
            for df in df1:
                df.iloc[:,0]=df.iloc[:,0]/SCALED_PARAMS['cut_control'][1]
                df.iloc[:,1]=df.iloc[:,1]/SCALED_PARAMS['cut_control'][1]
        else:
            for df in df1:
                df.iloc[:,0]=df.iloc[:,0]/SCALED_PARAMS['nozzle_diameter'][1]
                df.iloc[:,1]=(df.iloc[:,1]-SCALED_PARAMS['nozzle_distance'][0])/(SCALED_PARAMS['nozzle_distance'][1]-SCALED_PARAMS['nozzle_distance'][0])
                df.iloc[:,2]=(df.iloc[:,2]-SCALED_PARAMS['gas_pressure'][0])/(SCALED_PARAMS['gas_pressure'][1]-SCALED_PARAMS['gas_pressure'][0])
                df.iloc[:,3]=df.iloc[:,3]/SCALED_PARAMS['raster'][1]
                df.iloc[:,4]=(df.iloc[:,4]-SCALED_PARAMS['laser_power'][0])/(SCALED_PARAMS['laser_power'][1]-SCALED_PARAMS['laser_power'][0])
                df.iloc[:,5]=df.iloc[:,5]/SCALED_PARAMS['thickness'][1]
                df.iloc[:,6]=(df.iloc[:,6]-SCALED_PARAMS['speed'][0])/(SCALED_PARAMS['speed'][1]-SCALED_PARAMS['speed'][0])
                df.iloc[:,7]=(df.iloc[:,7]-SCALED_PARAMS['focal_position'][0])/(SCALED_PARAMS['focal_position'][1]-SCALED_PARAMS['focal_position'][0])
                
        return(df1)
    
    def processList(self,listData,C_inShape,B_inShape):
        
        labels = self.adjustShape(listData,3,C_inShape,B_inShape)  
       
        Cdata=self.normalize(listData,0,C_inShape,B_inShape)
        Bdata=self.normalize(listData,1,C_inShape,B_inShape)
        para=self.normalize(listData,2,C_inShape,B_inShape)
        zipName=self.adjustShape(listData,4,C_inShape,B_inShape) 
        
        return(Cdata,Bdata,para,labels,zipName)  
    
    def getpreProcessed_data(self,pred):
        
        Cln=DataPreProcessing(self.path,self.setLimit) 
       
        listData_Train,listData_Pred=Cln.makeList(pred)
        return(listData_Train,listData_Pred)
    
    
    
    def getList(self,C_inShape,B_inShape,pred=False):
        L=[]
        Lpred=[]
        
        if pred==False:
          
            listData_Train,listData_Pred=self.getpreProcessed_data(pred)
            # list for training
            
            Cdata,Bdata,para,labels,zipName=self.processList(listData_Train,C_inShape,B_inShape)
            for i in range(len(Cdata)):
                L.append([Cdata[i],Bdata[i],para[i],labels[i],zipName[i]])
                
            # Input shape
            C_inShape=list(Cdata[0].shape)
            B_inShape=list(Bdata[0].shape)
        
            # List for Test
            CdataT,BdataT,paraT,labelsT,zipNameT=self.processList(listData_Pred,C_inShape,B_inShape)
            for i in range(len(CdataT)):
                    Lpred.append([CdataT[i],BdataT[i],paraT[i],labelsT[i],zipNameT[i]])
           
        else:
        # For prediction
            
            listData_Train,listData_Pred=self.getpreProcessed_data(pred)
            CdataT,BdataT,paraT,labelsT,zipNameT=self.processList(listData_Pred,C_inShape,B_inShape)
            for i in range(len(CdataT)):
                    Lpred.append([CdataT[i],BdataT[i],paraT[i],labelsT[i],zipNameT[i]])
                    
            
        return(L,Lpred)
    
    def toNumpy(self,df):
        df=[item.to_numpy() for item in df]
        df=np.asarray(df)
        #df=np.asarray(df).astype('float32')
        return(df)
    
    def Toarray_pred(self,L_test):
        C=self.ExtractFromList(L_test,0)
        B=self.ExtractFromList(L_test,1)
        P=self.ExtractFromList(L_test,2)
        Z=self.ExtractFromList(L_test,4)
        return(self.toNumpy(C),self.toNumpy(B),self.toNumpy(P),Z)
   
    
    
   


