-- Author : Estéban Ristich <esteban.ristich@protonmail.com>

SELECT 'CREATE DATABASE quarkey ENCODING ''UTF8'''
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quarkey')\gexec

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS accounts (
    id          TEXT PRIMARY KEY NOT NULL UNIQUE,
    firstname   TEXT NOT NULL,
    lastname    TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    public_key  BYTEA NOT NULL,
    private_key BYTEA NOT NULL,
    roles       TEXT NOT NULL,
    is_banned   BOOLEAN NOT NULL DEFAULT FALSE,
    updated_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS passwords (
    id          UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    login       TEXT DEFAULT NULL,
    password    TEXT NOT NULL,
    url         TEXT DEFAULT NULL,
    updated_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS tags (
    id          BIGSERIAL PRIMARY KEY NOT NULL,
    f_owner     TEXT NOT NULL,
    name        TEXT DEFAULT NULL,
    color       TEXT DEFAULT NULL,
    CONSTRAINT fk_account
        FOREIGN KEY(f_owner)
            REFERENCES accounts(id)
);


CREATE TABLE IF NOT EXISTS auth_token_rsa (
    id          SERIAL PRIMARY KEY NOT NULL,
    type        TEXT NOT NULL UNIQUE,
    public_key  BYTEA NOT NULL,
    private_key BYTEA NOT NULL,
    updated_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_on  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS linkers (
    id          BIGSERIAL PRIMARY KEY NOT NULL,
    f_owner     TEXT NOT NULL,
    f_item      UUID NOT NULL,
    f_tag       BIGINT DEFAULT NULL,
    CONSTRAINT fk_account
        FOREIGN KEY(f_owner)
            REFERENCES accounts(id),
    CONSTRAINT fk_password
        FOREIGN KEY(f_item)
            REFERENCES passwords(id),
    CONSTRAINT fk_tag
        FOREIGN KEY(f_tag)
            REFERENCES tags(id)
);