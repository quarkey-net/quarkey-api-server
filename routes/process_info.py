import os, falcon, psutil
from routes.middleware import AuthorizeResource
from utils.config import AppState

class ProcessApiInfos:
    
    def __init__(self) -> None:
        pass

    @falcon.before(AuthorizeResource(roles=["moderator", "admin"]))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_400
        proc = psutil.Process(AppState.PID).memory_info()
        resp.status = falcon.HTTP_OK
        resp.media  = {"title": "OK", "description": "Worker api infos", "content": {"PID": AppState.PID, "TOTAL_MEMORY": proc.rss / 1024 ** 2}}
        