# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 13:08:43 2022

@author: chggo
"""


from tensorflow import keras
from tensorflow.keras import layers,regularizers


class ModelImg():
    def __init__(self):
        pass
       
    def imgReg(self,x):
       
       initializer = keras.initializers.HeNormal()  # Xavier intialization
       
       
       x = layers.Conv2D(64, 3, padding="same",activation='relu',kernel_initializer=initializer)(x)  
       x = layers.Conv2D(64, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(64, 3, activation='relu', padding="same")(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       x = layers.Conv2D(128, 3, activation='relu',padding="same")(x)  
       x = layers.Conv2D(128, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(128, 3, activation='relu', padding="same")(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       x = layers.Conv2D(256, 3, activation='relu',padding="same")(x)
       x = layers.Conv2D(256, 3, activation='relu',padding="same")(x)
       x = layers.Conv2D(256, 3, activation='relu', padding="same")(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       x = layers.Conv2D(512, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(512, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(512, 3, activation='relu', padding="same")(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       
       # = layers.Conv2D(1024, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(1024, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(64, 3, activation='relu', padding="same")(x)
       x = layers.Conv2D(16, 3, activation='relu', padding="same")(x)
       
       # Dense Block
       x=layers.Flatten()(x)
       x = layers.Dropout(0.2)(x)
       x=layers.Dense(512,activation='relu', kernel_regularizer=regularizers.L2(.01))(x)
       x = layers.Dropout(0.1)(x)
       x=layers.Dense(256,activation='relu', kernel_regularizer=regularizers.L2(.01))(x)
      # x = layers.Dropout(0.2)(x)
       x=layers.Dense(16, activation='relu',kernel_regularizer=regularizers.L2(.01))(x)
       output=layers.Dense(3,activation='linear')(x)    # Linear activation is Identity
       
       
       return output

   
    