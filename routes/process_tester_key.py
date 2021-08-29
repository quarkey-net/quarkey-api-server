from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeResource
from utils.base import api_validate_form, api_message, gen_random_test_key
from utils.config import AppState


class ProcessTesterKey:

    def __init__(self) -> None:
        self._token_controller = AccountAuthToken('', '')

    @falcon.before(AuthorizeResource(roles=["standard", "moderator"]))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        account_roles = payload["roles"]
        email_dst = req.media.get("email", None)

        if email_dst is None and "moderator" not in account_roles:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media  = {"title": "BAD_REQUEST", "description": "please specify the email to which to send the referral link"}
            return

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
            try:
                cur.execute(
                    "INSERT INTO tester_keys (id, type, expiration_on, f_refferer, email_recipient) VALUES (%s, %s, %s, %s, %s)", 
                    (
                        key, 
                        AppState.TAG, 
                        expiration,
                        payload["uid"],
                        email_dst
                    )
                )
                AppState.Database.CONN.commit()
            except Exception as e:
                AppState.Database.CONN.rollback()
                api_message("e", f'Failed transaction : {e}')
                raise falcon.HTTPBadRequest()

        if "moderator" in account_roles:
            resp.media = {"title": "CREATED", "description": "tester key created successful", "content": {"key": key, "type": AppState.TAG, "expiration": expiration.strftime("%d-%m-%Y %H:%M:%S"), "send_to": email_dst}}
        else:
            resp.media = {"title": "CREATED", "description": f'tester key send to {email_dst}'}
        resp.status = falcon.HTTP_CREATED
