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
from routes.tool import ProcessGenData
from routes.process_account_activation import ProcessAccountActivation
from routes.process_info import ProcessApiInfos

# from routes.verify_account import VerifyAccount
from routes.middleware import AcceptJSONMiddleware, CORSMiddleware, DebugMiddleware

from utils.config import AppState
from utils.base import get_rsa_keypair, smtp_connect

parser = argparse.ArgumentParser(prog="launch", usage='%(prog)s [options] path', description="configure api launching")
parser.add_argument('--pub', metavar="pub", type=str, help="Rsa public key file for account token genaration. The program try to get keypair from database if not specified")
parser.add_argument('--pri', metavar="pri", type=str, help="Rsa private key file for account token genaration. The program try to get keypair from database if not specified")
parser.add_argument('--api-port', metavar="api_port", type=int, help="Specify listen port api")
args = parser.parse_args()

print(f'[+] App PID : {AppState.PID}')
print(f'[+] App version : v{".".join(map(str, AppState.VERSION))}-{AppState.TAG}')
print(f'[+] App socket : {AppState.HOST}:{AppState.PORT}')

""" SETUP LOGGING """
if AppState.LOGGING_ENABLE:
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

# init smtp quarkey email connection
if not smtp_connect():
    exit(1)


if AppState.AccountToken.TYPE == 'RS256':
    account_keypair: list = get_rsa_keypair(token_type="account_controller")
    AppState.AccountToken.PUBLIC_KEY = account_keypair[0]
    AppState.AccountToken.PRIVATE_KEY = account_keypair[1]
    
    email_keypair: list = get_rsa_keypair(token_type="email_controller")
    AppState.Email.PUBLIC_KEY = email_keypair[0]
    AppState.Email.PRIVATE_KEY = email_keypair[1]


api = application = falcon.App(middleware=middlewares)

reg = Register()
log = Login()
pass_itm = PasswordItem()

""" ver_acc = VerifyAccount() """

api.add_route("/api/auth/register", reg)
api.add_route("/api/auth/login", log)
api.add_route("/api/activate/account", ProcessAccountActivation())
api.add_route("/api/account/item/password", pass_itm)
api.add_route("/api/account/tester/key", ProcessTesterKey())
api.add_route("/api/account/item/tag", ProcessTag())
api.add_route("/api/account/item/password/link/to/tag", ProcessLinkTag())
# private (only moderator && admin) and debug endpoint
api.add_route("/api/account/tool/gen/data", ProcessGenData())
api.add_route("/api/infos", ProcessApiInfos())

if platform.system() == "Linux":
    import bjoern
    bjoern.run(api, host=AppState.HOST, port=AppState.PORT, reuse_port=True)
else:
    # import uvicorn
    # uvicorn.run(api, host=AppState.HOST, port=AppState.PORT, log_level=AppState.LOGGING_LEVEL)
    import waitress
    waitress.serve(api, host=AppState.HOST, port=AppState.PORT)
