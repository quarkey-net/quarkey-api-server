from utils.security.auth import AccountAuthToken
import falcon, uuid, datetime, os

from routes.middleware import AuthorizeAccount
from utils.base import api_validate_form, api_message
from utils.config import AppState

class ProcessGenData:

    @falcon.before(AuthorizeAccount(roles=["moderator", "admin"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_BAD_REQUEST
        user_list_file = "routes/tools/user_list.txt"
        email_list_file = "routes/tools/email_list.txt"
        if not os.path.isfile(user_list_file) or not os.path.isfile(email_list_file):
            raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="files not found")
        
        try:
            rtype = req.get_param("type").split(",") # user and email
            rnum  = int(req.get_param("num"))
        except:
            raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="Please specify type and integer number")

        for x in rtype:
            if x not in ["user", "email"]:
                raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="Invalid type")

        result = {}
        for y in rtype:
            result[y] = []
            if y == "user":
                sfile = open(user_list_file, "r")
            elif y == "email":
                sfile = open(email_list_file, "r")
            try:
                tmp = sfile.readlines()
                num = rnum
                if len(tmp) < num:
                    num = len(tmp)
                for x in range(0, num):
                    result[y].append(tmp[x].strip())
            except Exception as e:
                api_message("d", f'error : {e}')
                sfile.close()
                raise falcon.HTTPBadRequest()
            sfile.close()
        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "list getted successful", "content": result}