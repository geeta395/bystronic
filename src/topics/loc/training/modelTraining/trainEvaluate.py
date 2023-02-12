# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 12:12:31 2022

@author: chggo
"""

import os
from tensorflow.keras.optimizers import Adam,SGD,RMSprop
import numpy as np
from keras.utils.vis_utils import plot_model
import matplotlib.pyplot as plt
import df2img
from keras.callbacks import ModelCheckpoint,EarlyStopping,CSVLogger
import pandas as pd



class Train():
    def __init__(self,path,checkpoint_path,result_path,loadWeight):
        self.path=path
        self.checkpoint_path=checkpoint_path
        self.loadWeight=loadWeight
        self.result_path=result_path
        
    def trainModel(self,model,trainX=None,trainY=None,testX=None,testY=None,imageNam=None,val=None,epochs=None,batch_size=None):
        
        #model.summary()
        pltSave=os.path.join(self.checkpoint_path,imageNam)
        plot_model(model,to_file=pltSave, show_shapes=True)
        
        # loading the best model
        if self.loadWeight==True:
            model.load_weights(self.checkpoint_path)
            
        # Train and evaluate
        
        model.compile(
                        loss='binary_crossentropy',
                        optimizer=RMSprop(),           
                        metrics=["accuracy"],
                    )
        
        
        # defining the model checkpointing and metric to monitor
        checkpoint = ModelCheckpoint(self.checkpoint_path, monitor='accuracy',save_weights_only=True,verbose=1, save_best_only=True, mode='max')
        #es = EarlyStopping(monitor='accuracy', patience=20)  # early stopping for overfitting
        
       
        #csv_logger = CSVLogger(os.path.join(self.path,'training.log'))
        callbacks_list = [checkpoint] #,csv_logger
        history=model.fit(trainX,trainY,validation_split=val,epochs=epochs,batch_size=batch_size,shuffle=True,callbacks=callbacks_list)
        score = model.evaluate(testX,testY, verbose=2)
       
        model.load_weights(self.checkpoint_path)

        model.save(self.checkpoint_path + '/tmp',model.name)
        
        # Plot results
        self.plotHist('acc','Accuracy.png',history,epochs)
        self.plotHist(None,'Loss.png',history,epochs)
        
        # Results
        print('____________________________________________________________')
        print('____________________________________________________________')
        
        
        print('Result : ')
        print("Test loss:", score[0])
        print("Test accuracy:", score[1])
        
                
        # Dataframe
        trainX1=trainX[1].shape[0]
        numVal=int(trainX1*val)
        tLen=testX[1].shape[0]
        # save results
        dataF=pd.DataFrame({'Test':[round(score[1],6),round(score[0],6),tLen],'Validation':[round(history.history['val_accuracy'][-1],6),round(history.history['val_loss'][-1],6),numVal],
                             'Train':[round(history.history['accuracy'][-1],6),round(history.history['loss'][-1],6),(trainX1-numVal)]},index=['Accuracy','Loss','Total Images'])
        self.Table(dataF,name='AccTable.png')
        return
        
        
        
    def plotHist(self,plOt=None,nam=None,history=None,epochs=None):
        totalEpochs=len(history.history['accuracy'])
        X=np.arange(0,totalEpochs)
        if plOt=='acc':
            plt.plot(X,history.history['accuracy'])
            plt.plot(history.history['val_accuracy'])
            plt.title('Model Accuracy')
            plt.ylabel('Accuracy')
        else:
            plt.plot(X,history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.title('Model Loss')
            plt.ylabel('Loss')
        
        plt.xlabel('epoch')
        plt.legend(['train', 'val'], loc='upper right')
        plt.savefig(os.path.join(self.result_path,nam))
        plt.show()
        return
    
    def Table(self,dataF,name=None):
        
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
    
        