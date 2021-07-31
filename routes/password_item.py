from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message
from utils.config import AppState


class PasswordItem(object):

    def __init__(self):
        self._token_controller = AccountAuthToken('', '')
        self.post_form = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "title"         : {"type": "string"},
                "description"   : {"type": "string"},
                "username"      : {"type": "string"},
                "password"      : {"type": "string"},
                "url"           : {"type": "string"}
            },
            "required": ["title", "password"]
        }

    @falcon.before(AuthorizeAccount(roles=['standard']))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_400
        if api_validate_form(req.media, self.post_form):
            payload = self._token_controller.decode(req.get_header('Authorization'))
            q1 = None
            with AppState.Database.CONN.cursor() as cur:
                cur.execute("SELECT id FROM passwords WHERE f_owner = %s AND title = %s", (payload['uid'], req.media['title']))
                q1 = cur.fetchone()

            if q1 is not None:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = resp.media  = {"title": "BAD_REQUEST", "description": "item already exist"}
                return                

            puuid = uuid.uuid4().hex
            with AppState.Database.CONN.cursor() as cur:
                cur.execute(
                    "INSERT INTO passwords (id, f_owner, name, description, username, password, url) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (
                        puuid,
                        payload['uid'],
                        req.media['title'],
                        req.media['description'],
                        req.media['username'],
                        req.media['password'],
                        req.media['url']
                    )
                )
                cur.execute("INSERT INTO password_tag_linkers (f_password, f_tag) VALUES (%s, %s)", (puuid, None))
                AppState.Database.CONN.commit()

            
        resp.status = falcon.HTTP_CREATED
        resp.media  = {"title": "CREATED", "description": "resource created successful"}


    @falcon.before(AuthorizeAccount(roles=["standard"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        q1 = None
        columns = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t2.name, t2.description, t2.login, t2.password, t2.url, t4.name AS tag_name, t4.color AS tag_color FROM password_tag_linkers AS t1 INNER JOIN passwords AS t2 ON t1.f_password = t2.id INNER JOIN accounts AS t3 ON t2.f_owner = t3.id LEFT JOIN tags AS t4 ON t1.f_tag = t4.id WHERE t3.id = %s AND t3.is_banned = FALSE", (payload['uid'],))
            columns = list(cur.description)
            q1 = cur.fetchall()

        if q1 is None:
            resp.media = {"title": "BAD_REQUEST", "description": "failed to get password items"}
            return
        elif len(q1) < 1:
            resp.media = {"title": "BAD_REQUEST", "description": "empty password items"}
            return
        
        print(q1)

        results: list = []
        for row in q1:
            row_dict: dict = {}
            for i, col in enumerate(columns):
                row_dict[col.name] = row[i]
        results.append(row_dict)

        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "password list getted successful", "content": results}