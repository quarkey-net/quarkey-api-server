import falcon, yagmail, datetime, jwt
from utils.security.auth import user_auth_guard, create_verification_token, decode_user_token, UUIDCONVERTER, API_JWT_SECRET
from utils.base import EMAIL, email_confirmation_msg
from database.models import Users


class VerifyAccount(object):

    @falcon.before(user_auth_guard)
    def on_get(self, req, resp, uid):
        return


    def on_post(self, req, resp, uid):
        resp.status = falcon.HTTP_500

        result = decode_user_token(req.get_header("Authorization"))

        if UUIDCONVERTER.convert(result.get("sub")) != uid:
            raise falcon.HTTPNotAcceptable(description="Someone is probably trying to hack the security token")


        try:
            user = Users.get_or_none(Users.uid == uid)
            if user != None:
                if user.verified != True: # à verifier

                    try:
                        res = jwt.decode(user.verification_token, API_JWT_SECRET)
                    except jwt.ExpiredSignatureError:
                        token = create_verification_token()
                        query = Users.update(verification_token=token).where(Users.uid == uid, Users.verified == False, Users.verification_token == None)
                        query.execute()
                        EMAIL.send(to=user.email, subject="QuarKEY Email Confirmation", contents=email_confirmation_msg(user=user.username, token=token.decode()))
                        resp.status = falcon.HTTP_200
                        resp.media = {"code": 0, "message": "The verification email has been sent"}
                        return
                    except Exception as e:
                        print(e)
                
                    resp.status = falcon.HTTP_ALREADY_REPORTED
                    resp.media = {"code": 0, "message": "The verification email still hasn't expired."}
                    return
                    """
                    if res.get("exp") < datetime.datetime.utcnow():
                        token = create_verification_token()
                        query = Users.update(verification_token=token).where(Users.uid == uid, Users.verified == False, Users.verification_token == None)
                        query.execute()
                        EMAIL.send(to=user.email, subject="QuarKEY Email Confirmation", contents=email_confirmation_msg(user=user.username, token=token))
                        resp.status = falcon.HTTP_200
                        resp.media = {"code": 0, "message": "The verification email has been sent"}
                        return
                    else:
                        resp.status = falcon.HTTP_ALREADY_REPORTED
                        resp.media = {"code": 0, "message": "The verification email still hasn't expired."}
                        return
                    """
                else:
                    """ already verified """
                    resp.status = falcon.HTTP_200
                    resp.media = {"code": 0, "message": "User already verified"}
                    return
            else:
                resp.status = falcon.HTTP_401
                resp.media = {"code": 3, "message": "User no exist"}

        except Exception as e:
            print(e)