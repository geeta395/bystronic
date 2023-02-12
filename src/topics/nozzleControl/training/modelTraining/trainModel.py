# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 14:37:18 2022

@author: chggo
"""

from sklearn.model_selection import train_test_split
import os
from keras.utils.vis_utils import plot_model
from os.path import exists 
from tensorflow.keras.optimizers import RMSprop,SGD,Adam
from keras.callbacks import ModelCheckpoint,LearningRateScheduler,EarlyStopping
import pandas as pd
import df2img
import matplotlib.pyplot as plt
import numpy as np
from keras import backend as K
import math


class Training():
    def __init__(self,X,Y,result_path,model,checkpoint_path,epochs,batch_size,randomSeed):
        self.X=X
        self.Y=Y
        self.result_path=result_path
        self.checkpoint_path=checkpoint_path
        self.model=model
        self.epochs=epochs
        self.batch_size=batch_size
        self.randomSeed=randomSeed
        
    def plotHist(self,plOt,nam,history):
         e=len(history.history['rmse'])
         X=np.arange(0,e)
         
         if plOt=='acc':
             plt.plot(X,history.history['rmse'])
             plt.plot(history.history['rmse'])
             plt.title('Model RMSE')
             plt.ylabel('rmse')
         else:
             plt.plot(X,history.history['loss'])
             plt.plot(history.history['val_loss'])
             plt.title('Model Loss')
             plt.ylabel('Loss')
         
         plt.xlabel('epoch')
         plt.legend(['train', 'val'], loc='upper right')
         plt.savefig(os.path.join(self.result_path,nam))
         plt.show()
         plt.close()
         return
     
    def Table(self,dataF,name='performance.png'):
         
         fig = df2img.plot_dataframe(dataF,
                                     
         title=dict(
         font_color="black",
         font_family="Times New Roman",
         font_size=20,
         text="Results",),
         
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
         
         fig_size=(700,200),
         )
         
         
         df2img.save_dataframe(fig=fig, filename=os.path.join(self.result_path,name))
         return
     
        
    
    def scheduler(self,epoch, lr):
        if epoch < 100 :
            lr=lr 
        elif epoch > 99 and lr > 1e-5:
            lr=lr*0.1
        elif epoch > 99 and lr <= 1e-5:
            lr=lr
        return (lr) 

     

    def rmse(self,y_true, y_pred):
        R=K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))
        
        return R

    def coeff_determination(self,y_true, y_pred):
        SS_res =  K.sum(K.square( y_true-y_pred ))
        SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
        return ( 1 - SS_res/(SS_tot + K.epsilon()) )

    def Train(self,lr):
        
       
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(self.X,self.Y, test_size=0.1,random_state=self.randomSeed)  #42
        
        #Save Model structure
        pltSave=os.path.join(self.result_path,'modelAlt.png')
        plot_model(self.model,to_file=pltSave, show_shapes=True)
        self.model.summary()
        
        if exists(self.checkpoint_path):
            self.model.load_weights(self.checkpoint_path)
            
        # Optimize and Compile
     
        #opt = Adam(lr)
        opt = SGD(lr, decay=4e-5, momentum=0.9, nesterov=True)
        self.model.compile(optimizer=opt, loss="mse", metrics=[self.rmse,self.coeff_determination]) 
        
        # defining the model checkpointing and metric to monitor
        checkpoint = ModelCheckpoint(self.checkpoint_path, monitor='loss',save_weights_only=True,verbose=1, save_best_only=True, mode='min')
        es = EarlyStopping(monitor='loss', patience=50) 
        #lrScheduler= LearningRateScheduler(self.scheduler,verbose=0)
        callbacks_list = [checkpoint,es]  #rScheduler,
        
        # Train 
        train_history = self.model.fit(X_train,y_train,epochs=self.epochs,shuffle=True,batch_size=self.batch_size,validation_split=0.1,callbacks=callbacks_list)
        


        self.model.save(self.checkpoint_path)
    
        # Evaluate
        score = self.model.evaluate(X_test,y_test, verbose=2)
        y_hat = self.model.predict(X_test)
       
       
        
        # Plots
        
        self.plotHist('acc','rmsePlot.png',train_history)
        self.plotHist(None,'LossPlot.png',train_history)
        print('Result : ')
        print("Test loss:", score[0])
        print("Test rmse:", score[1])
        
        
        # Dataframe
        numVal=int(X_train.shape[0]*0.2)
        dataF=pd.DataFrame({'Test':[round(score[1],6),round(score[0],6),round(score[2],6),X_test.shape[0]],'Validation':[round(train_history.history['rmse'][-1],6),round(train_history.history['val_loss'][-1],6),round(train_history.history['val_coeff_determination'][-1],6),numVal],
                            'Train':[round(train_history.history['rmse'][-1],6),round(train_history.history['loss'][-1],6),round(train_history.history['coeff_determination'][-1],6),(X_train.shape[0]-numVal)]},index=['RMSE','Loss','coeff_determination','Total Images'])
        self.Table(dataF)
        
        return(y_hat,y_test,X_test)
        