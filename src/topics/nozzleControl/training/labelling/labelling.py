

import pandas as pd
import json
import os
import cv2
import matplotlib.pyplot as plt
from topics.nozzleControl.training.labelling.FindCircle import findCircle



data_path=r'C:\Users\chggo\REG_analysis\data\nozzle_MP2'
result_path=r'C:\Users\chggo\REG_analysis\data'
json_path=r'C:\Users\chggo\REG_analysis\data\labelStudio_MC7_MP2.json'



class Labelling():
    def __init__(self,data_path,result_path,json_path,w,h,name):
        self.data_path=data_path
        self.result_path=result_path
        self.json_path=json_path
        self.w=w
        self.h=h
        self.name=name
     
        
    
    def getLabelsFromJson(self):
        f=open(self.json_path)
        data=json.load(f)
        
        Img=[]
        keyPt=[]
        quality=[]
        for i in range(len(data)):
           Kp=[]
           Img.append(data[i]['data']['img'])
           result=data[i]['annotations'][0]['result']
           if len(result) !=0:
               Kp.append(data[i]['annotations'][0]['result'][0]['value'])
               Kp.append(data[i]['annotations'][0]['result'][1]['value'])
               Kp.append(data[i]['annotations'][0]['result'][2]['value'])
               keyPt.append(Kp)
               quality.append('Good')
           else:
               keyPt.append(None)
               quality.append('Bad')
        df=pd.DataFrame({'img':Img,'kp-1':keyPt,'quality':quality})
        return(df)

    def split(self,p):
       P=p.split(',')
       return(P[0])
   
    def getCoordinates(self):
        data=self.getLabelsFromJson()
        ImgPath=data['img']
        coordinates=data['kp-1']
        quality=data['quality']
        coor=[]
        Img=[]
        BadImg=[]
        for i in range(len(coordinates)):  
            C=coordinates[i]
            I=(ImgPath[i].split('-'))[-1]
            if quality[i]=='Good':
                coor.append({'x1':C[0]['x'],'y1':C[0]['y'],'x2':C[1]['x'],'y2':C[1]['y'],'x3':C[2]['x'],'y3':C[2]['y']})
                Img.append(os.path.join(self.data_path,I))
            else:
                BadImg.append({'img':os.path.join(self.data_path,I),'quality':'Bad'})
                
        df1=pd.DataFrame(BadImg)
        df1.to_excel(os.path.join(self.data_path,'BadImges.xlsx')) 
        return(coor,Img)
    
    
    def getCircle(self):
        Circle=[]
        Points=[]
        coor,Img=self.getCoordinates()
        if len(coor) !=0:
            for i in range(len(coor)):
                
                circle,point=findCircle(coor[i],self.w,self.h)
                circle['img']=Img[i]
                Circle.append(circle)
                Points.append(point)
            
        return(Circle,Points)
    
   
    def drawCircle(self,points=True):
       
        try: 
            path=os.path.join(self.result_path,'LabelValidation')
            os.mkdir(path) 
        except OSError as error: 
            print(error)  
            
        Circle,Points=self.getCircle()
        if len(Circle) !=0:
            for j in range(len(Circle)):
                r1=Circle[j]['r']
                x1=Circle[j]['x']
                y1=Circle[j]['y']
                fn=Circle[j]['img']
                img=cv2.imread(fn,cv2.IMREAD_ANYCOLOR)
                if r1 != 'None':
                    img=cv2.circle(img,(int(x1),int(y1)),int(r1),(0,0,255),2)
                    img=cv2.circle(img,(int(Points[j]['x1']),int(Points[j]['y1'])),4,(0,0,0),3)
                    img=cv2.circle(img,(int(Points[j]['x2']),int(Points[j]['y2'])),4,(0,0,0),3)
                    img=cv2.circle(img,(int(Points[j]['x3']),int(Points[j]['y3'])),4,(0,0,0),3)
                
                
                 
                filename=os.path.join(self.result_path,'LabelValidation','img_'+str(j)+'.png')
               
                cv2.imwrite(filename,img)
                df=pd.DataFrame(Circle)
                df.to_excel(os.path.join(self.data_path,self.name))
        return(Circle,Points,df)
    
    def changeAddress(self,Circle):
       # For deep monster we need absolute path
       for i in range(len(Circle)):
           s=Circle[i]['img']
           s1=(s[27:]).split('\\')
           s2=s1[1]+'/'+ s1[2]+'/'+ s1[3]
           Circle[i]['img']=s2
       df=pd.DataFrame(Circle)
       df.to_excel(os.path.join(self.data_path,self.name))            
       return

L=Labelling(data_path,result_path,json_path,720,540,'label_MP2.xlsx')
Circle,Points,df=L.drawCircle()
# If Deep Monster
L.changeAddress(Circle)

