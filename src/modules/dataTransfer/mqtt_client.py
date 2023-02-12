# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 09:41:38 2022

@author: chggo
"""


import paho.mqtt.client as mqtt
import warnings
warnings.filterwarnings("ignore")




class MqttClient():
    def __init__(self,worker,logger,clientName, username="manager", password="byadmin", brokerUrl="localhost", port = 1883,charts=False):
        self.clientName = clientName
        self.username = username
        self.password = password
        self.worker=worker
        self.brokerUrl=brokerUrl
        self.port=port
        self.logger=logger
        self.charts=charts  # parameter to check if charts should be displayed
    
        
        
    def connect(self):
        global client
        client = mqtt.Client(self.clientName)
        client.username_pw_set(username=self.username, password=self.password)
        client.on_connect=self.on_connect
        client.connect(self.brokerUrl,self.port) 
        client.loop_start()
        client.on_subscribe = self.on_subscribe
        client.on_message = self.on_message
        
        
        
    def disconnect(self):
        
        client.loop_stop()
        
    def isConnected(self):
        return client.isConnected()
    
    def subscribe(self, topic):
        self.logger.info('subscribed to the topic {} '.format(topic))
        client.subscribe(topic)
        #client.loop_forever()


    def on_subscribe(self,client,userdata,mid,granted_qos):
        #self.logger.info('subscribed')
        pass
    
    def on_connect(self,client, userdata, flags, rc):
        global connected
        #self.logger.info("Connected with result code "+str(rc))
        connected=1
    
    
    def on_message(self,client, userdata, message):
    
        self.logger.info('topic : {}, qos : {}, retain flag : {}'.format(message.topic,message.qos,message.retain))
      
           
        if message.topic.startswith('icp/'):
            oMsg = {}
            oMsg["payload"] = message.payload
            oMsg["topic"] =message.topic
            try:
                self.worker.doWork(oMsg,self.charts)
            except Exception as e:
                self.logger.exception('doWork failed')
        else: 
            self.logger.info('Not the right topic')
            
        return
 


