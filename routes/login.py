import falcon, datetime
from database.models import Accounts
from utils.base import api_message, api_validate_form
from utils.security.auth import AccountAuthToken, UserPasswordHasher
from utils.config import AppState

class Login(object):

    def __init__(self):
        """
        self.username_regex     = "^(?=[a-zA-Z0-9._]{4,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"
        self.password_regex     = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"
        """
        self.token_controller = AccountAuthToken('', '')
        self.password_hasher    = UserPasswordHasher()
        self.get_form          = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "uid"       : {"type": "string", "pattern": "^(?=[a-zA-Z0-9._]{4,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"},
                "password"  : {"type": "string", "pattern": "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"}
            },
            "required": ["uid", "password"]
        }

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_400

        if api_validate_form(req.media, self.get_form):
            try:
                q1 = Accounts.select(
                    Accounts.uid,
                    Accounts.firstname,
                    Accounts.lastname,
                    Accounts.password,
                    # peewee.fn.CONCAT(Accounts.firstname, ' ', Accounts.lastname).alias('fullname'),
                    Accounts.role,
                    Accounts.premium_expiration
                ).where((Accounts.is_banned == False) & (Accounts.is_verified == True) & (Accounts.uid == req.media['uid'])).limit(1).dicts()
            except Exception as e:
                api_message('w', f'Failed to request database to login account : {e}')
                resp.status = falcon.HTTP_500
                return

            if not q1:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'username or password not found'}
                return

            roles: list = q1[0]['role'].split(':')
            fullname: str = "{0} {1}".format(q1[0]['firstname'], q1[0]['lastname'])


            if self.password_hasher.verify_password(q1[0]['password'], req.media['password']):
                if q1[0]['premium_expiration'] > datetime.datetime.utcnow():
                    roles.append('premium')

                api_message('d', f'pub type {type(AppState.AccountToken.PUBLIC)}')
                token = self.token_controller.create(
                    duration=3000,
                    uid=q1[0]['uid'],
                    roles=roles,
                    fullname=fullname
                )
                api_message('i', "success login (uid={0} fullname={1})".format("'"+q1[0]['uid']+"'", "'"+fullname+"'"))
                resp.status = falcon.HTTP_OK
                resp.media  = {'title': 'OK', 'description': 'success to login', 'content': {'token': token}}
                return
            else:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'username or password not found'}
                return