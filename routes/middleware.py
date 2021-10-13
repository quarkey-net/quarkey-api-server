# -*- coding: utf-8 -*-
from database.database import PGDatabase
from utils.config import AppState
from utils.security.auth import AccountAuthToken
import falcon
from utils.base import api_message
# from database.database import db

class DebugMiddleware(object):

    def process_request(self, req, resp):
        # api_message('d', f'[MIDDLEWARE][{req.path}] <= {req.media}')
        pass

    def process_response(self, req, resp, resource, req_succeeded):
        # api_message('d', f'[MIDDLEWARE][{req.path}] => {resp.media}')
        pass


class AcceptJSONMiddleware(object):

    def process_request(self, req, resp):

        if req.content_type is None or req.content_type == falcon.MEDIA_URLENCODED and req.method == "GET":
            pass
        elif not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.')
        elif req.content_type is None:
            raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.')
        else:
            raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.')
        """
        if req.content_type == falcon.MEDIA_URLENCODED and req.method == 'GET':
            pass
        elif req.content_type == None or falcon.MEDIA_JSON not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType('This API only supports requests encoded as JSON.')
        """
            

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Accept', falcon.MEDIA_JSON)
        resp.set_header('X-Api-Version', ".".join(map(str, AppState.VERSION)))

class CORSMiddleware(object):
    
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 3600)  # 20 days
        #api_message('WARNING', f'{req.headers}')
        if req.method == 'OPTIONS':
            raise falcon.HTTPStatus(falcon.HTTP_200, body='\n')
"""
    def process_response(self, req, resp, resource, req_succeeded):
        api_message('WARNING', f'{resp.headers}')
"""


class DatabaseConnectMiddleware():
    
    def process_resource(self, req, resp, resource, params):
        if resource is not None:
            AppState.Database.CONN.close()
            AppState.Database.CONN = PGDatabase().connect()

    def process_response(self, req, resp, resource, req_succeeded):
        if AppState.Database.CONN:
            AppState.Database.CONN.close()


class AuthorizeResource:
    def __init__(self, roles: list):
        self._token_controller  = AccountAuthToken('', '')
        self._roles             = roles

    def __call__(self, req, resp, resource, params):
        api_message("d", f'[HOOK] resource : {req.path}, require roles : {self._roles}')
        token = req.get_header('Authorization')
        if token is None:
            raise falcon.HTTPUnauthorized(title="UNAUTHORIZED", description="this resource require account token")
        payload = self._token_controller.decode(token)
        roles = payload['roles']
        for x in self._roles:
            if x not in roles:
                raise falcon.HTTPUnauthorized(title="UNAUTHORIZED", description="you don't have roles to access to this resource")