-- Author : Estéban Ristich <esteban.ristich@protonmail.com>

SELECT 'CREATE DATABASE quarkey ENCODING ''UTF8'''
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quarkey')\gexec

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS accounts (
    id                  UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT uuid_generate_v4(),

    username            VARCHAR(20) NOT NULL,
    email               VARCHAR(150) NOT NULL UNIQUE,
    password            VARCHAR(256) NOT NULL,

    public_key          BYTEA DEFAULT NULL,
    private_key         BYTEA DEFAULT NULL,
    roles               TEXT ARRAY DEFAULT NULL,

    activated_on        TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
    subscription_exp    TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    is_banned           BOOLEAN NOT NULL DEFAULT FALSE, -- set obsolete in future

    updated_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    created_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);


-- Add refferal account
CREATE TABLE IF NOT EXISTS tester_keys (
    id                  VARCHAR(20) PRIMARY KEY NOT NULL UNIQUE,
    type                VARCHAR(6) NOT NULL,
    f_owner             UUID UNIQUE DEFAULT NULL,
    f_refferer          UUID NOT NULL,
    email_recipient     VARCHAR(150) NULL,
    expiration_on       TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc'),
    created_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    CONSTRAINT fk_refferer
        FOREIGN KEY (f_refferer)
            REFERENCES accounts(id),
    CONSTRAINT fk_owner
        FOREIGN KEY (f_owner) 
            REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS passwords (
    id                  UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    f_owner             UUID NOT NULL,
    type                VARCHAR(10) NOT NULL DEFAULT 'basic',
    name                VARCHAR(24) NOT NULL,
    description         VARCHAR(255) DEFAULT NULL,
    login               VARCHAR(128) DEFAULT NULL,
    password_1          TEXT NOT NULL,
    password_2          TEXT DEFAULT NULL,
    url                 VARCHAR(255) DEFAULT NULL,
--    data        JSON NOT NULL, -- '{"name": "N26", "description": "Bank account", "login": "random01", "password": ["root"], "url": "https://app.n26.com/login"}'
    updated_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    created_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    CONSTRAINT fk_account
        FOREIGN KEY(f_owner)
            REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS tags (
    id                  UUID PRIMARY KEY NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    f_owner             UUID NOT NULL,
    name                VARCHAR(20) NOT NULL,
    color               VARCHAR(8) DEFAULT NULL,
    icon                VARCHAR(40) DEFAULT NULL,
    -- See to add icon in relational table maybe
    CONSTRAINT fk_account
        FOREIGN KEY(f_owner)
            REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS password_tag_linkers (
    id                  BIGINT GENERATED BY DEFAULT AS IDENTITY UNIQUE,
    f_password          UUID NOT NULL,
    f_tag               UUID NOT NULL,
    CONSTRAINT fk_password
        FOREIGN KEY(f_password)
            REFERENCES passwords(id),
    CONSTRAINT fk_tag
        FOREIGN KEY(f_tag)
            REFERENCES tags(id),
    CONSTRAINT unq_password_tag
        UNIQUE(f_password, f_tag)
);


CREATE TABLE IF NOT EXISTS auth_token_rsa (
    id                  INT GENERATED BY DEFAULT AS IDENTITY UNIQUE,
    type                TEXT NOT NULL UNIQUE,
    public_key          BYTEA NOT NULL,
    private_key         BYTEA NOT NULL,
    updated_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
    created_on          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);