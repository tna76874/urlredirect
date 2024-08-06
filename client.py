#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
client
"""
import requests
import pandas as pd
import os

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
            
    def update_from_file(self, file_path):
        csv = SheetParser(file_path)
        if not isinstance(csv.redirect,type(None)):
            for index, row in csv.redirect.iterrows():
                self.add_redirect(**row)
        if not isinstance(csv.alias,type(None)):
            for index, row in csv.alias.iterrows():
                self.add_alias(**row)

    def add_redirect(self, **kwargs):
        url = f"{self.host}/api/add_redirect"
        headers = {'Authorization': self.key}
        payload = {
            'redirect': kwargs.get('redirect'),
            'key': kwargs.get('key'),
        }
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            return {'message': 'Failed to add redirect', 'error': response.json()}

    def add_alias(self, **kwargs):
        url = f"{self.host}/api/add_alias"
        headers = {'Authorization': auth_key}
        payload = {
            'alias': kwargs.get('alias'),
            'key': kwargs.get('key'),
        }
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            return {'message': 'Failed to add alias', 'error': response.json()}
        
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