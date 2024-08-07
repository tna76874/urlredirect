#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
url redirect
"""
from urldb import *
from helper import *
from flask import Flask, request, redirect, render_template_string, url_for
from flask_restful import Api, Resource, reqparse
from functools import wraps

app = Flask(__name__)
api = Api(app)

config = ConfigLoader('data/config.yml')
db = DatabaseManager(data='data/data.db')

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get('Authorization')
        valid_keys = config.get_keys()
        if auth_key not in valid_keys.values():
            return {'message': 'Unauthorized'}, 401

        return f(*args, **kwargs)
    return decorated

## ADDING REDIRECT
add_redirect_parser = reqparse.RequestParser()
add_redirect_parser.add_argument('key', type=str, help='Key for the redirect', required=True)
add_redirect_parser.add_argument('redirect', type=str, help='Redirect URL', required=True)
class AddRedirect(Resource):
    @require_auth
    def post(self):       
        args = add_redirect_parser.parse_args()
        data = {
                'key': args.get('key'),
                'redirect': args.get('redirect'),
                }

        try:
            db._ensure_redirect(**data)
            return {'message': 'Redirect added', **data}, 201
        except Exception as e:
            return {'message': 'Failed to add redirect', 'error': str(e)}, 500    
api.add_resource(AddRedirect, '/api/add_redirect')

## GETTING ALL REDIRECTS
class GetAllRedirects(Resource):
    def get(self):
        try:
            redirects = db._get_all_redirects()  # Ruft die Methode zum Abrufen aller Redirects auf
            return {'redirects': redirects}, 200
        except Exception as e:
            return {'message': 'Failed to retrieve redirects', 'error': str(e)}, 500

api.add_resource(GetAllRedirects, '/api/get_all_redirects')

## ADDING ALIAS
add_alias_parser = reqparse.RequestParser()
add_alias_parser.add_argument('alias', type=str, help='The alias key', required=True)
add_alias_parser.add_argument('key', type=str, help='the key to redirect to.', required=True)
class AddAlias(Resource):
    @require_auth
    def post(self):       
        args = add_alias_parser.parse_args()
        data = {
                'key': args.get('key'),
                'alias': args.get('alias'),
                }

        try:
            db._add_alias(**data)
            return {'message': 'Alias added', **data}, 201
        except Exception as e:
            return {'message': 'Failed to add alias', 'error': str(e)}, 500    
api.add_resource(AddAlias, '/api/add_alias')

## DELETING ALL REDIRECTS
class DeleteAllRedirects(Resource):
    @require_auth
    def delete(self):
        try:
            db._delete_all()  # Ruft die Methode zum Löschen aller Redirects auf
            return {'message': 'All redirects deleted successfully'}, 200
        except Exception as e:
            return {'message': 'Failed to delete all redirects', 'error': str(e)}, 500

api.add_resource(DeleteAllRedirects, '/api/delete_all_redirects')

## URL REDIRECT ENDPOINT
class Redirect(Resource):
    def get(self, key):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        allowed = db._allow_request(ip)
        if allowed==False:
            return {'message': 'Not allowed', 'error': 'too many requests'}, 500
        
        redirect_url = db._get_redirect(key)
        
        if redirect_url is not None:
            db._add_event(key=key, source=ip)
            return redirect(redirect_url, code=303)
        else:
            return redirect(url_for('index'), code=303)
api.add_resource(Redirect, '/<string:key>')

## HEALTHCHECK
class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy'}, 200
api.add_resource(HealthCheck, '/api/health')

## VERSIONS
class VersionCheck(Resource):
    def get(self):
        return {'client': config._get_client_version()}, 200
api.add_resource(VersionCheck, '/api/versions')


## LANDINGPAGE
@app.route('/')
def index():
    landing_page = config.get_landingpage()
    if landing_page is not None:
        return redirect(landing_page, code=303)
    else:
        return render_template_string('')
    
# ERROR HANDLING
@app.errorhandler(500)
def handle_server_error(error):
    return redirect(url_for('index'), code=303)

if __name__ == '__main__':
    app.run(debug=True)