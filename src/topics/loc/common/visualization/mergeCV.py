# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 13:51:36 2022

@author: chggo
"""

import cv2

import os
import pandas as pd
from ...common.visualization import createPlots
import df2img
pjoin=os.path.join



class mergePlot():
    
    def __init__(self,path,result_path):
        self.path=path
        self.result_path=result_path
        
        
    def makeList(self):
        # create list for all graphs which are saved or to be saved
        imageNameList=[]
    
        L=['cut.png','loc.png','recut.png','expose.png','Plot1.png','Plot2.png','Plot3.png','Plot4.png','random1.png','random2.png','random3.png']
        for i in L:
            imageNameList.append(pjoin(self.result_path,i))
        return(imageNameList)

    def Table(self,df,ind=None,size=None,name=None,colW=False):
        
        
        # convert datasets into images
        if ind != None:
            df=df.set_index(ind)
        if colW == True:
            col_width=[1,2]
        else:
            col_width=[1,1,1,1]
        fig = df2img.plot_dataframe(df,col_width=col_width,
        tbl_header=dict(align="right",
            fill_color="purple",
            font_color="white",
            font_size=10,
            line_color="darkslategray",),
        
        tbl_cells=dict(
            align="right",
            line_color="darkslategray",
        ),
        row_fill_color=("#E6E6FA", "#C79FEF"), 
        
        fig_size=size,
        print_index=True, show_fig=False
        )
        
        nam=os.path.join(self.result_path,name)
        df2img.save_dataframe(fig=fig, filename=nam)
        return



    def concat(self,im1,im2,name,im3=None,im4=None,im5=None,mode='vertical'):
        filepath=pjoin(self.result_path,name)
        if mode=='vertical':
            if im3 is None:
                imG=cv2.vconcat([im1,im2])
            else:
                imG=cv2.vconcat([im1,im2,im3,im4,im5])
        else:
            imG=cv2.hconcat([im1,im2])
        cv2.imwrite(filepath, imG)
        
        
 
        
    def saveImg(self,dump,fold,zipName):
        
        Im=[]
        Zip=[]
        
        Py=createPlots.CreatePlots(0.3,dump,self.result_path)
        img1,img2,img3,img4,df,df1,ZipName=Py.getAll(fold,zipName)
        
        for i in zipName:
            Zip.append(i)
            Zip.append(i)
            
        df2=pd.DataFrame({'Title':['Zipfile','DumpNumber'],'dumpId':[Zip[dump],str(int(dump/2))]})
        df3=pd.DataFrame({'Labels' : ['A','B','C'],'Explanation':['Only LOC cut control','Overlap in LOC and Recut cut control','Only Recut cut control']})
        
        self.Table(df,'Parameters',(900,165),'Plot1.png')
        self.Table(df1,'Material Number',(900,80),'Plot2.png')
        self.Table(df=df2,ind='Title',size=(900,90),name='Plot3.png',colW=True)
        self.Table(df=df3,ind='Labels',size=(900,115),name='Plot4.png',colW=True)
        
        imageNameList= self.makeList()
        for j in imageNameList[0:8]:
            im=cv2.imread(j)
            Im.append(im)
        
        self.concat(Im[0],Im[3],'random1.png')
        s1=cv2.imread(pjoin(self.result_path,'random1.png'))
        self.concat(Im[1],Im[2],name='random2.png',mode='horizontal')
        s2=cv2.imread(pjoin(self.result_path,'random2.png'))
        self.concat(im1=s2,im2=Im[5],im3=Im[4],name='random3.png',im4=Im[6],im5=Im[7])
        s3=cv2.imread(pjoin(self.result_path,'random3.png'))
       
        
        nam1='Preview' +'_'+str(dump)+'.'+'png'
        self.concat(im1=s1,im2=s3,name=nam1,mode='horizontal')
        self.remove(imageNameList)
      
        return
    
    def remove(self,imageNameList):
      for i in imageNameList:
          os.remove(i)
          
          

