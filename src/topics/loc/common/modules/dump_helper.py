# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 10:27:36 2022

@author: chggo
"""
#Get .h5 files from all the zip files given in the "path"
 

import os
from zipfile import ZipFile
from topics.loc.common.modules.H5Reader import H5Reader
from modules.logger import logger


setLimit=90

class DumpHelper():
    def __init__(self,path):
        #self.result_path=result_path
        self.path=path
        
        
    def processDumpFromFile(self,file_name):
        zip_ref = ZipFile(file_name)
        fn_h5_cut, fn_h5_recut=self.get_H5_file_names(zip_ref)
        zip_ref.close() 
        return(fn_h5_cut, fn_h5_recut)
        
   
        
    def get_H5_file_names(self,zip_ref):
        
        dup_loc=[]
        dup_recut=[]
        listOfFiles = zip_ref.namelist()
        count=0
        opd=os.path.dirname
        
        for f in listOfFiles :
            
            if f.endswith('.h5') and opd(f)=='data/lossOfCutDetected':
                logger.info('{} file is opened'.format(f))
                f2=zip_ref.open(f) 
                dup_loc.append(f2)
                count=count+1
            elif f.endswith('.h5') and opd(f)=='data/lossOfCutRecut':
                logger.info('{} file is opened'.format(f))
                f2=zip_ref.open(f) 
                dup_recut.append(f2)
               
                count=count+1
        if count !=2 :     
    
            print(' WARNING ..............................................................................')
            print('More than two .h5 files')
      
        return(dup_loc[-1],dup_recut[-1])

            
        
    def unZipLS(self):
        fold=[]
        ZipName=[]
        
        for item in os.listdir(self.path):                
            if item.endswith('.zip'):
                
                #file_name = os.path.abspath(item)    
                file_name=os.path.join(self.path,item)
                f1,f2=self.processDumpFromFile(file_name)
                fold.append(f1) 
                fold.append(f2) 
                ZipName.append(item)
        return(fold,ZipName)
    
    def empty(self,fold1,setLimit):
        
        ffold=[]
        H5File=H5Reader(fold1[0])
        h5=H5File.readH5()
       
        ecat=h5['ecat']
        
        if ecat.shape[0]>setLimit:
            logger.info('.h5 files have sufficient points')
            ffold.append(fold1[0])
            ffold.append(fold1[1])
        else:
            logger.info('.h5 files do not have sufficient points')
        return(ffold)
    
    def checkEmpty(self,points=90):
        
        fold,ZipName=self.unZipLS()
        j=0
        ffold=[]
        zzip=[]
        for i in range(0,len(fold),2):
            fold1=fold[i:i+2]
            ff=self.empty(fold1,points)
            if len(ff) != 0:
                ffold.append(ff[0])
                ffold.append(ff[1])
                zzip.append(ZipName[j])
            j=j+1
        return(ffold,zzip)

