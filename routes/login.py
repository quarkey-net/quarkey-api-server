import falcon, datetime
from utils.base import api_message, api_validate_form
from utils.security.auth import AccountAuthToken, UserPasswordHasher
from utils.config import AppState

class Login(object):

    def __init__(self):
        """
        self.username_regex     = "^(?=[a-zA-Z0-9._]{3,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"
        self.password_regex     = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"
        """
        self.token_controller = AccountAuthToken('', '')
        self.password_hasher    = UserPasswordHasher()
        self.get_form          = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "uid"       : {"type": "string", "pattern": "^(?=[a-zA-Z0-9._]{3,15}$)(?!.*[_.]{2})[^_.].*[^_.]$"},
                "password"  : {"type": "string", "pattern": "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,60}$"}
            },
            "required": ["uid", "password"]
        }

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_400

        if api_validate_form(req.media, self.get_form):
            q1 = None
            with AppState.Database.CONN.cursor() as cur:
                cur.execute(
                    "SELECT t1.id, CONCAT(t1.firstname, ' ', t1.lastname) AS fullname, t1.password, t1.roles, t1.subscription_exp, t2.id AS tester_key, t2.type AS tester_type, t2.expiration_on AS tester_expiration FROM accounts AS t1 INNER JOIN tester_keys AS t2 ON t1.f_tester_key = t2.id WHERE t1.is_banned = FALSE AND t1.id = %s AND t2.type = %s AND t2.expiration_on > CURRENT_TIMESTAMP LIMIT 1",
                    (
                        req.media["uid"],
                        AppState.TAG
                    )
                )
                q1 = cur.fetchone()

            if q1 is None or not q1:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'username or password not found'}
                return

            fullname: str = q1[1]
            password: str =q1[2]
            roles: list = q1[3].split(':')
            subscription_exp = q1[4]

            if self.password_hasher.verify_password(password, req.media['password']):
                if subscription_exp.replace(tzinfo=None) > datetime.datetime.utcnow():
                    roles.append('premium')

                api_message('d', f'pub type {type(AppState.AccountToken.PUBLIC)}')
                token = self.token_controller.create(
                    duration=3000,
                    uid=q1[0],
                    roles=roles,
                    fullname=fullname
                )
                api_message('i', "success login (user_id={0} fullname={1})".format(q1[0], fullname))
                resp.status = falcon.HTTP_OK
                resp.media  = {'title': 'OK', 'description': 'success to login', 'content': {'token': token}}
                return
            else:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = {'title': 'BAD_REQUEST', 'description': 'username or password not found'}
                return