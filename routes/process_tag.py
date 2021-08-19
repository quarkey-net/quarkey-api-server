from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message
from utils.config import AppState


class ProcessTag:

    def __init__(self) -> None:
        self._token_controller = AccountAuthToken('', '')

    @falcon.before(AuthorizeAccount(roles=['standard']))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        tag_id = uuid.uuid4().hex
        q1 = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t1.id, t1.name FROM tags AS t1 WHERE t1.f_owner = %s AND t1.name = %s", (payload["uid"], req.media["name"]))
            q1 = cur.fetchall()

        api_message("d", f'tag SQL request content {q1}')
        if len(q1) > 0:
            resp.media = {"title": "BAD_REQUEST", "description": "tag already exist"}
            return
            
        with AppState.Database.CONN.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO tags (id, f_owner, name, color) VALUES (%s, %s, %s, %s)",
                    (
                        tag_id,
                        payload["uid"],
                        req.media["name"],
                        req.media["color"]
                    )
                )
                AppState.Database.CONN.commit()
            except Exception as e:
                AppState.Database.CONN.rollback()
                api_message("e", f'Failed transaction : {e}')
                raise falcon.HTTPBadRequest()


        resp.status = falcon.HTTP_CREATED
        resp.media = {"title": "CREATED", "description": "tag created successful", "content": {"tag_id": tag_id}}


    @falcon.before(AuthorizeAccount(roles=["standard"]))
    def on_delete(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        tag_id = req.get_param("tag_id")
        tag_name = req.get_param("tag_name")
        q1 = None
        with AppState.Database.CONN.cursor() as cur:
            if tag_name is not None and tag_name != 'global':
                cur.execute("SELECT id FROM tags WHERE f_owner = %s AND name = %s", (payload["uid"], tag_name))
            else:
                cur.execute("SELECT id FROM tags WHERE f_owner = %s AND id = %s AND name != 'global'", (payload["uid"], tag_id))
            q1 = cur.fetchone()

        api_message("d", f'tag id by request : {q1[0]}, type : {type(q1[0])}')
        if q1 is None or len(q1) < 1:
            return

        tag_id = uuid.UUID(q1[0]).hex
        with AppState.Database.CONN.cursor() as cur:
            try:
                cur.execute("DELETE FROM password_tag_linkers WHERE f_tag = %s", (tag_id,))
                cur.execute("DELETE FROM tags AS t1 WHERE t1.id = %s", (tag_id,))
                AppState.Database.CONN.commit()
            except Exception as e:
                AppState.Database.CONN.rollback()
                api_message("e", f'Failed transaction : {e}')
                raise falcon.HTTPBadRequest()
        
        resp.status = falcon.HTTP_OK


    @falcon.before(AuthorizeAccount(roles=["standard"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_400
        payload = self._token_controller.decode(req.get_header('Authorization'))
        q1 = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT id, name, color FROM tags WHERE f_owner = %s AND name != 'global'", (payload["uid"],))
            q1 = cur.fetchall()
        
        if len(q1) < 1:
            resp.status = falcon.HTTP_200 
            resp.media  = {"title": "OK", "description": "Empty tag list"}
            return

        results: list = []
        for x in q1:
            tag_itm: dict = {}
            tag_itm["id"]       = uuid.UUID(x[0]).hex
            tag_itm["name"]     = x[1]
            tag_itm["color"]    = x[2]
            results.append(tag_itm)

        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "tags getted successful", "content": results}
        return