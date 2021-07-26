import peewee

db = peewee.DatabaseProxy()

""" 
def get_database(file='./quark.json', deploy_mod="test"):

    with open(file, 'r') as desc:
        conf = json.load(desc)[deploy_mod]["SGBD"]
    
    if conf.get("type") == "SQLITE":
        db = peewee.SqliteDatabase(conf["options"]["file"])
        db.connect()
        print(f"[DATABASE] SUCCESS TO CONNECT TO SQLite Database")
        return db
    elif conf.get("type") == "MYSQL":
        options = conf["options"]
        db = peewee.MySQLDatabase(options["name"], host=options["host"], port=options["port"], user=options["user"], password=options["pass"], autocommit=True, autorollback=True)
        db.connect()
        print(f"[DATABASE] SUCCESS TO CONNECT TO MySQL Database")
        return db
    elif conf.get("type") == "POSTGRESQL":
        options = conf["options"]
        db = peewee.PostgresqlDatabase(options["name"], host=options["host"], port=options["port"], user=options["user"], password=options["pass"], autocommit=True, autorollback=True)
        db.connect()
        print(f"[DATABASE] SUCCESS TO CONNECT TO PostgreSQL Database")
        return db
    else:
        print(f"[DATABASE] ERROR no supporting database")
        exit(0)
    

db = get_database()     
"""
