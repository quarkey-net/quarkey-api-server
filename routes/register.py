import falcon, datetime

from git import exc
from utils.security.auth import EmailAuthToken, UserPasswordHasher, gen_account_keypair
from utils.config import AppState
from utils.base import api_validate_form, api_message

class Register(object):

    def __init__(self):
        self.password_hasher    = UserPasswordHasher()
        self._email_token_controller = EmailAuthToken()
        self.post_form          = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "username"  : {"type": "string", "pattern": "^(?=[a-zA-Z0-9._]{3,24}$)(?!.*[_.]{2})[^_.].*[^_.]$"},
                "firstname" : {"type": "string", "minLength": 2, "maxLength": 20},
                "lastname"  : {"type": "string", "minLength": 2, "maxLength": 20},
                "email"     : {"type": "string", "format": "email", "pattern": "^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"},
                "password"  : {"type": "string", "pattern": "^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,128}$"},
                "key"       : {"type": "string", "minLength": 20, "maxLength": 20}
            },
            "required": ["username", "firstname", "lastname", "email", "password", "key"]
        }


    def on_post(self, req, resp):
        resp.status         = falcon.HTTP_400

        if api_validate_form(req.media, self.post_form):
            q1 = None
            q2 = None
            with AppState.Database.CONN.cursor() as cur:
                cur.execute("SELECT id FROM tester_keys WHERE id = %s AND type = %s AND expiration_on > CURRENT_TIMESTAMP AND f_owner IS NULL LIMIT 1", (req.media["key"], AppState.TAG))
                q1 = cur.fetchone()

            if q1 is None:
                api_message('d', "key invalid, expired or already activated")
                resp.status = falcon.HTTP_400
                resp.media = {'title': 'BAD_REQUEST', 'description': 'key invalid, expired or already activated'}
                return

            key_id: int = q1[0]
            print(f'key id : {key_id}')

            with AppState.Database.CONN.cursor() as cur:
                cur.execute("SELECT id, email, roles FROM accounts WHERE id = %s OR email = %s", (req.media['username'], req.media["email"]))
                q2 = cur.fetchone()

            if q2 is None:
                # keypair = gen_account_keypair()
                # datenow = datetime.datetime.utcnow()
                with AppState.Database.CONN.cursor() as cur:
                    try:
                        cur.execute(
                            "INSERT INTO accounts (id, firstname, lastname, email, password) VALUES (%s, %s, %s, %s, %s)",
                            (
                                req.media['username'],
                                req.media['firstname'],
                                req.media['lastname'],
                                req.media['email'],
                                self.password_hasher.hash_password(req.media['password'])
                            )
                        )
                        cur.execute("UPDATE tester_keys SET f_owner = %s WHERE id = %s", (req.media["username"], key_id))
                    except Exception as e:
                        AppState.Database.CONN.rollback()
                        api_message("e", f'Failed transaction : {e}')
                        raise falcon.HTTPBadRequest()
                # gen activation token and send it
                try:
                    activation_token: str = self._email_token_controller.create(
                        duration=86400,
                        uid=req.media["username"],
                        tester_key=req.media["key"]
                    )
                    activation_link = f'https://quarkey.com/active/account?token={activation_token}'
                    AppState.Email.CONN.send(to=req.media["email"], subject="Quarkey Account Activation", contents=f'Hi {req.media["firstname"]} !\n\nHere is your activation key for your Quarkey account :\n{activation_link}')
                except Exception as e:
                    api_message("w", f'Failed to send verification email, error : {e}')
                    AppState.Database.CONN.rollback()
                    raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="Failed to send activation email, register aborted!")
                AppState.Database.CONN.commit()
                # response success
                api_message('d', "successfull register (user=\"{0}\", uid={1})".format(req.media['firstname'] + ' ' + req.media['lastname'], req.media['username']))
                resp.status = falcon.HTTP_201
                resp.media = {'title': 'CREATED', 'description': 'accounts created successfull', "content": {"activation_link": f'http://quarkey.herokuapp.com/api/activate/account?token={activation_token}'}}
                return
            else:
                resp.status = falcon.HTTP_400
                resp.media = {'title': 'BAD_REQUEST', 'description': 'username or email already exist'}
                return