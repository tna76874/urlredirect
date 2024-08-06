#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
helper
"""
import yaml

class ConfigLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = self.load_config()

    def load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei."""
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file)
    
    def get_keys(self):
        api_keys = self.config.get('api_keys', [])
        return {entry['name']: entry['key'] for entry in api_keys}
    
    def get_landingpage(self):
        return self.config.get('landing_page', None)