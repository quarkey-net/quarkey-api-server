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
                cur.execute("SELECT id FROM passwords WHERE f_owner = %s AND name = %s", (payload['uid'], req.media['title']))
                q1 = cur.fetchone()

            if q1 is not None:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = resp.media  = {"title": "BAD_REQUEST", "description": "item already exist"}
                return                

            puuid = uuid.uuid4().hex
            tag_id = uuid.uuid4().hex
            with AppState.Database.CONN.cursor() as cur:
                cur.execute(
                    "INSERT INTO passwords (id, f_owner, name, description, login, password_1, url) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
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
                cur.execute("INSERT INTO tags (id, f_owner, name, color) VALUES (%s, %s, %s, %s)", (tag_id, payload["uid"], "global", "white"))
                cur.execute("INSERT INTO password_tag_linkers (f_password, f_tag) VALUES (%s, %s)", (puuid, tag_id))
                AppState.Database.CONN.commit()

            
        resp.status = falcon.HTTP_CREATED
        resp.media  = {"title": "CREATED", "description": "resource created successful"}


    @falcon.before(AuthorizeAccount(roles=["standard"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        payload = self._token_controller.decode(req.get_header('Authorization'))
        q1 = None
        q2 = None
        columns = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t2.id, t2.type, t2.name, t2.description, t2.login, t2.url, t2.password_1 FROM passwords AS t2 INNER JOIN accounts AS t3 ON t2.f_owner = t3.id WHERE t3.id = %s AND t3.is_banned = FALSE", (payload['uid'],))
            columns = list(cur.description)
            q1 = cur.fetchall()

        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t1.f_password AS password_id, t2.name AS tag_name, t2.color AS tag_color FROM password_tag_linkers AS t1 INNER JOIN tags AS t2 ON t1.f_tag = t2.id WHERE t2.f_owner = %s", (payload["uid"],))
            q2 = cur.fetchall()


        if q1 is None or q2 is None:
            resp.media = {"title": "BAD_REQUEST", "description": "failed to get password items"}
            return
        elif len(q1) < 1:
            resp.media = {"title": "BAD_REQUEST", "description": "empty password items"}
            return
        
        print(q1)

        pass_template = {
            "id": None,
            "type": None,
            "name": None,
            "description": None,
            "login": None,
            "passwords": [],
            "url": None,
            "tags": []
        }
        tag_template = {
            "name": None, 
            "color": None
        }

        results = []
        for x in q1:
            pass_itm = pass_template.copy()
            pass_itm["id"]          = x[0].hex
            pass_itm["type"]        = x[1]
            pass_itm["name"]        = x[2]
            pass_itm["description"] = x[3]
            pass_itm["login"]       = x[4]
            pass_itm["passwords"].append(x[6])
            pass_itm["url"]         = x[5]
            for y in q2:
                print(f'q1 : {x[0]}, q2 : {y[0]}')
                if x[0] == y[0]:
                    print('work')
                    tag_itm = tag_template.copy()
                    tag_itm["name"]     = y[1]
                    tag_itm["color"]    = y[2]
                    pass_itm["tags"].append(tag_itm)
            results.append(pass_itm)

        """
        results: list = []
        for row in q1:
            row_dict: dict = {}
            for i, col in enumerate(columns):
                row_dict[col.name] = row[i]
        results.append(row_dict)
        """

        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "password list getted successful", "content": results}