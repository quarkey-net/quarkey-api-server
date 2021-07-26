import falcon, datetime
from utils.security.auth import UserPasswordHasher, gen_account_keypair
from utils.config import AppState
from utils.base import api_validate_form, api_message

from database.models import Accounts

class Register(object):

    def __init__(self):
        """
        self.username_regex     = "^(?=[a-zA-Z0-9._]{4,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"
        self.email_regex        = "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"
        self.password_regex     = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"
        """
        self.password_hasher    = UserPasswordHasher()
        self.post_form          = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "uid"       : {"type": "string", "pattern": "^(?=[a-zA-Z0-9._]{4,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"},
                "firstname" : {"type": "string"},
                "lastname"  : {"type": "string"},
                "email"     : {"type": "string", "format": "email"},
                "password"  : {"type": "string", "pattern": "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"}
            },
            "required": ["uid", "firstname", "lastname", "email", "password"]
        }


    def on_get(self, req, resp):
        pass

    def on_post(self, req, resp):
        resp.status         = falcon.HTTP_400

        if api_validate_form(req.media, self.post_form):
            try:
                q1 = Accounts.get_or_none((Accounts.uid == req.media["uid"]) | (Accounts.email == req.media["email"]))
            except Exception as e:
                api_message('w', f'Failed to request database : {e}')
                resp.status = falcon.HTTP_500
                return
            
            if q1 is None:
                keypair = gen_account_keypair()
                datenow = datetime.datetime.utcnow()
                try:
                    Accounts.create(
                        uid=req.media['uid'],
                        firstname=req.media['firstname'],
                        lastname=req.media['lastname'],
                        email=req.media['email'],
                        password=self.password_hasher.hash_password(req.media['password']),
                        public_key=keypair[0],
                        private_key=keypair[1],
                        role="standard",
                        premium_expiration=datenow,
                        updated_on=datenow,
                        created_on=datenow
                    )
                    api_message('d', "successfull register (user=\"{0}\", uid={1})".format(req.media['firstname'] + ' ' + req.media['lastname'], req.media['uid']))
                    resp.status = falcon.HTTP_201
                    resp.media = {'title': 'CREATED', 'description': 'accounts created successfull'}
                    return
                except Exception as e:
                    api_message('w', f'Failed to request database to create user : {e}')
                    resp.status = falcon.HTTP_500
                    return
            else:
                resp.status = falcon.HTTP_400
                resp.media = {'title': 'BAD_REQUEST', 'description': 'username or email already exist'}