# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:38:15 2023

@author: chggo
"""

import os
import cv2
import numpy as np
import pandas as pd
import df2img
from zipfile import ZipFile
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from topics.pierce.common.modules.H5ReaderForPiercing import H5Reader
from topics.pierce.common.visualization.processImages import ProcessImages
from matplotlib.pyplot import cm

class ReadData():
    def __init__(self,dataPath=None,resultPath=None,gamma=None):
        self.dataPath=dataPath
        self.resultPath=resultPath
        self.gamma=gamma
    
    def unZip(self,item):
        dumpImg=[]
        h5=None
        if item.endswith('.zip'):
            # read Zip
            file_name=os.path.join(self.dataPath,item)
            zip_ref = ZipFile(file_name)
            listOfFiles = zip_ref.namelist()
            
            for f in listOfFiles :
                
                if f.endswith('.h5') :
                    # read h5
                    f1=zip_ref.open(f)
                    H5File=H5Reader(f1)
                    h5=H5File.readH5()
                   
                    
                if f.endswith('.png') :
                    # read images
                    f2=zip_ref.open(f)
                    string=f2.read()
                    #img=cv2.imdecode(np.frombuffer(string, np.uint8),1) 
                    img=cv2.imdecode(np.frombuffer(string, np.uint8),cv2.IMREAD_ANYDEPTH)    
                    dumpImg.append(img)
                    
        return(h5,dumpImg)
   
    def getGrphsForAll(self):
        Data=[]
        count=0
        for item in os.listdir(self.dataPath): 
            print('{}th dump is being processed'.format(count))
            h5,dumpImg=self.unZip(item)
            
            # read data from h5 and plot
            PI=ProcessImages(dumpImg,self.resultPath,self.gamma)
            idx=PI.pickImages()
            self.getAttributes(h5,idx)
            Im=PI.mergePng(count)
            count += 1
            data={'H5':h5,'images':dumpImg,'Im':Im}
            Data.append(data)
        return(Data)
   
    def getAttributes(self,h5,idx):
        frame=h5['vr']['frame']
        frame=frame-min(frame)
        maxIn=h5['vr']['maxIntensity']
        para=h5['param']
        equipment=h5['paramConfig'].iloc[0,0]
        
        self.plot(frame,maxIn,idx)
        self.summary(para,equipment)
       
        return
    

    def plot(self,frame,maxIn,idx):
        
        figure(figsize=(12, 4.5), dpi=80,facecolor='lavender')
        ax = plt.gca()
        ax.set_facecolor("azure")
        plt.plot(frame,maxIn,color='orangered',label='Intensity')
        color = cm.brg(np.linspace(0, 1,len(idx)))
        for i in range(len(idx)):
            plt.axvline(x = idx[i], color = color[i],ls='--',lw=0.8, label = 'frame'+str(i))
        plt.grid(True,linewidth=0.2)
        plt.title('icpPiercing maxIntensity values w.r.t frames')
        plt.xlabel('frames')
        plt.ylabel('maxIntensity')
        plt.legend(bbox_to_anchor=(0.12,-0.14,1,1.3), loc="upper right")
        plt.savefig(os.path.join(self.resultPath,'maxIn.png'))
        plt.close()
        return
    
    
    
    def summary(self,para,equipment):
        
        # Get the Properties of each dump
        summary={'Parameters':['Laser Power[w]','Nozzle Distance[mm]','Focal Position[mm]','Gas Pressure[bar]','Nominal Speed[mm/min]'],'Cutting':[para['laserPower_0'][0],para['nozzleDistance_0'][0],para['focalPosition_0'][0],para['gasPressure_0'][0],para['nominalSpeed_0'][0]],
                                'Lead In':[para['laserPower_4'][0],para['nozzleDistance_4'][0],para['focalPosition_4'][0],para['gasPressure_4'][0],para['nominalSpeed_4'][0]]}
        df=pd.DataFrame(summary)
    
        mat={'Material Number':[para['materialNumber'][0]],'Thickness':[para['thickness'][0]],'Nozzle Type':[para['nozzleType'][0]],'Equipment Number':[equipment]}
        df1=pd.DataFrame(mat)
        
        self.Table(df,'Parameters',(960,120),'Plot1.png')
        self.Table(df1,'Material Number',(960,60),'Plot2.png')
       
        return
    
    def Table(self,df,ind=None,size=None,name=None):
        
        
        # convert datasets into images
        if ind != None:
            df=df.set_index(ind)
      
        fig = df2img.plot_dataframe(df,
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
        
        nam=os.path.join(self.resultPath,name)
        df2img.save_dataframe(fig=fig, filename=nam)
        return
    
   
                
            
                       
