# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:33:00 2022

@author: chggo
"""



# Create dynamic plots from the DumpReader data 

import numpy as np
import pandas as pd
import kaleido
import os

import plotly.express as px
import plotly.io as pio

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from topics.loc.common.dataProcessing.dumpReader import dumpReader

class CreatePlots():
    def __init__(self,thresh,dump,result_path):
    
       self.thresh=thresh
       self.result_path=result_path
       self.dump=dump
       
    
    def getdata_for_charts(self,fold):
        
        #  Collecte the well structured data for the dump=i 
        
        fold1=fold[self.dump:self.dump+2]
        chart=dumpReader(self.thresh, fold1)
        X_loc,Y_loc,Loc,X_re,Y_re,Re,a,b,B,Time,Btime,Bcut,Bre,Cre,para,paraConf,vr,TimeLoc,Ctime,Es,Rs=chart.getData(fold1[0],fold1[1])
        
        
        return(X_loc,Y_loc,Loc,X_re,Y_re,Re,a,b,B,Time,Btime,Bcut,Bre,Cre,para,paraConf,vr,TimeLoc,Es,Rs)
    
    
    
    
    
    def summary(self,para,paraConf,Es,Rs):
        
        # Get the Properties of each dump
        summary={'Parameters':['Laser Power[w]','Nozzle Distance[mm]','Focal Position[mm]','Gas Pressure[bar]','Nominal Speed[mm/min]','EffectiveSpeed[mm/min] (RelativeSpeed[%])'],'Cutting':[para['laserPower_0'][0],para['nozzleDistance_0'][0],para['focalPosition_0'][0],para['gasPressure_0'][0],para['nominalSpeed_0'][0],'{} ({})'.format(Es,Rs)],
                                'Lead In':[para['laserPower_4'][0],para['nozzleDistance_4'][0],para['focalPosition_4'][0],para['gasPressure_4'][0],para['nominalSpeed_4'][0],None]}
        df=pd.DataFrame(summary)
    
        mat={'Material Number':[para['materialNumber'][0]],'Thickness':[para['thickness'][0]],'Nozzle Type':[para['nozzleType'][0]],'Equipment Number':[paraConf['equipmentNummer'][0]]}
        df1=pd.DataFrame(mat)
    
       
        return(df,df1)
    

    
    def loc_Plot(self,X_loc,Y_loc,Loc,r,exist=None):
        
        # Creates LOC graph , 'exist' variable checks for 'B' sequence
        
        p1=px.scatter(x=X_loc,y=Y_loc,color=Loc,labels={'x':'X-coordinate','y':'Y-coordinate'},title="LOC Dump",width=450, height=450)
        p1.add_trace(go.Scatter(x=[X_loc[0]], y=[Y_loc[0]],marker=dict( color='darkOrange', size=20),name='LOC Starts-A', mode = 'markers',marker_symbol = 'circle'))
        if exist is not None:
            p1.add_trace(go.Scatter(x=[X_loc[r]], y=[Y_loc[r]],marker=dict( color='darkGreen', size=20),name='Recut Starts-B', mode = 'markers',marker_symbol = 'circle'))
        p1.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right", x=1))
        r1=np.ptp(X_loc) # range
        r2=np.ptp(Y_loc)
        if r1>r2:
            d=round(r1/10)
        else:
            d=round(r2/10)
        p1.update_xaxes(scaleanchor = "y",scaleratio = 1,dtick=d)    # balance aspect ratio
        loc=os.path.join(self.result_path,"loc.png")
        pio.write_image(p1,loc ,engine='kaleido')
        return(p1)
            
    def Recut_Plot(self,X_re,Y_re,Re,a=None,b=None,exist=None):
        
        # Creates Recut graph, 'a' checks for "C" sequence
        
        p1=px.scatter(x=X_re,y=Y_re,color=Re,labels={'x':'X-coordinate','y':'Y-coordinate'},title="Recut Dump")
        if exist is not None:
            p1.add_trace(go.Scatter(x=[X_re[0]], y=[Y_re[0]],marker=dict( color='darkGreen', size=20),name='Recut Starts-B', mode = 'markers',marker_symbol = 'circle'))
        if a is not None:
            p1.add_trace(go.Scatter(x=[a], y=[b],marker=dict( color='yellowgreen', size=20),name='C Starts', mode = 'markers',marker_symbol = 'circle'))
        p1.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right", x=1),width=450, height=450)
        r1=np.ptp(X_re)  # range 
        r2=np.ptp(Y_re)
        if r1>r2:
            d=round(r1/10)
        else:
            d=round(r2/10)
        p1.update_xaxes(scaleanchor = "y",scaleratio = 1,dtick=d)  # balance aspect ratio
        # save image 
        loc=os.path.join(self.result_path,"recut.png")
        pio.write_image(p1,loc,engine='kaleido')
        return(p1)
            
    def cutcontrol_Plot(self,Time,Btime,Bcut,Loc,Bre,Cre,TimeLoc):
        
        # Create cutcontrol graph
        R=Bre+Cre
        if (len(Bcut) !=0):
            s=Btime[len(Btime)-1]
        else:
            s=Time[-1]
        Time[:] = [(num - s)/1000000 for num in Time]   # start time where LOC stops
        TimeLoc[:]=[(num - TimeLoc[-1])/1000000 for num in TimeLoc]   
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout()
        

        trace1=go.Scatter(x=TimeLoc,y=Loc,name='LOC starts from A',xaxis='x1',yaxis='y1',marker=dict(color='darkOrange'))  
        trace2 = go.Scatter(x=Time,y=R,name='Recut (B+C)',xaxis='x1',yaxis='y2',marker=dict(color='darkGreen')) # x2
        
        #data = [trace1, trace2]

           
        fig.add_trace(trace1,secondary_y=False)
        fig.add_trace(trace2,secondary_y=True)
        fig.update_layout(title = 'Cut Control Graph from Ecat',legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right", x=1),width=900, height=450,xaxis_title="Time Stamp from Ecat",yaxis_title="Loc cut control",yaxis2_title='Recut cut control') #,xaxis2= {'overlaying': 'x', 'side': 'top'})
    
        loc=os.path.join(self.result_path,"cut.png")
        pio.write_image(fig, loc,engine='kaleido')
        return(fig,Time,TimeLoc)
    
    def expIntensity_plot(self,vr,Time,TimeLoc):
        maxI=vr['maxIntensityAvrg']
        expose=vr['exposure']
        X=vr['tsBeckhoff'].to_list()
        X[:] = [(num - X[-1])/1000000 for num in X] 
    
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
     
        trace1=go.Scatter(x=X,y=maxI,name='maxIntensityAvrg',xaxis='x1',yaxis='y1',marker=dict(color='yellowgreen'))
        trace2 = go.Scatter(x=X,y=expose,name='exposure',xaxis='x1',yaxis='y2',marker=dict(color='slateblue'))
       
        fig.add_trace(trace1)
        fig.add_trace(trace2,secondary_y=True)
        fig.update_layout(title = 'Exposure/Intensity Graph from Vr Loc',legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right", x=1),width=900, height=450,xaxis_title="Time Stamp",yaxis_title="Max Intensity",yaxis2_title='Exposure',xaxis_range=[min(min(TimeLoc),min(Time)),max(max(Time),max(TimeLoc))]),
        loc=os.path.join(self.result_path,"expose.png")
        pio.write_image(fig,loc,engine='kaleido')
        return(fig)
        
    def getAll(self,fold,ZipName):
        
        X_loc,Y_loc,Loc,X_re,Y_re,Re,a,b,B,Time,Btime,Bcut,Bre,Cre,para,paraConf,visionResult,TimeLoc,EffectiveSpeed,RelativeSpeed=self.getdata_for_charts(fold)
        
        df,df1=self.summary(para,paraConf,EffectiveSpeed,RelativeSpeed)
        
        r=min(range(len(X_loc)), key=lambda k: abs(X_loc[k]-X_re[0]))
        img1,Time,TimeLoc=self.cutcontrol_Plot(Time,Btime,Bcut,Loc,Bre,Cre,TimeLoc)
        img2=self.loc_Plot(X_loc,Y_loc,Loc,r,exist=B)
        img3=self.Recut_Plot(X_re,Y_re,Re,a,b,exist=B)
        img4=self.expIntensity_plot(visionResult,Time,TimeLoc)
        
        return(img1,img2,img3,img4,df,df1,ZipName)



