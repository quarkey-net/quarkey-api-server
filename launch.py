# -*- coding: utf-8 -*-
# Author    : Esteban Ristich <esteban.ristich@protonmail.com>
# License   : MIT

import platform, os, logging, falcon, argparse
from database.database import PGDatabase
from routes.register import Register

from routes.login import Login
from routes.process_tag import ProcessTag
from routes.process_link_tag import ProcessLinkTag
from routes.process_tester_key import ProcessTesterKey
from routes.password_item import PasswordItem

# from routes.verify_account import VerifyAccount
from routes.middleware import AcceptJSONMiddleware, CORSMiddleware, DebugMiddleware

from utils.config import AppState
from utils.base import get_rsa_keypair

parser = argparse.ArgumentParser(prog="launch", usage='%(prog)s [options] path', description="configure api launching")
parser.add_argument('--pub', metavar="pub", type=str, help="Rsa public key file for account token genaration. The program try to get keypair from database if not specified")
parser.add_argument('--pri', metavar="pri", type=str, help="Rsa private key file for account token genaration. The program try to get keypair from database if not specified")
parser.add_argument('--api-port', metavar="api_port", type=int, help="Specify listen port api")
args = parser.parse_args()

print(f'[+] App PID : {AppState.PID}')
print(f'[+] App version : v{".".join(map(str, AppState.VERSION))}-{AppState.TAG}')
print(f'[+] App socket : {AppState.HOST}:{AppState.PORT}')

""" SETUP LOGGING """
if AppState.LOGGING_LEVEL is not None:
    try: 
        os.mkdir('logs')
    except FileExistsError: 
        pass
    logfile = f'process-{AppState.PID}.log'
    logging.basicConfig(filename=f'logs/{logfile}', filemode='w', level=AppState.LOGGING_LEVEL, format='%(name)s:%(levelname)s-%(asctime)s-%(message)s', datefmt="%d-%m-%Y %H:%M:%S")
""" END SETUP LOGGING """

db = PGDatabase()
AppState.Database.CONN = db.connect()

middlewares: list = []
if AppState.TAG in ['dev', 'test']:
    middlewares.append(CORSMiddleware())
    middlewares.append(DebugMiddleware())

middlewares.append(AcceptJSONMiddleware())
# middlewares.append(DatabaseConnectMiddleware()) 


if AppState.AccountToken.TYPE == 'RS256':
    keypair: list = get_rsa_keypair(token_type="account_authentication")
    AppState.AccountToken.PUBLIC = keypair[0]
    AppState.AccountToken.PRIVATE = keypair[1]

api = application = falcon.App(middleware=middlewares)

reg = Register()
log = Login()
pass_itm = PasswordItem()

""" ver_acc = VerifyAccount() """

API_PREFIX = f'/api/v{AppState.VERSION[0]}'

api.add_route(f'{API_PREFIX}/register', reg)

api.add_route(f'{API_PREFIX}/login', log)

api.add_route("{}/account/password_item".format(
    API_PREFIX
), pass_itm)
api.add_route(f'{API_PREFIX}/account/tester/key', ProcessTesterKey())
api.add_route(f'{API_PREFIX}/account/tag', ProcessTag())
api.add_route(f'{API_PREFIX}/account/link/tag', ProcessLinkTag())


"""
api.add_route("{}/user/{}/verify_account".format(
    API_PREFIX,
    "{uid:uuid}"
), ver_acc) 
"""


if platform.system() == "Linux":
    import bjoern
    bjoern.run(api, host=AppState.HOST, port=AppState.PORT, reuse_port=True)
else:
    # import uvicorn
    # uvicorn.run(api, host=AppState.HOST, port=AppState.PORT, log_level=AppState.LOGGING_LEVEL)
    import waitress
    waitress.serve(api, host=AppState.HOST, port=AppState.PORT)
