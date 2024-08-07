#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
helper
"""
import yaml
import os

class ConfigLoader:
    def __init__(self, config_file_path, versions='versions.yml'):
        self.file_path = config_file_path
        self.versions_file_path = versions

        self.config = self.load_config()
        self.versions = self.load_versions()

    def load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei."""
        try:
            with open(self.file_path, 'r') as file:
                return yaml.safe_load(file)
        except:
            return {}

    def load_versions(self):
        """Lädt die Versionen aus der versions.yml-Datei, falls sie existiert."""
        if os.path.exists(self.versions_file_path):
            try:
                with open(self.versions_file_path, 'r') as file:
                    return yaml.safe_load(file) or {}
            except Exception as e:
                print(f"Fehler beim Laden der Versionen: {e}")
                return {}
        else:
            return {}
    
    def get_keys(self):
        api_keys = self.config.get('api_keys', [])
        return {entry['name']: entry['key'] for entry in api_keys}
    
    def get_landingpage(self):
        return self.config.get('landing_page', None)

    def get_matomo(self):
        return self.config.get('matomo', {})

    def _get_client_version(self):
        """Holt die Version für den Eintrag './redirectmanager' aus self.versions."""
        return self.versions.get('./redirectmanager', {})