from utils.config import AppState
import argon2, falcon, datetime
from utils.base import api_message
from authlib import jose

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

UUIDCONVERTER = falcon.routing.UUIDConverter()


def gen_account_keypair() -> list:
    """
    Generate 4096 RSA keypair for account
    . Return list of pem key in bytes
    - KEYPAIR[0] -> public key
    - KEYPAIR[1] -> private key
    """
    
    """ 
    RSAKeys = OpenSSL.crypto.PKey()
    RSAKeys.generate_key(OpenSSL.crypto.TYPE_RSA, 4096)
    privkey = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, RSAKeys, cipher=None, passphrase=None)
    pubkey = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, RSAKeys)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return [public_pem, private_pem] # str
    # return [public_pem, private_pem] # bytes



class AccountAuthToken():

    def __init__(self, pubkey=None, privkey=None) -> None:
        self._pubkey = pubkey
        self._privkey = privkey

    def create(self, duration: int, uid: str, roles: list, fullname: str) -> str:
        api_message("d", f'roles type : {type(roles)}')
        header = {"alg": AppState.AccountToken.TYPE}
        try:
            payload: dict = {
                'uid': uid,
                'username': fullname,
                'roles': roles,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
            }
        except Exception as e:
            api_message('d', f'Failed to deserialize payload : {e}')
        try:
            return jose.jwt.encode(
                header,
                payload,
                AppState.AccountToken.PRIVATE_KEY if AppState.AccountToken.TYPE == "RS256" else AppState.AccountToken.SECRET,
                check=False
            ).decode('utf-8')
        except Exception as e:
            print(f'LOGGING : {AppState.LOGGING_ENABLE}\nSTDOUT : {AppState.STDOUT_ENABLE}\nSTDERR : {AppState.STDERR_ENABLE}')
            api_message('d', f'{e}')
            print(e)
            raise falcon.HTTPInternalServerError(title="account auth token", description=f'{e}')


    def decode(self, token: str) -> dict:
        try:
            token = bytes(token, encoding="utf-8")
            res = jose.jwt.decode(
                token, 
                AppState.AccountToken.PUBLIC_KEY if AppState.AccountToken.TYPE == "RS256" else AppState.AccountToken.SECRET
            )
            res.validate()
            api_message("d", f'payload token content : {res}')
            return res
        except jose.errors.ExpiredTokenError as e:
            api_message('w', "Connection Expired (Signature invalid)")
            raise falcon.HTTPUnauthorized(description='Signature expired. Please log in again.')
        except jose.errors.BadSignatureError as e:
            api_message('w', "Signature Key Invalid. Please login again")
            raise falcon.HTTPForbidden(description='Invalid token. Please log in again.')
        except Exception as e:
            api_message('w', f"unknow exception on decode token function : {e}")
            raise falcon.HTTPForbidden(description="Impossible d'authentifier l'utilisateur")



class EmailAuthToken():

    def __init__(self, pubkey=None, privkey=None) -> None:
        self._pubkey = pubkey
        self._privkey = privkey

    def create(self, duration: int, uid: str, tester_key: str, fullname: str) -> str:
        header = {"alg": "RS256"}
        try:
            payload: dict = {
                'uid': uid,
                'username': fullname, 
                'tester_key': tester_key,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
            }
        except Exception as e:
            api_message('d', f'Failed to deserialize payload : {e}')
        try:
            return jose.jwt.encode(
                header,
                payload,
                AppState.Email.PRIVATE_KEY,
                check=False
            ).decode('utf-8')
        except Exception as e:
            print(f'LOGGING : {AppState.LOGGING_ENABLE}\nSTDOUT : {AppState.STDOUT_ENABLE}\nSTDERR : {AppState.STDERR_ENABLE}')
            api_message('d', f'{e}')
            print(e)
            raise falcon.HTTPInternalServerError(title="email activation token", description=f'{e}')


    def decode(self, token: str) -> dict:
        try:
            token = bytes(token, encoding="utf-8")
            res = jose.jwt.decode(
                token, 
                AppState.Email.PUBLIC_KEY
            )
            res.validate()
            api_message("d", f'payload token content : {res}')
            return res
        except jose.errors.ExpiredTokenError as e:
            api_message('w', "Account activation token expired")
            raise falcon.HTTPNotAcceptable(description='Account activation token expired')
        except jose.errors.BadSignatureError as e:
            api_message('w', "Signature invalid")
            raise falcon.HTTPNotAcceptable(description='Invalid activation token')
        except Exception as e:
            api_message('w', f"unknow exception on decode token during account activation : {e}")
            raise falcon.HTTPNotAcceptable(description="Failed to activate account")

    
        

class UserPasswordHasher():

    def __init__(self, header="$argon2id$v=19$m=102400,t=2,p=8$"):
        self.header = header
        self.hasher = argon2.PasswordHasher()

    def hash_password(self, _password):
        try:
            password = self.hasher.hash(_password)[len(self.header):]
        except Exception as e:
            print("FAILED TO HASH PASSWORD")
            api_message('w', f'Erreur de type, surement parametrer sur null : {e}')
            raise falcon.HTTPBadRequest()
        return password

    def verify_password(self, _hash, _password):
        try:
            _hash = self.header + _hash
            if self.hasher.verify(_hash, _password):
                return True
        except Exception as e:
            print(e)
            return False

        return False