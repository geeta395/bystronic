
 # -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 11:31:33 2022

@author: chggo
"""



import os
import math
import pandas as pd
import numpy as np
from numpy import linalg as LA
from ...common.modules.H5Reader import H5Reader



class dumpReader:
    def __init__(self,thresh,folder1):
    
       self.thresh=thresh
       self.folder1=folder1
       
    def read_H5(self,file):
    
        # read h5 files
        H5File=H5Reader(file)  
        h5=H5File.readH5()
        ecat=h5['ecat']
        para=h5['param']
        paraConf=h5['paramConfig']
        visionResult=h5['vr']
        # get coordinates of location and cut control/time values
        
        posX=ecat['posX'].tolist()
        posY=ecat['posY'].tolist()
        
        # time stamp
        time=ecat['tsBeckhoff'].tolist()
        variable=ecat['cutcontrol'].tolist()   # select the column that you want to predict
        return(ecat,posX,posY,variable,time,para,paraConf,visionResult)  
    
    
    
    def predictVar(self,p1,p2,target,var1,var2):
        
        # predict cut control value for point 'target' which lies b/w points (p1,p2)
        d1=math.dist(p1,target)       # eculidean distance 
        d2=math.dist(p1,p2)
        
        if d2 !=0:
            tar1=var1+(d1/d2)*(var2-var1)
        else:
            tar1=var1
        
        return (tar1)
   
    def opertion(self,a,b,op='add'):
        
        # adding or subtracting two lists
        if (op=='add'):
            res=[a_i + b_i for a_i, b_i in zip(a, b)]
        elif (op=='sub'):
            res=[a_i - b_i for a_i, b_i in zip(a, b)]
        elif (op=='div'):
            res=[a_i/b_i for a_i, b_i in zip(a, b)]
        return(res)
        
    def delta(self,p1,p2):
        
        # get unit normal vector to point p1
        
        delY=p2[1]-p1[1]
        delX=p2[0]-p1[0]
        v=[-delY,delX]      
        veC=self.opertion(p2,p1,'sub')              # direction vec
        l=LA.norm(v)                             # L2 norm
        
        v=v/l 
                                       # unit vector
        
        return(v*self.thresh,veC)
    
    def areaTriangle(self,a,b,c):
        
        # finds area of a triangle given 3 points
        A=np.abs(a[0]*(b[1]-c[1])+b[0]*(c[1]-a[1])+c[0]*(a[1]-b[1]))
        return(A/2.0)
    
    def Triangle(self,a,b,c,target):
        
        # checks if point lies in the triangle
        A=self.areaTriangle(a, b, c)
        A1=self.areaTriangle(a, target, c)
        A2=self.areaTriangle(a, target, b)
        A3=self.areaTriangle(b, target, c)
        
        Sum=A1+A2+A3
        
        t = math.isclose(A,Sum)    # comparing two float values
        if (t):
            tar=1
        else: 
            tar=0
        return(tar,A,Sum)
    
    def getPoints(self,p1,p2):
        
       
        v,veC=self.delta(p1,p2)    # get unit normal vector
        
        # get corner points of the rectangle 
        a1=self.opertion(v,p1,'add') 
        a2=self.opertion(a1,veC,'add') 
        a3=self.opertion(p1,v,'sub') 
        a4=self.opertion(a3,veC,'add') 
        
        return (a1,a2,a3,a4)
        
    
    def between(self,p1,p2,target):
        
      
        # get points
        a1,a2,a3,a4=self.getPoints(p1,p2)
        
        # check if point(target) lies b/w p1 and p2 by dividing the rectangle into two triangles
        tar1,G,sum1=self.Triangle(a1,a2,a3,target)
        tar2,K,sum2=self.Triangle(a2,a3,a4,target)
        
        if(tar1+tar2 != 0):
            tar=1
        else:
            tar=0
        
        return(target[0],target[1],tar)
        
        
        
    def checkOverlap(self,L1,R1,L2,R2):
        
        # checks if overlapping happanes in the dump
        
        target=[L2[0],R2[0]]
        startingPoint=0
        over=0
        
        for i in range(len(L1)-1):
            p1=[L1[i],R1[i]]
            p2=[L1[i+1],R1[i+1]]
            x,y,val=self.between(p1,p2,target)
            if (val!=0):
                print( 'overlapping exist at {}th loc position'.format(i))
                #logger.info('-------------------------------------------------------------------')
                #logger.info('Synchronize LOC and Recut Data')
                #logger.info( 'overlapping exist at {}th loc position'.format(i))
                over=1
                break
            
        if (over!=1):
            for j in range(len(L2)-1):
                
                target1=[L2[j],R2[j]]
                
                # Fix first two points in loc
                p1=[L1[0],R1[0]]
                p2=[L1[1],R1[1]]
                
                x,y,val1=self.between(p1,p2,target1)
    
                
                if (val1 !=0):
                    print('overlapping exist at {}th recut position'.format(j))
                    over=1
                    startingPoint=j
                    break
                
        if(over==0):
            print('No overlapping exists')
    
        return(startingPoint)


        
    def sync(self,L1,R1,L2,R2,cutloc,cutre,timeloc,time_re):
        
        # (L1,R1) the list of refrence values (loc)
        # (L2,R2) list of values for prediction (recut)
        
                
        sP=self.checkOverlap(L1,R1,L2,R2)
        
        L2=L2[sP:]
        R2=R2[sP:]
        
        List=[]
       
        m=len(L1)
        n=len(L2)
        strt=0
        overlap=0
        
        for j in range(0,n):
            
            i=strt   
           
            while i <= m-2:    
                
                p1=[L1[i],R1[i]]
                p2=[L1[i+1],R1[i+1]]
                target=[L2[j],R2[j]]
                c1=cutloc[i]
                c2=cutloc[i+1]
                t1=timeloc[i]
                t2=timeloc[i+1]
                
                
                x,y,val=self.between(p1,p2,target)
                i += 1
                
                if (val != 0):     # between pass                      
                    value=self.predictVar(p1,p2,target,c1,c2)
                    tm=self.predictVar(p1,p2,target,t1,t2)
                    List.append([x,y,value,cutre[j],tm,time_re[j],'B'])                   # pass the predicted cut control value
                    strt=i-1
                    overlap=1
                    jj=j
                    break
                    
                elif((overlap==0) and (val==0)): # between fails
                    List.append([p1[0],p1[1],c1,'nan',t1,'nan','A'])                      # pass the loc cut control value
                    
                    
                    if(i==m-2):
                        List.append([p2[0],p2[1],c2,'nan',t2,'nan','A']) 
                        strt=m-1
                        
            if (overlap==1) and (strt==m-2) and (jj<j<n) :        
                 List.append([L2[j],R2[j],'nan',cutre[j],'nan',time_re[j],'C'])           # pass the recut control value
                
            if (overlap==0) and (strt==m-1) and (j<n):        
                 List.append([L2[j],R2[j],'nan',cutre[j],'nan',time_re[j],'C'])  
               
  
        return(List,len(List))
    
    def getRelativeSpeed(self,ecat):
        Vx=ecat['veloX']
        Vy=ecat['veloY']
        Or=ecat['overRideFeed']
        
        EffSpeed=round(np.mean(np.sqrt(Vx**2+Vy**2)),3)           # pythagoras for Effective speed
        RelSpeed=round(np.mean(Or)/10,3)                          # relative speed
                         
        return(EffSpeed,RelSpeed)
        
        
    def getPredData(self,path_loc,path_recut):
        
        # read data
        
        ecat_re,PosXrecut,PosYrecut,cutre,time_re,para_re,paraConf,visionResult=self.read_H5(path_recut)
        ecat_loc,PosXloc,PosYloc,cutloc,timeloc,para,paraConf,visionResult=self.read_H5(path_loc)
        
        EffSpeed,RelSpeed=self.getRelativeSpeed(ecat_loc)
    
        # collective list
        List,Len=self.sync(PosXloc,PosYloc,PosXrecut,PosYrecut,cutloc,cutre,timeloc,time_re)
        finalList=pd.DataFrame(List,columns=['posX','posY','cutLoc','cutRe','timeLoc','timeRe','label'])
        return(finalList,Len,para,paraConf,visionResult,EffSpeed,RelSpeed)
    
    
    
    def getData(self,path_loc,path_recut):
        
        F_list,Len,para,paraConf,visionResult,EffSpeed,RelSpeed=self.getPredData(path_loc,path_recut)
        
        
        # chosse cut control and location coordinates for label A
        Acut=F_list[F_list['label']=='A']['cutLoc'].tolist()
        xA=F_list[F_list['label']=='A']['posX'].tolist()
        yA=F_list[F_list['label']=='A']['posY'].tolist()
        Atime=F_list[F_list['label']=='A']['timeLoc'].tolist()
        
        # chosse cut control and location coordinates for label B
       
        Bcut=F_list[F_list['label']=='B']['cutLoc'].tolist()       
        Bre=F_list[F_list['label']=='B']['cutRe'].tolist()
        xB=F_list[F_list['label']=='B']['posX'].tolist()
        yB=F_list[F_list['label']=='B']['posY'].tolist()
        Btime=F_list[F_list['label']=='B']['timeRe'].tolist()
        BtimeLoc=F_list[F_list['label']=='B']['timeLoc'].tolist()
        
    
        # chosse cut control and location coordinates for label C
       
        Cre=F_list[F_list['label']=='C']['cutRe'].tolist()
        xC=F_list[F_list['label']=='C']['posX'].tolist()
        yC=F_list[F_list['label']=='C']['posY'].tolist()
        Ctime=F_list[F_list['label']=='C']['timeRe'].tolist()
        
        # Merge
        Time=Btime+Ctime
        TimeLoc=Atime+BtimeLoc
        Re=Bre+Cre
        Loc=Acut+Bcut
        
        if len(yB)==0:
            print('No overlap')
            B=None
        else:
            B=1
            
        if len(yC)!=0:
            a=xC[0]
            b=yC[0]
        else:
            a=None
            b=None
        
        
        X_loc=xA+xB
        Y_loc=yA+yB
        
        X_re=xB+xC
        Y_re=yB+yC
           
        return(X_loc,Y_loc,Loc,X_re,Y_re,Re,a,b,B,Time,Btime,Bcut,Bre,Cre,para,paraConf,visionResult,TimeLoc,Ctime,EffSpeed,RelSpeed)
    

 



