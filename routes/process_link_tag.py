from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message
from utils.config import AppState


class ProcessLinkTag:

    def __init__(self) -> None:
        self._token_controller = AccountAuthToken('', '')

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        password_id = req.media["password_id"]
        tag_id      = req.media["tag_id"]
        tag_name    = req.media.get("tag_name", None)
        q1 = None
        q2 = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t1.id, t1.name FROM passwords AS t1 WHERE t1.id = %s AND t1.f_owner = %s", (password_id, payload["uid"]))
            q1 = cur.fetchone()
        with AppState.Database.CONN.cursor() as cur:
            if ((tag_name is not None or tag_name != "") and tag_name != "global"):
                cur.execute("SELECT t1.id, t1.name FROM tags AS t1 WHERE t1.name = %s AND t1.f_owner = %s", (tag_name, payload["uid"]))
            else:
                cur.execute("SELECT t1.id, t1.name FROM tags AS t1 WHERE t1.id = %s AND t1.f_owner = %s", (tag_id, payload["uid"]))
            q2 = cur.fetchone()

        if q1 is None or q2 is None:
            return

        if len(q1) > 0 and len(q2) > 0:
            # analyse
            tag_id = uuid.UUID(q2[0]).hex
            with AppState.Database.CONN.cursor() as cur:
                try:
                    cur.execute("INSERT INTO password_tag_linkers (f_password, f_tag) VALUES (%s, %s)", (password_id, tag_id))
                    AppState.Database.CONN.commit()
                except Exception as e:
                    AppState.Database.CONN.rollback()
                    api_message("e", f'Failed transaction : {e}')
                    raise falcon.HTTPBadRequest()
            
            resp.status = falcon.HTTP_CREATED
            resp.media  = {"title": "CREATED", "description": "sucess to attach tag", "content": {"password_id": password_id, "tag_id": tag_id}}
            return

    def on_delete(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        tag_id = req.get_param("tag_id")
        with AppState.Database.CONN.cursor() as cur:
            try:
                cur.execute("DELETE FROM password_tag_linkers AS t1 USING tags AS t2 WHERE t2.f_owner = %s AND t2.name != 'global' AND t1.f_tag = %s AND t2.id = %s", (payload["uid"], tag_id, tag_id))
                AppState.Database.CONN.commit()
            except Exception as e:
                AppState.Database.CONN.rollback()
                api_message("e", f'Failed transaction : {e}')
                raise falcon.HTTPBadRequest()

        resp.status = falcon.HTTP_200

