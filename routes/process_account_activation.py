from utils.security.auth import AccountAuthToken, gen_account_keypair, EmailAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeResource
from utils.base import api_validate_form, api_message, email_confirmation_msg
from utils.config import AppState


class ProcessAccountActivation(object):

    def __init__(self) -> None:
        # self._token_controller = AccountAuthToken()
        self._email_token_controller = EmailAuthToken()

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        # 1 : Decode and verify activation token (encode tester_key and uid in token)
        # 2 : Get content of activation token
        # 3 : Make atomic transaction and set columns : roles, activated_on and rsa keypair
        activation_token: str = req.get_param("token", None)
        # verify token and get payload
        payload: dict = self._email_token_controller.decode(activation_token)
        username: str    = payload["uid"]
        tester_key: str  = payload["tester_key"]

        q1 = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT activated_on FROM accounts WHERE id = %s AND activated_on IS NULL", (username,))
            q1 = cur.fetchone()

        # return error if account is already activated or not found
        if q1 is None:
            raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="account already activated or not found")

        rsa: list = gen_account_keypair()
        with AppState.Database.CONN.cursor() as cur:
            try:
                cur.execute("UPDATE accounts SET public_key = %s, private_key = %s, roles = %s, activated_on = (NOW() AT TIME ZONE 'utc') WHERE id = %s", (rsa[0], rsa[1], ["standard"], username))
            except Exception as e:
                api_message("w", f'failed transaction to activate account (uid=\'{username}\')')
                AppState.Database.CONN.rollback()
                raise falcon.HTTPBadRequest()
            AppState.Database.CONN.commit()

        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "Success to activate account"}


