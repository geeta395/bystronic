# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 11:28:53 2022

@author: chggo
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.layers.convolutional import Conv2D,Conv1D
from keras.layers.convolutional import MaxPooling2D,MaxPooling1D
from keras.layers import Activation,Dense,Flatten,BatchNormalization,Dropout

# Mixed Input Keras Model
class Model():
    def __init__(self,C_inShape,B_inShape,P_inShape):
        self.C_inShape=C_inShape
        self.B_inShape=B_inShape
        self.P_inShape=P_inShape
        
        
    def mixedKeras(self):
        
        # define three sets of inputs (input nodes)
        inputA = keras.Input(shape=(self.C_inShape[0],self.C_inShape[1],))
        inputB = keras.Input(shape=(self.B_inShape[0],self.B_inShape[1],))
        inputC = keras.Input(shape=(self.P_inShape[0],self.P_inShape[1],)) 
    
        # the first branch operates on the first input
        x = Dense(64)(inputA)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Dropout(0.3)(x)
        x = Dense(32)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Dropout(0.3)(x)
        x = Dense(2)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = keras.Model(inputs=inputA, outputs=x,name='model_Cdata')
        
    
        # the second branch opreates on the second input
        y = Dense(64)(inputB)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = Dropout(0.3)(y)
        y = Dense(32)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = Dropout(0.3)(y)
        y = Dense(2)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = Flatten()(y)
        y = keras.Model(inputs=inputB, outputs=y,name='model_Bdata')
        
    
        # the third branch opreates on the third input
        
        z = Dense(64)(inputC)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Dropout(0.3)(z)
        z = Dense(32)(z)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Dropout(0.3)(z)
        z = Dense(2)(z)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Flatten()(z)
        
        z = keras.Model(inputs=inputC, outputs=z,name='model_Para')
    
        # combine the output of all the branches
        combined = layers.concatenate([x.output, y.output, z.output])
        
       
        # combined outputs
        w = Dense(2)(combined)
        w = BatchNormalization()(w)
        w = Activation('relu')(w)
        w = Dense(1)(w)
        w = Activation('sigmoid')(w)  
        
        # single output
        model = keras.Model(inputs=[x.input, y.input, z.input], outputs=w)
        return(model)
    
    def mixedCon(self):
        
        # define three sets of inputs (input nodes)
        inputA = keras.Input(shape=(self.C_inShape[0],self.C_inShape[1]))
        inputB = keras.Input(shape=(self.B_inShape[0],self.B_inShape[1]))
        inputC = keras.Input(shape=(self.P_inShape[0],self.P_inShape[1])) 
    
        # the first branch operates on the first input
        x = Conv1D(filters=64, kernel_size=2)(inputA)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.3)(x)
        x = Conv1D(filters=32, kernel_size=2)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.3)(x)
        x = Flatten()(x)
        x = Dense(2)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = keras.Model(inputs=inputA, outputs=x,name='model_Cdata')
        
    
        # the second branch opreates on the second input
        y = Conv1D(filters=64, kernel_size=2)(inputB)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = MaxPooling1D(pool_size=2)(y)
        y = Dropout(0.3)(y)
        y = Conv1D(filters=32, kernel_size=2)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = MaxPooling1D(pool_size=2)(y)
        y = Flatten()(y)
        y = Dense(2)(y)
        y = BatchNormalization()(y)
        y = Activation('relu')(y)
        y = keras.Model(inputs=inputB, outputs=y,name='model_Bdata')
        
    
        # the third branch opreates on the third input
        z = Dense(64)(inputC)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Dropout(0.3)(z)
        z = Dense(32)(z)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Dropout(0.3)(z)
        z = Dense(2)(z)
        z = BatchNormalization()(z)
        z = Activation('relu')(z)
        z = Flatten()(z)
        z = keras.Model(inputs=inputC, outputs=z,name='model_Para')
    
        # combine the output of all the branches
        combined = layers.concatenate([x.output, y.output, z.output])
        
       
        # combined outputs
        w = Dense(2)(combined)
        w = BatchNormalization()(w)
        w = Activation('relu')(w)
        w = Dense(1)(w)
        w = Activation('sigmoid')(w)
       
        
        # single output
        model = keras.Model(inputs=[x.input, y.input, z.input], outputs=w)
        return(model)
    
   