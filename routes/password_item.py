from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeResource
from utils.base import api_validate_form, api_message
from utils.config import AppState


class PasswordItem(object):

    def __init__(self):
        self._token_controller = AccountAuthToken('', '')
        self.post_form = {
            "$schema": AppState.Tools.JSONSCHEMA_VERSION,
            "type": "object",
            "properties": {
                "name"          : {"type": "string"},
                "description"   : {"type": "string"},
                "login"         : {"type": "string"},
                "password"      : {"type": "string"},
                "url"           : {"type": "string"}
            },
            "required": ["name", "password"]
        }

    def on_options(self, req, resp):
        resp.set_header('Access-Control-Allow-Headers', '*')

    @falcon.before(AuthorizeResource(roles=['standard']))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_400
        if api_validate_form(req.media, self.post_form):
            # payload = self._token_controller.decode(req.get_header('Authorization'))
            payload = self._token_controller.decode(req.get_cookie_values("Authorization"))
            q1 = None
            with AppState.Database.CONN.cursor() as cur:
                cur.execute("SELECT id FROM passwords WHERE f_owner = %s AND name = %s", (payload['uid'], req.media['name']))
                q1 = cur.fetchone()

            if q1 is not None:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = resp.media  = {"title": "BAD_REQUEST", "description": "item already exist"}
                return                

            puuid = uuid.uuid4().hex
            tag_id = uuid.uuid4().hex
            with AppState.Database.CONN.cursor() as cur:
                try:
                    cur.execute(
                        "INSERT INTO passwords (id, f_owner, name, description, login, password_1, url) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (
                            puuid,
                            payload['uid'],
                            req.media['name'],
                            req.media['description'],
                            req.media['login'],
                            req.media['password'],
                            req.media['url']
                        )
                    )
                    cur.execute("INSERT INTO tags (id, f_owner, name, color) VALUES (%s, %s, %s, %s)", (tag_id, payload["uid"], "global", "white"))
                    cur.execute("INSERT INTO password_tag_linkers (f_password, f_tag) VALUES (%s, %s)", (puuid, tag_id))
                    AppState.Database.CONN.commit()
                except Exception as e:
                    AppState.Database.CONN.rollback()
                    api_message("e", f'Failed transaction : {e}')
                    raise falcon.HTTPBadRequest()

            
        resp.status = falcon.HTTP_CREATED
        resp.media  = {"title": "CREATED", "description": "resource created successful", "content": {"password_id": uuid.UUID(puuid).hex}}



    @falcon.before(AuthorizeResource(roles=["standard"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        # payload = self._token_controller.decode(req.get_header('Authorization'))
        payload = self._token_controller.decode(req.get_cookie_values("Authorization"))
        q1 = None
        q2 = None
        password_columns = None
        tag_columns = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t2.id, t2.type, t2.name, t2.description, t2.login, t2.url, t2.password_1, t2.password_2 FROM passwords AS t2 INNER JOIN accounts AS t3 ON t2.f_owner = t3.id WHERE t3.id = %s AND t3.is_banned = FALSE", (payload['uid'],))
            # password_columns = list(cur.description)
            q1 = cur.fetchall()

        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t1.f_password AS password_id, t2.id AS tag_id, t2.name AS tag_name, t2.color AS tag_color FROM password_tag_linkers AS t1 INNER JOIN tags AS t2 ON t1.f_tag = t2.id WHERE t2.f_owner = %s", (payload["uid"],))
            # tag_columns = list(cur.description)
            q2 = cur.fetchall()


        if q1 is None or q2 is None:
            resp.media = {"title": "BAD_REQUEST", "description": "failed to get password items"}
            return
        elif len(q1) < 1:
            resp.status = falcon.HTTP_200
            resp.media = {"title": "BAD_REQUEST", "description": "empty password items", "content": {"item_number": 0, "item": []}}
            return


        tag_list_id: list = []
        for i in q2:
            tag_list_id.append(uuid.UUID(i[1]).hex)
        tag_list_id = list(set(tag_list_id))


        tag_slot: list = []
        for c in tag_list_id:
            for z in q2:
                if uuid.UUID(z[1]).hex == c:
                    if z[2] != 'global':
                        tag_slot.append({
                            "id": c,
                            "name": z[2],
                            "color": z[3],
                            "items": []
                        })

        items: list = []
        for x in q1:
            pass_itm: dict = {}
            pass_itm["id"]      = uuid.UUID(x[0]).hex
            pass_itm["type"]    = x[1]
            pass_itm["name"]    = x[2]
            pass_itm["description"] = x[3]
            pass_itm["login"]       = x[4]
            pass_itm["password"] = []
            pass_itm["password"].append(x[6])
            pass_itm["password"].append(x[7])
            pass_itm["url"]         = x[5]
            pass_itm["tags"]        = []
            for y in q2:
                if uuid.UUID(x[0]).hex == uuid.UUID(y[0]).hex:
                    tag_itm: dict = {}
                    tag_itm["id"] = uuid.UUID(y[1]).hex
                    tag_itm["name"] = y[2]
                    tag_itm["color"] = y[3]
                    pass_itm["tags"].append(tag_itm)
            items.append(pass_itm)

        tag_slot: list = []
        for c in tag_list_id:
            for z in q2:
                if uuid.UUID(z[1]).hex == c:
                    if z[2] != 'global':
                        slot = {
                            "id": c,
                            "name": z[2],
                            "color": z[3],
                            "items": []
                        }
                        for v in items:
                            for u in v["tags"]:
                                if c == u["id"]:
                                    slot["items"].append(v["id"])
                                    break
                        tag_slot.append(slot)
                                    
        


        resp.set_header("Access-Control-Allow-Credentials", "true")
        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "password list getted successful", "content": {"username": payload["uid"], "username": payload["username"], "item_number": len(items), "items" : items, "tag_slot": tag_slot}}
        return



    @falcon.before(AuthorizeResource(roles=["standard"]))
    def on_delete(self, req, resp):
        resp.status = falcon.HTTP_400
        payload = self._token_controller.decode(req.get_header('Authorization'))
        password_id = req.get_param("password_id")
        tag_global_id = None
        with AppState.Database.CONN.cursor() as cur:
            cur.execute("SELECT t2.id FROM password_tag_linkers AS t1 INNER JOIN tags AS t2 ON t1.f_tag = t2.id WHERE t1.f_password = %s AND t2.f_owner = %s AND t2.name = 'global'", (password_id, payload["uid"]))
            tag_global_id = cur.fetchone()[0].hex

        if tag_global_id is None:
            return

        with AppState.Database.CONN.cursor() as cur:
            try:
                cur.execute("DELETE FROM password_tag_linkers AS t1 USING passwords AS t2 WHERE t1.f_password = %s AND t2.id = %s AND t2.f_owner = %s", (password_id, password_id, payload["uid"]))
                cur.execute("DELETE FROM tags AS t1 WHERE id = %s", (tag_global_id,))
                cur.execute("DELETE FROM passwords WHERE id = %s AND f_owner = %s", (password_id, payload["uid"]))
                AppState.Database.CONN.commit()
            except Exception as e:
                AppState.Database.CONN.rollback()
                api_message("e", f'Failed transaction : {e}')
                raise falcon.HTTPBadRequest()
        
        resp.status = falcon.HTTP_200