from __future__ import print_function
import datetime, falcon, jsonschema, sys, logging, os, random
from utils.config import AppState

# EMAIL = yagmail.SMTP(API_DEV_EMAIL_EXPEDITOR, API_DEV_EMAIL_PASSWORD)

def email_confirmation_msg(user, token="http://api.quarkey.co/v1/verify_account?token=klzagcfberzgujkfucerybgvbyjgbtyjrgbyufzjcecgf"):
    return f"Hi {user} !\n\nPlease click on the link to confirm your email address.\nlink : {token}"


def eprint(*args, **kwargs) -> None:
    """ Print stderr """
    print(*args, file=sys.stderr, **kwargs)


def check_form(media: dict, form: list, allow_null=[]):
    """ Obsolete function """
    if media == None:
        return False
    
    media_list = list(media)
     
    for i in form:
        if None in media_list or i not in media_list:
            return False

    for x in media:
        if media.get(x) == None and x not in allow_null:
            return False
            
    return True


def api_message(type: str, msg: str, log: bool = True) -> None:

    color: str = ""
    end: str = "\x1b[0m"
    if type == 'c':
        if AppState.LOGGING_ENABLE and log:
            logging.critical(msg)
        color = "\x1b[7;35;40m"
    elif type == 'e':
        if AppState.LOGGING_ENABLE and log:
            logging.error(msg)
        color   = "\x1b[5;30;41m"
    elif type == 'w':
        if AppState.LOGGING_ENABLE and log:
            logging.warning(msg)
        color = "\x1b[5;30;43m"
    elif type == 'i':
        if AppState.LOGGING_ENABLE and log:
            logging.info(msg)
        color    = "\x1b[5;30;47m"
    elif type == 'd':
        if AppState.LOGGING_ENABLE and log:
            logging.debug(msg)
        color   = "\x1b[5;30;44m"
    else:
        if AppState.STDERR_ENABLE:
            eprint(msg)

    if type in ['c', 'e'] and AppState.STDERR_ENABLE:
        eprint("{0}[{1}]{2} {3}".format(color, datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), end, msg))

    if type in ['w', 'i', 'd'] and AppState.STDOUT_ENABLE:
        print("{0}[{1}]{2} {3}".format(color, datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), end, msg))



    
def get_rsa_keypair(token_type: str = None) -> list:
    """
    Get the public and private key in list from 
    auth_token_rsa table in database. 
    - KEYPAIR[0] -> public key
    - KEYPAIR[1] -> private key
    """
    result = None
    with AppState.Database.CONN.cursor() as cur:
        cur.execute("SELECT public_key, private_key FROM auth_token_rsa WHERE type = %s", (token_type,))
        result = cur.fetchone()
    AppState.Database.CONN.commit()
    print(f'pubkey : {result[0]}')
    try:
        return [result[0], result[1]]
        """         
        RSAKEYS.insert(0, str(q[0]["public_key"]))
        RSAKEYS.insert(1, str(q[0]["private_key"]))
        """
    except Exception as e:
        print(f'[ ERROR ] - No rsa jwt key available in database : {e}, in file {__file__}')




def api_validate_form(media: dict, schema: dict) -> bool:
    """ Valide http json form and catch them """
    try:
        jsonschema.validate(media, schema)
    except Exception as e:
        api_message('w', "Request form not found")
        raise falcon.HTTPBadRequest(title="BAD_REQUEST", description="Request form not found")
    else:
        return True


def is_set(var: str) -> bool:
    """Check if variable is define localy or globaly"""
    if var in globals() or var in locals():
        return True
    return False


def read_file(file_path : str, block_size: int = 1024, mode: str = 'rb') -> bytes:
    """This function is optimized to read big file size"""

    if (os.path.isfile(file_path)):
        with open(file_path, mode) as f:
            while True:
                block = f.read(block_size)
                if block:
                    yield block
                else:
                    return
    else:
        raise FileNotFoundError


def gen_random_test_key() -> str:
    """ Generate 20 characters hexadecimal for tester key """
    chain: str = "0123456789ABCDEF"
    key: list = []
    for x in range(1, 21):
        idx = random.randint(0, len(chain) - 1)
        key.append(chain[idx])
    return "".join(key)


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size