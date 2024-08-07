#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
client
"""
import requests
import pandas as pd
import os
import sys
from packaging.version import Version
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import redirectmanager

class RequestHandler:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.key = kwargs.get('key')
        self.headers = {'Authorization': self.key}

    def post(self, endpoint, payload):
        url = f"{self.host}{endpoint}"
        response = requests.post(url, json=payload, headers=self.headers)
        return self._handle_response(response)

    def get(self, endpoint):
        url = f"{self.host}{endpoint}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def delete(self, endpoint):
        url = f"{self.host}{endpoint}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

    def _handle_response(self, response):
        if response.status_code in [200, 201]:
            return {'status': True, 'response': response.json()}
        else:
            return {'status': False, 'response': response.json()}

class SheetParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.redirect = None
        self.alias = None
        self.load_data()

    def load_data(self):
        # Überprüfen der Dateiendung
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension == '.csv':
            # CSV-Datei laden
            self.redirect = pd.read_csv(self.file_path)
        elif file_extension == '.xlsx':
            # Excel-Datei laden und überprüfen, ob die benötigten Sheets existieren
            xls = pd.ExcelFile(self.file_path)
            if 'redirect' in xls.sheet_names:
                self.redirect = pd.read_excel(xls, sheet_name='redirect')
            if 'alias' in xls.sheet_names:
                self.alias = pd.read_excel(xls, sheet_name='alias')
        else:
            raise ValueError("Unsupported file type. Please provide a .csv or .xlsx file.")
        
class RedirectManager:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.key = kwargs.get('key')
        if self.host is None:
            raise ValueError("Host must be provided.")
        if self.key is None:
            raise ValueError("Key must be provided.")
            
        self.request_handler = RequestHandler(host = self.host, key = self.key)
        
        self._check_if_client_fit_server()
        
    def _get_client_version(self):
        try:
            return redirectmanager.__version__
        except:
            return None
        
    def _check_if_client_fit_server(self):
        client_version = self._get_client_version()
        if client_version==None:
            return
        server_version = self._get_server_version()
        if server_version==None:
            raise ValueError("Server not reachable")      
        
        client_version = Version(client_version)
        server_version = server_version
        
        passed = client_version==server_version
        if passed==False:
            raise ValueError(f'Server {server_version.base_version} and client {client_version.base_version} not fitting')
        
    
    def _get_server_version(self):       
        response = self.request_handler.get("/api/versions")
        if response.get('status')==True:
            return response.get('response', {}).get('client', {}).get('semantic')
        return None
            
    def add_redirect(self, **kwargs):
        payload = {
            'redirect': kwargs.get('redirect'),
            'key': kwargs.get('key'),
        }
        return self.request_handler.post("/api/add_redirect", payload)

    def get_all_redirects(self):
        response = self.request_handler.get("/api/get_all_redirects")
        if response.get('status')==True:
            return pd.DataFrame(response.get('response', {}).get('redirects', {}))
        return None

    def delete_all_redirects(self):
        return self.request_handler.delete("/api/delete_all_redirects")

    def add_alias(self, **kwargs):
        payload = {
            'alias': kwargs.get('alias'),
            'key': kwargs.get('key'),
        }
        return self.request_handler.post("/api/add_alias", payload)

    def update_from_file(self, file_path):
        csv = SheetParser(file_path)
        if not isinstance(csv.redirect,type(None)):
            for index, row in csv.redirect.iterrows():
                self.add_redirect(**row)
        if not isinstance(csv.alias,type(None)):
            for index, row in csv.alias.iterrows():
                self.add_alias(**row)
        
if __name__ == "__main__":
    host = "http://localhost:5000"
    auth_key = "test"

    self = RedirectManager(host=host, key=auth_key)

    # # Redirect hinzufügen
    # redirect_response = self.add_redirect(redirect="http://google.com", key='blabla')
    # print(redirect_response)

    # # Alias hinzufügen
    # alias_response = self.add_alias(alias="alias123", key='blabla')
    # print(alias_response)