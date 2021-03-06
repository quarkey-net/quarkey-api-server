import peewee, datetime
from .database import db

class PgSQLBaseModel(peewee.Model):
    """ Reference to Postgresql Database """
    class Meta:
        database = db

    @classmethod
    def using(cls, db):
        cls._meta.database.initialize(db)
        return cls



class SQLAccounts(PgSQLBaseModel):
    """ SQL Accounts database table """

    uid                 = peewee.TextField(null=False, primary_key=True, unique=True)

    firstname           = peewee.TextField(null=False, unique=False)
    lastname            = peewee.TextField(null=False, unique=False)
    email               = peewee.TextField(null=False, unique=True)
    password            = peewee.TextField(null=False, unique=False)

    public_key          = peewee.BlobField(null=False, unique=False)
    private_key         = peewee.BlobField(null=False, unique=False)

    role                = peewee.TextField(null=False, unique=True)
    is_verified         = peewee.BooleanField(null=False, unique=False, default=False)
    is_banned           = peewee.BooleanField(null=False, unique=False, default=False)
    premium_expiration  = peewee.DateTimeField(null=False, unique=False, default=datetime.datetime.utcnow())

    updated_on          = peewee.DateTimeField(null=False, unique=False)
    created_on          = peewee.DateTimeField(null=False, unique=False)

    class Meta:
        table_name = 'accounts'



class SQLPasswords(PgSQLBaseModel):
    """ SQL Database table to describe Password slot items """

    id                  = peewee.UUIDField(primary_key=True, null=False, unique=True)

    f_owner             = peewee.ForeignKeyField(SQLAccounts, backref="password_items")
    title               = peewee.TextField(null=False, unique=False)
    description         = peewee.TextField(null=True, unique=False)
    username            = peewee.TextField(null=True, unique=False)
    password            = peewee.TextField(null=False, unique=False)
    url                 = peewee.TextField(null=True, unique=False)

    updated_on          = peewee.DateTimeField(null=False, unique=False, default=datetime.datetime.utcnow())
    created_on          = peewee.DateTimeField(null=False, unique=False, default=datetime.datetime.utcnow())

    class Meta:
        table_name = 'passwords'



class SQLTags(PgSQLBaseModel):
    """ SQL Database table to describe tags and color for an item password """

    id                  = peewee.BigIntegerField(null=False, unique=True, primary_key=True)
    name                = peewee.TextField(null=False, unique=False)
    color               = peewee.TextField(null=False, unique=False)

    class Meta:
        table_name = 'tags'



class SQLPasswordsTags(PgSQLBaseModel):
    """ Many to many SQL database table (password_items <-> tags) """
    id                  = peewee.BigIntegerField(null=False, unique=True, primary_key=True)
    f_item              = peewee.ForeignKeyField(SQLPasswords, null=False, unique=False)
    f_tag               = peewee.ForeignKeyField(SQLTags, null=True, unique=False)
    # f_org             = peewee.ForeignKeyField(null=False, unqiue=False)

    class Meta:
        table_name = "passwords_tags"



class SQLAuthToken(PgSQLBaseModel):
    """ SQL database table to describe rsa keypair for specific service"""
    # id
    token_type          = peewee.TextField(null=False, unique=True)

    public_key          = peewee.BlobField(null=False, unique=False)
    private_key         = peewee.BlobField(null=False, unique=False)

    updated_on          = peewee.DateTimeField(null=False, unique=False, default=datetime.datetime.utcnow())
    created_on          = peewee.DateTimeField(null=False, unique=False, default=datetime.datetime.utcnow())

    class Meta:
        table_name = 'auth_token_rsa'




    
