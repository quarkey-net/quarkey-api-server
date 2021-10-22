from typing import Any, Literal
import falcon, datetime
from utils.base import api_message, api_validate_form
from utils.security.auth import AccountAuthToken, UserPasswordHasher
from utils.config import AppState

class Login(object):

    def __init__(self):
        self.token_controller = AccountAuthToken('', '')
        self.password_hasher    = UserPasswordHasher()
        self.get_form          = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                # "username"  : {"type": "string", "pattern": "^(?=[a-zA-Z0-9._]{3,24}$)(?!.*[_.]{2})[^_.].*[^_.]$"},
                "email"     : {"type": "string", "format": "email", "pattern": "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"},
                "password"  : {"type": "string", "pattern": "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"}
            },
            "required": ["email", "password"]
        }

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_400
        if api_validate_form(req.media, self.get_form):
            q1 = None
            email       = req.media.get("email", None)
            with AppState.Database.CONN.cursor() as cur:
                cur.execute("SELECT t2.id, t2.username, t2.password, t2.roles, t2.subscription_exp, t1.id AS tester_key, t2.activated_on, t2.is_banned FROM tester_keys AS t1 INNER JOIN accounts AS t2 ON t1.f_owner = t2.id WHERE t2.email = %s AND t1.type = %s AND t1.expiration_on > CURRENT_TIMESTAMP LIMIT 1",
                    (
                        email,
                        AppState.TAG
                    )
                )
                q1 = cur.fetchone()

            if q1 is None:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'Email or password not found'}
                return

            fullname: str   = q1[1]
            password: str   = q1[2]
            roles: list     = q1[3]
            subscription_exp = q1[4]
            tester_key: str      = q1[5]
            verification_date = q1[6]
            is_banned = q1[7]

            if is_banned:
                resp.status = falcon.HTTP_UNAUTHORIZED
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'Your account has been banned'}
                return

            if self.password_hasher.verify_password(password, req.media['password']):

                if verification_date is None or verification_date > datetime.datetime.utcnow():
                    resp.status = 350
                    resp.media  = {'title': 'BAD_REQUEST', 'description': 'Please verify your account'}
                    return

                if subscription_exp > datetime.datetime.utcnow():
                    roles.append('premium')

                api_message("w", f'fullname : {fullname}')
                token = self.token_controller.create(
                    duration=10800, # 3 hours in seconds
                    uid=q1[0],
                    roles=roles,
                    fullname=fullname
                )
                
                api_message('i', "success login (user_id={0} fullname={1})".format(q1[0], fullname))
                resp.status = falcon.HTTP_OK
                resp.set_header("Access-Control-Allow-Credentials", "true")
                resp.set_cookie(name="Token-Account", value=token, http_only=True, max_age=10800, secure=False, domain=".app.localhost", same_site="None")
                resp.media  = {'title': 'OK', 'description': 'Success to login', 'content': {'uid': q1[0], 'username': fullname, 'roles': roles, 'token': token}}
                return
            else:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'Email or password not found'}
                return