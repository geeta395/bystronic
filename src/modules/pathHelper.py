import os
from sys import platform

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if platform == "linux" or platform == "linux2":
    platForm='linux'
    path_module = os.path.dirname(os.path.abspath(__file__))
    path_work = os.getcwd()
    path_log =  os.path.join(os.path.abspath(os.path.join(path_work, os.pardir)) , 'log')
    
elif platform == "win32":
    platForm='win32'
    from modules.filePath import file
    path_module = file
    #path_module = os.path.dirname(os.path.abspath(__file__))
    #path_work =  os.getcwd()
    path_work = "c:/temp/icpdataprocessor/data"
    createDir(path_work)
    path_log =  os.path.join(os.path.abspath(os.path.join(path_work,os.pardir)) , 'log')
    createDir(path_log)

path_srcRoot = os.path.abspath(os.path.join(path_module, os.pardir)) 
path_resources =  os.path.join(path_srcRoot, 'resources')


