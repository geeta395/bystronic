# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 15:31:34 2022

@author: chggo
"""

import os
import math
import numpy as np
import pandas as pd
from modules.logger import logger
from .dumpReader import dumpReader
from ...common.modules.dump_helper_with_labels import dump_helper_with_labels
from ...common.modules.H5Reader import *
from ...common.modules.dump_helper import DumpHelper



class DataPreProcessing():
    def __init__(self,path,setLimit):
        self.path=path
        self.setLimit=setLimit
       
    
    def sinCos(self,X,Y):
        
        angle=np.arctan2(Y,X)
        sin = [math.sin(l)/2.0+0.5 for l in angle]
        cos = [math.cos(m)/2.0+0.5 for m in angle]
        
        return(sin,cos)
    
    def reSample(self,e,timeStamp):
        # Predict VeloX and veloY using timestamp
        df=pd.DataFrame({'veloX':e.veloX}) 
        df1=pd.DataFrame({'veloY':e.veloY}) 
        dfResampled = df.reindex(df.index.union(timeStamp)).interpolate('values').loc[timeStamp]    
        dfResampled1 = df1.reindex(df1.index.union(timeStamp)).interpolate('values').loc[timeStamp]    
        d1=list(dfResampled['veloX'])
        d2=list(dfResampled1['veloY'])
        return (d1,d2)
        
    def dataCollect(self,fold1,ecat_loc,ecat_re):
        
        chart=dumpReader(0.3, fold1)
        X_loc,Y_loc,Loc,X_re,Y_re,Re,a,b,B,Time,Btime,Bcut,Bre,Cre,para,paraConf,vr,TimeLoc,Ctime,Es,Rs=chart.getData(fold1[0],fold1[1])

        CreX,CreY=self.reSample(ecat_loc,Ctime)

        BcutX,BcutY=self.reSample(ecat_loc,Btime)
        
        # direction varibables
        sinC,cosC = self.sinCos(CreX,CreY)
        sinB,cosB = self.sinCos(BcutX,BcutY)
        
        # Prepare input data C,B and para
        
        Cdata=pd.DataFrame({'cutControl':Cre,'sinC':sinC,'cosC':cosC})
        Bdata=pd.DataFrame({'locCut':Bcut,'reCut':Bre,'sinB':sinB,'cosB':cosB})
        param=para.iloc[:,[1,2,5,7,8,10,13,15]]
        
       
        
        return(Cdata,Bdata,param)
    
    
    def getEcat(self,f):
       H5File=H5Reader(f)  
       h5=H5File.readH5()
       return(h5['ecat'])
    
    def makeList(self,pred):
  
        if pred==False:
            
            H55=dump_helper_with_labels(self.path)
            fold,labels,foldTest,ZipName,zipTest=H55.createFolder()
           
            listData_Train=self.structureList(fold,labels,ZipName)
            listData_Pred=self.structureList(foldTest,None,zipTest)
        else:
          
            G=DumpHelper(self.path)
          
            foldTest,zipTest=G.checkEmpty()
            
            labels=None
            listData_Train=None
            listData_Pred=self.structureList(foldTest,None,zipTest)
    
            
       
        return(listData_Train,listData_Pred)
    
    def structureList(self,fold,labels,Zip):
        listData=[]
        j=0
        for i in range(0,len(fold),2):
            print('.......................................................')
            print('{}th dump is being processed'.format(i))
            
           
            
            print('.......................................................')
            fold1=fold[i:i+2]
            ecat_loc=self.getEcat(fold1[0])
            ecat_re=self.getEcat(fold1[1])
            Cdata,Bdata,param=self.dataCollect(fold1,ecat_loc,ecat_re)
            if labels != None:
        
                listData.append([Cdata,Bdata,param,labels[j],Zip[j]])  
                j=j+1
                
            
            else:
                listData.append([Cdata,Bdata,param,None,Zip[j]]) 
                j=j+1
        listData=([i for i in listData if (i[0].shape[0] >self.setLimit and i[1].shape[0] >self.setLimit)])
        
        return(listData)
 
