#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
version-cli
"""
from version import *


def main():
    parser = argparse.ArgumentParser(description='Get Git version information for given paths')
    parser.add_argument('paths', nargs='+', help='List of paths to directories to get Git version information for')
    parser.add_argument('--yml', default='versions.yml', help='Filename for the exported YAML (default: versions.yml)')

    args = parser.parse_args()
    
    version_info = VersionYAML(*args.paths)
    version_info.save_as_yaml(args.yml)

if __name__ == "__main__":
    main()

