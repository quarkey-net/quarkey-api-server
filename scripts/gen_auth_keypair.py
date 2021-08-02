""" import peewee, datetime, argparse
from database.database import db
from database.models import SQLAuthToken
from utils.security.auth import gen_account_keypair """
from utils.security.auth import gen_account_keypair
from database.database import PGDatabase

if __name__ == "__main__":

    """
    parser = argparse.ArgumentParser(prog="launch", usage='%(prog)s [options] path', description="configure api launching")
    parser.add_argument('--token-name', metavar="token_name", type=str, help="")
    args = parser.parse_args()

    datenow = datetime.datetime.utcnow()
    rsa = gen_account_keypair()

    try:
        db.initialize(peewee.PostgresqlDatabase("quarkey", host="localhost", port=5432, user="postgres", password="root", autocommit=True, autorollback=True))
        db.connect()
    except Exception as e:
        print("Failed to connect to database")
        exit(0)

    q1 = SQLAuthToken.create(token_type=args.token_name, public_key=rsa[0], private_key=rsa[1], updated_at=datenow, created_at=datenow)
    """

    db = PGDatabase()
    conn = db.connect()

    rsa = gen_account_keypair()

    q1 = None
    with conn.cursor() as cur:
        q1 = cur.execute("INSERT INTO auth_token_rsa (type, public_key, private_key) VALUES (%s, %s, %s) RETURNING id", ("account_authentication", rsa[0], rsa[1]))
        conn.commit()
    
    print(q1)