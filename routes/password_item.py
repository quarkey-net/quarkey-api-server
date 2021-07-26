from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message
from database.models import PasswordItems
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
            api_message("d", f'request media type : {type(req.media)}')
            payload = self._token_controller.decode(req.get_header('Authorization'))

            try:
                q1 = PasswordItems.select(
                    PasswordItems.id
                ).where((PasswordItems.f_owner == payload['uid']) & (PasswordItems.title == req.media['title']))
            except Exception as e:
                api_message("d", f'failed to get item {e}')
                raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="failed to get item")

            if q1.count() > 0:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media  = resp.media  = {"title": "BAD_REQUEST", "description": "item already exist"}
                return

            datenow = datetime.datetime.utcnow()
            try:
                q2 = PasswordItems.create(
                    id=uuid.uuid4(),
                    f_owner=payload['uid'],
                    title=req.media['title'],
                    description=req.media['description'],
                    username=req.media['username'],
                    password=req.media['password'],
                    url=req.media['url'],
                    updated_on=datenow,
                    created_on=datenow
                )
            except Exception as e:
                api_message("d", f'exception during password item creation : {e}')
                raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="failed to create item")
            
        resp.status = falcon.HTTP_CREATED
        resp.media  = {"title": "CREATED", "description": "resource created successful"}


"""
    @falcon.before(AuthorizeAccount(roles=['standard']))
    def on_get(self, req, resp, uid):
        resp.status = falcon.HTTP_400

        premium = decode_user_token(req.get_header('Authorization'))["premium"]

        try:
            if "num" in req.params:
                i_number = int(req.params.get("num"))
                if i_number > 12 and premium != True:
                    query = PasswordItems.select(PasswordItems.title,
                        PasswordItems.description, 
                        PasswordItems.username,
                        PasswordItems.password
                    ).where(PasswordItems.owner == uid).order_by(PasswordItems.created_date).limit(12).dicts()
                else:
                    query = PasswordItems.select(PasswordItems.title, 
                        PasswordItems.description, 
                        PasswordItems.username, 
                        PasswordItems.password
                    ).where(PasswordItems.owner == uid).order_by(PasswordItems.created_date).limit(i_number).dicts()
                items = []
                for row in query:
                    items.append(row)

                result = {"number": len(items), "items": items}
                resp.status = falcon.HTTP_200
                resp.media = result
                return
            else:
                resp.status = falcon.HTTP_403
                resp.media = {"code": 12, "message": "Invalid parameter(s)"}
                return
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.media = {"code": 1, "message": f"Unknow error : {e}"}
            return
"""
