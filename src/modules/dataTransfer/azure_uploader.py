# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 15:30:19 2022

@author: chggo
"""

import os
import requests
from urllib.parse import urlparse
from datetime import datetime





class AzureUploader():
    def __init__(self,sas_url):
        self.sas_url=sas_url
        
    def add_prefix(self,filename):
        # Adding timestamp to file name
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        return f"{ts}_{filename}"


    def put_blob(self,storage_url,container_name, blob_name,qry_string,filePath):
        
        file_name_only = os.path.basename(filePath) #self.
        
        
        try:
            file_ext = '.' + file_name_only.split('.')[1]
        except IndexError:
            file_ext = None
        
        with open(filePath , 'rb') as fh:
            response = requests.put(storage_url+container_name + '/' + blob_name+'?'+qry_string,
                                    data=fh,
                                    headers={
                                                'content-type': 'application/zip',
                                                'x-ms-blob-type': 'BlockBlob'
                                            },
                                    params={'file': filePath}
                                    )
            
        return response.status_code
    
        
        
    def upload_using_sas1(self, fileName, binaryData):
       # mimetypes.suffix_map['.zip']
        # https://stackoverflow.com/questions/54556859/upload-binary-file-using-python-requests
        pass
        
    def upload_using_sas(self, filePath):
        
        
        """
        Upload File using Azure SAS url.
        This function uploads file to Azure blob container
        :param sas_url:  Azure sas url with write access on a blob storage
        :param file_name_full_path:  File name with fill path
        :return:  HTTP response status of file upload
        """
        o = urlparse(self.sas_url)
        # Remove first / from path
        if o.path[0] == '/':
            blob_storage_path = o.path[1:]
        else:
            blob_storage_path = o.path
        storage_account = o.scheme + "://" + o.netloc + "/"
        file_name_only = os.path.basename(filePath)
        # make unique file names by adding time stamp
        file_name_only = self.add_prefix(file_name_only)
        
        response_status = self.put_blob(storage_account,blob_storage_path,file_name_only,o.query,filePath)
        return response_status,file_name_only

