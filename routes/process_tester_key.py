from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message, gen_random_test_key
from utils.config import AppState


class ProcessTesterKey:

    def __init__(self) -> None:
        self._token_controller = AccountAuthToken('', '')

    @falcon.before(AuthorizeAccount(roles=["standard", "moderator"]))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        account_roles = payload["roles"].split(":")

        """
        roles = req.media["roles"]
        if "moderator" in account_roles:
            for x in roles:
                if x not in ["standard"]:
                    raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="role not defined or not privileges")
        elif "admin" in account_roles:
            for x in roles:
                if x not in ["standard", "moderator", "premium", "verified"]:
                    raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="roles not defined")
        """

        key: str = gen_random_test_key()
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("INSERT INTO tester_keys (id, type, expiration_on) VALUES (%s, %s, %s)", (key, AppState.TAG, expiration))
            AppState.Database.CONN.commit()

        if "moderator" in account_roles:
            resp.media = {"title": "CREATED", "description": "tester key created successful", "content": {"key": key, "type": AppState.TAG, "expiration": expiration.strftime("%d-%m-%Y %H:%M:%S")}}
        else:
            resp.media = {"title": "CREATED", "description": "tester key created successful"}
        resp.status = falcon.HTTP_CREATED
