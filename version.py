#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versioning Classes
"""

import os
import subprocess
from datetime import datetime, timedelta
import argparse
import yaml

import sys

class VersionYAML:
    def __init__(self, *paths):
        self.versions = {k:GitVersion(k) for k in paths}
    
    def _get_list(self):
        version_dict = {k:v._get_dict() for k,v in self.versions.items()}
        return version_dict

    def save_as_yaml(self, path):
        dict_list = self._get_list()
        with open(path, 'w') as yaml_file:
            yaml.dump(dict_list, yaml_file, default_flow_style=False) 


class GitVersion:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Der angegebene Pfad '{path}' existiert nicht.")
        
        self.path = path
        self.change_date = None
        self.commit_hash = None
        self.change_count = 0
        
        self.checkpoints =  {
                            'major' : 0,
                            'minor' : 0,
                            'last_minor_commit' : '111d7e844285cb040cd84ddf6f3fd428f4cb672f',
                            }
        
        self._get_last_change_date()
        self._get_change_count()
        
    def _get_dict(self):
        return {
                'hash' : self.commit_hash,
                'date': self.change_date.isoformat(),
                'count' : self.change_count,
                'version' : self.version(),
                'semantic' : self._get_semantic_version(),
                }
        
    def _get_semantic_version(self):
        return f'{self.checkpoints.get("major")}.{self.checkpoints.get("minor")}.{self.count_commits_since_last_minor()}'

    def count_commits_since_last_minor(self):
        if 'minor' in self.checkpoints:
            minor_commit_hash = self.checkpoints['last_minor_commit']
            
            result = subprocess.run(['git', 'rev-list', '--count', f'{minor_commit_hash}..HEAD', '--', self._get_git_root()], stdout=subprocess.PIPE)
            commit_count_since_minor = int(result.stdout.decode('utf-8').strip())
            
            return commit_count_since_minor
        else:
            return 0

    def _get_last_change_date(self):
        result = subprocess.run(['git', 'log', '-1', '--format=%cd %H', '--date=iso', '--' ,self.path], stdout=subprocess.PIPE)
        last_change_info = result.stdout.decode('utf-8').strip().split()
        last_change_date_str = " ".join(last_change_info[:-1])
        self.commit_hash = last_change_info[-1]
        self.change_date = datetime.strptime(last_change_date_str, "%Y-%m-%d %H:%M:%S %z")

    def _get_change_count(self):
        from_time = self.change_date.strftime('%Y-%m-%d')
        to_time = (self.change_date + timedelta(days=1)).strftime('%Y-%m-%d')
        result = subprocess.run(['git', 'log', f'--since="{from_time} 00:00:00"', f'--until="{to_time} 00:00:00"', '--format=%cd', '--', self.path], stdout=subprocess.PIPE)
        changes_today = result.stdout.decode('utf-8').strip().split('\n')
        self.change_count = len(changes_today)

    def _get_git_root(self):
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE)
        git_root = result.stdout.decode('utf-8').strip()
        return os.path.abspath(git_root)
    
    def version(self):
        return f'{self.change_date.strftime("%Y-%m-%d")}v{int(self.change_count)}'
    
    def get_change_date(self):
        return f'{self.change_date.strftime("%d.%m.%Y")}'

    def _print(self):
        return self.version()
    
    def __str__(self):
        return self._print()

    def __repr__(self):
        return self._print()

def main():
    parser = argparse.ArgumentParser(description='Get Git version information for a given path')
    parser.add_argument('path', help='Path to the directory to get Git version information for')

    args = parser.parse_args()
    
    version_info = GitVersion(args.path)
    print(version_info.version())

if __name__ == "__main__":
    pass
    self = GitVersion('./redirectmanager')
    # main()