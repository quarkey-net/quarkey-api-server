from utils.config import AppState
import argon2, falcon, datetime
from utils.base import api_message
from authlib import jose

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

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

    def __init__(self, pubkey, privkey) -> None:
        self._pubkey = pubkey
        self._privkey = privkey

    def create(self, duration: int, uid: str, roles: list, fullname: str) -> str:
        roles: str = ':'.join(roles)
        header = {"alg": AppState.AccountToken.TYPE}
        try:
            payload: dict = {
                'uid': uid,
                'fullname': fullname,
                'roles': roles,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
            }
        except Exception as e:
            api_message('d', f'Failed to deserialize payload : {e}')
        try:
            return jose.jwt.encode(
                header,
                payload,
                AppState.AccountToken.PRIVATE if AppState.AccountToken.TYPE == "RS256" else AppState.AccountToken.SECRET,
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
                AppState.AccountToken.PUBLIC if AppState.AccountToken.TYPE == "RS256" else AppState.AccountToken.SECRET
            )
            res.validate()
            api_message("d", f'payload token content : {res}')
            return res
        except jose.errors.ExpiredTokenError as e:
            api_message('w', "Connection Expired (Signature invalid)")
            raise falcon.HTTPNotAcceptable(description='Signature expired. Please log in again.')
        except jose.errors.BadSignatureError as e:
            api_message('w', "Signature Key Invalid. Please login again")
            raise falcon.HTTPNotAcceptable(description='Invalid token. Please log in again.')
        except Exception as e:
            api_message('w', f"unknow exception on decode token function : {e}")
            raise falcon.HTTPNotAcceptable(description="Impossible d'authentifier l'utilisateur")

    
        

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



def encrypt_AES_GCM(msg: str, password: bytes) -> tuple:
    kdfSalt = b'$' + get_random_bytes(30) + b'$'
    try:
        msg = msg.encode(encoding='utf-8', errors='strict')
        secretKey = argon2.hash_password_raw(password, hash_len=32, type=argon2.Type.ID, salt=kdfSalt)
        aesCipher = AES.new(key=secretKey, mode=AES.MODE_GCM, nonce=get_random_bytes(64))
        ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
    except Exception as e:
        api_message("w", f'Failed to encrypt data : {e}')
        raise falcon.HTTPBadRequest()
    return (kdfSalt, ciphertext, aesCipher.nonce, authTag)



def decrypt_AES_GCM(encryptedMsg: tuple, password: bytes):
    (kdfSalt, ciphertext, nonce, authTag) = encryptedMsg
    try:
        secretKey = argon2.hash_password_raw(password, hash_len=32, type=argon2.Type.ID, salt=kdfSalt)
        aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
        plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    except Exception as e:
        api_message("w", f'Failed to decrypt data : {e}')
        raise falcon.HTTPBadRequest()
    return plaintext